import os
import json

import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def get_general_support_response(question: str):
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is missing.")

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant for a simple airline customer-support app. Provide brief, practical travel guidance without inventing policies, prices, or features. If asked how to improve you or this service, suggest relevant next steps such as more verified flight data, travel-date support, clearer policy sources, or a response feedback button; do not claim these already exist.",
            },
            {"role": "user", "content": question},
        ],
        "temperature": 0.3,
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5173",
        "X-Title": "Airline AI Agent",
    }

    response = requests.post(
        f"{OPENROUTER_BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        timeout=60,
    )

    if response.status_code != 200:
        if response.status_code == 401:
            raise RuntimeError(
                "OpenRouter rejected OPENROUTER_API_KEY. Replace it with a valid key from https://openrouter.ai/settings/keys."
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
        error_text = error_text or f"HTTP {response.status_code}"
        raise RuntimeError(f"OpenRouter API request failed: {error_text}")

    data = response.json()
    if not data.get("choices"):
        raise RuntimeError("OpenRouter returned no choices.")

    message = data["choices"][0]["message"]
    return message.get("content") or "I am unable to answer that question right now."


def chat_with_openrouter_tools(history, user_message):
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is missing.")

    from grok_service import execute_tool_call, get_tools_definition, prepare_messages

    messages = prepare_messages(history, user_message)
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5173",
        "X-Title": "Airline AI Agent",
    }
    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": messages,
        "tools": get_tools_definition(),
        "tool_choice": "auto",
        "temperature": 0.2,
    }
    response = requests.post(
        f"{OPENROUTER_BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        timeout=60,
    )

    if response.status_code == 401:
        raise RuntimeError(
            "OpenRouter rejected OPENROUTER_API_KEY. Replace it with a valid key from https://openrouter.ai/settings/keys."
        )
    if response.status_code != 200:
        try:
            provider_error = response.json().get("error", {})
            error_text = (
                provider_error.get("message", "")
                if isinstance(provider_error, dict)
                else str(provider_error)
            )
        except (ValueError, AttributeError):
            error_text = ""
        raise RuntimeError(
            f"OpenRouter API request failed: {error_text or f'HTTP {response.status_code}'}"
        )

    choices = response.json().get("choices", [])
    if not choices:
        raise RuntimeError("OpenRouter returned no choices.")

    assistant_message = choices[0]["message"]
    tool_calls = assistant_message.get("tool_calls") or []
    if not tool_calls:
        return {
            "response": assistant_message.get("content") or "I could not generate a response.",
            "tool_used": None,
            "data": None,
        }

    tool_call = tool_calls[0]
    tool_name = tool_call["function"]["name"]
    try:
        arguments = json.loads(tool_call["function"]["arguments"])
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("OpenRouter returned invalid tool arguments.") from exc

    tool_result = execute_tool_call(tool_name, arguments)
    messages.extend(
        [
            assistant_message,
            {
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "name": tool_name,
                "content": json.dumps(tool_result),
            },
        ]
    )
    payload.update({"messages": messages, "tool_choice": "none"})
    final_response = requests.post(
        f"{OPENROUTER_BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        timeout=60,
    )

    if final_response.status_code != 200:
        raise RuntimeError(
            f"OpenRouter final response failed: HTTP {final_response.status_code}"
        )
    final_choices = final_response.json().get("choices", [])
    if not final_choices:
        raise RuntimeError("OpenRouter returned no final response.")

    return {
        "response": final_choices[0]["message"].get("content")
        or "I could not generate a final answer.",
        "tool_used": tool_name,
        "data": tool_result,
    }
