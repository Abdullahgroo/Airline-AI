import json
import os
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv

load_dotenv()

GROK_API_KEY = os.getenv("GROK_API_KEY", "")
GROK_BASE_URL = "https://api.x.ai/v1"
TOOL_ARGUMENTS = {
    "search_flights": {"source", "destination"},
    "get_flight_price": {"source", "destination"},
    "get_flight_status": {"flight_number"},
    "get_baggage_policy": {"airline"},
}


def build_system_prompt():
    return '''
You are Airline AI Support Agent. Use airline tools only when needed.

Rules:
- If the user asks about flights, prices, schedules, or baggage, use the available airline tools.
- Do not invent flight numbers, prices, or baggage policies.
- If a user asks for flights "from" a city without naming a destination, search departures from that city; do not require or invent a destination.
- AirLabs live schedules cover up to 10 hours ahead. Flight prices still come from sample data. If a tool result says sample_data, clearly tell the user it is not live.
- If the user asks general travel questions, answer without needing a tool.
- If asked how to improve you or this service, answer specifically about this airline support app. Suggest practical next improvements such as more verified flight data, travel-date support, clearer policy sources, or a response feedback button. Do not imply these features already exist.
- Be concise, clear, and helpful.
- Always respect the country and airline context when answering.
- If a tool call is needed, return valid function call arguments.
'''.strip()


def get_tools_definition():
    return [
        {
            "type": "function",
            "function": {
                "name": "search_flights",
                "description": "Search flights departing from a city, optionally filtered by destination. If destination is omitted, return departures from the source city.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string"},
                        "destination": {"type": "string"},
                    },
                    "required": ["source"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_flight_price",
                "description": "Get the price of a flight between a source and destination city.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string"},
                        "destination": {"type": "string"},
                    },
                    "required": ["source", "destination"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_flight_status",
                "description": "Get flight status by flight number. Uses AirLabs live flight data when configured, otherwise returns clearly labeled local sample data.",
                "parameters": {
                    "type": "object",
                    "properties": {"flight_number": {"type": "string"}},
                    "required": ["flight_number"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_baggage_policy",
                "description": "Get baggage policy information for an airline.",
                "parameters": {
                    "type": "object",
                    "properties": {"airline": {"type": "string"}},
                    "required": ["airline"],
                },
            },
        },
    ]


def call_grok(
    messages: List[Dict[str, Any]],
    tools: List[Dict[str, Any]] | None = None,
    tool_choice: str = "auto",
):
    if not GROK_API_KEY:
        raise RuntimeError("GROK_API_KEY is missing.")

    payload = {
        "model": "grok-3-mini",
        "messages": messages,
        "tools": tools or get_tools_definition(),
        "tool_choice": tool_choice,
        "temperature": 0.2,
    }

    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"{GROK_BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        timeout=60,
    )

    if response.status_code != 200:
        if response.status_code == 401:
            raise RuntimeError(
                "xAI rejected GROK_API_KEY. Replace it with a valid key from https://console.x.ai and restart the backend."
            )
        try:
            provider_error = response.json().get("error", {})
            error_text = (
                provider_error.get("message", "")
                if isinstance(provider_error, dict)
                else str(provider_error)
            )
        except (ValueError, AttributeError):
            error_text = ""
        error_text = error_text or "Provider rejected the request."
        raise RuntimeError(f"Grok API request failed: {error_text}")

    data = response.json()
    if not data.get("choices"):
        raise RuntimeError("Grok returned no choices.")

    return data["choices"][0]["message"]


def prepare_messages(history: List[Dict[str, Any]], user_message: str):
    messages = [{"role": "system", "content": build_system_prompt()}]

    for item in history:
        if item.get("role") in {"user", "assistant"} and isinstance(
            item.get("content"), str
        ):
            messages.append({"role": item["role"], "content": item["content"]})

    messages.append({"role": "user", "content": user_message})
    return messages


def execute_tool_call(tool_name: str, arguments: Dict[str, Any]):
    from airline_tools import (
        get_baggage_policy,
        get_flight_price,
        get_flight_status,
        search_flights,
    )

    tool_map = {
        "search_flights": search_flights,
        "get_flight_price": get_flight_price,
        "get_flight_status": get_flight_status,
        "get_baggage_policy": get_baggage_policy,
    }

    if tool_name not in tool_map:
        raise ValueError(f"Unsupported tool: {tool_name}")

    required_arguments = TOOL_ARGUMENTS[tool_name]
    allowed_arguments = required_arguments
    if tool_name == "search_flights":
        required_arguments = {"source"}
    if (
        not isinstance(arguments, dict)
        or not required_arguments.issubset(arguments)
        or not set(arguments).issubset(allowed_arguments)
    ):
        expected = ", ".join(sorted(required_arguments))
        raise ValueError(f"Invalid arguments for {tool_name}; required: {expected}.")

    if any(
        value is not None and (not isinstance(value, str) or not value.strip())
        for value in arguments.values()
    ):
        if tool_name != "search_flights" or any(
            key != "destination" for key, value in arguments.items() if not value
        ):
            raise ValueError(f"Arguments for {tool_name} must be non-empty strings.")

    if tool_name == "search_flights" and not arguments.get("destination"):
        arguments["destination"] = None

    return tool_map[tool_name](**arguments)


def generate_final_answer(messages: List[Dict[str, Any]]):
    response_message = call_grok(messages, tools=get_tools_definition())
    return response_message


def chat_with_grok(history: List[Dict[str, Any]], user_message: str):
    messages = prepare_messages(history, user_message)
    initial_response = call_grok(messages, tools=get_tools_definition())

    tool_calls = initial_response.get("tool_calls") or []
    if not tool_calls:
        return {
            "response": initial_response.get("content") or "I couldn't generate a response.",
            "tool_used": None,
            "data": None,
        }

    tool_call = tool_calls[0]
    tool_name = tool_call["function"]["name"]
    try:
        arguments = json.loads(tool_call["function"]["arguments"])
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Grok returned invalid tool arguments.") from exc

    tool_result = execute_tool_call(tool_name, arguments)

    tool_message = {
        "role": "tool",
        "tool_call_id": tool_call["id"],
        "name": tool_name,
        "content": json.dumps(tool_result),
    }

    conversation = messages + [
        {
            "role": "assistant",
            "content": "",
            "tool_calls": initial_response["tool_calls"],
        },
        tool_message,
    ]

    final_response = call_grok(
        conversation, tools=get_tools_definition(), tool_choice="none"
    )
    final_text = final_response.get("content") or "I couldn't generate a final answer."

    return {
        "response": final_text,
        "tool_used": tool_name,
        "data": tool_result,
    }
