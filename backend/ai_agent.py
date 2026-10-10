from typing import Dict, List, Optional

from grok_service import chat_with_grok
from openrouter_service import (
    OPENROUTER_API_KEY,
    chat_with_openrouter_tools,
    get_general_support_response,
)


def is_general_support_question(message: str) -> bool:
    lower = message.lower()
    keywords = [
        "document",
        "passport",
        "visa",
        "cancel",
        "refund",
        "check-in",
    ]
    return any(keyword in lower for keyword in keywords)


def _get_data_source(data):
    if not isinstance(data, dict):
        return None

    if data.get("data_source"):
        return data["data_source"]

    flights = data.get("flights")
    if isinstance(flights, list) and flights:
        sources = {flight.get("data_source") for flight in flights if isinstance(flight, dict)}
        sources.discard(None)
        if len(sources) == 1:
            return sources.pop()

    return None


def process_user_message(message: str, history: Optional[List[Dict[str, str]]] = None):
    if not message or not str(message).strip():
        return {
            "response": "Please enter a valid message before sending.",
            "tool_used": None,
            "data": None,
        }

    clean_message = str(message).strip()
    clean_history = history or []

    if OPENROUTER_API_KEY and is_general_support_question(clean_message):
        try:
            return {
                "response": get_general_support_response(clean_message),
                "tool_used": "openrouter",
                "data": None,
                "provider": "OpenRouter",
                "data_source": None,
            }
        except Exception:
            pass

    try:
        result = chat_with_grok(clean_history, clean_message)
        data = result.get("data")
        return {
            "response": result.get("response") or "I could not generate a response.",
            "tool_used": result.get("tool_used"),
            "data": data,
            "provider": "Grok",
            "data_source": _get_data_source(data),
        }
    except RuntimeError as exc:
        try:
            result = chat_with_openrouter_tools(clean_history, clean_message)
            result["provider"] = "OpenRouter"
            result["data_source"] = _get_data_source(result.get("data"))
            return result
        except Exception as fallback_error:
            return {
                "response": (
                    f"Grok could not answer: {exc} "
                    f"OpenRouter fallback could not answer: {fallback_error}"
                ),
                "tool_used": None,
                "data": None,
            }
    except ValueError as exc:
        return {
            "response": f"Invalid request: {exc}",
            "tool_used": None,
            "data": None,
        }
    except Exception as exc:
        return {
            "response": f"Something went wrong while processing your request: {exc}",
            "tool_used": None,
            "data": None,
        }
