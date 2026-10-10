import os

import requests
from dotenv import load_dotenv

from airline_data import BAGGAGE_POLICIES, CITY_AIRPORT_CODES, FLIGHTS, normalize_text

load_dotenv()
AIRLABS_BASE_URL = "https://airlabs.co/api/v9"


def _find_flights(source, destination):
    source_norm = normalize_text(source)
    destination_norm = normalize_text(destination)

    if not source_norm or not destination_norm:
        raise ValueError("Source and destination are required.")

    matches = [
        flight
        for flight in FLIGHTS
        if normalize_text(flight["source"]) == source_norm
        and normalize_text(flight["destination"]) == destination_norm
    ]
    return matches


def search_flights(source, destination=None):
    source_norm = normalize_text(source)
    destination_norm = normalize_text(destination)

    if not source_norm:
        raise ValueError("A departure city is required.")

    api_key = os.getenv("AIRLABS_API_KEY", "").strip()
    source_code = CITY_AIRPORT_CODES.get(source_norm)
    destination_code = CITY_AIRPORT_CODES.get(destination_norm)
    if api_key and source_code and (not destination_norm or destination_code):
        try:
            params = {"api_key": api_key, "dep_iata": source_code, "limit": 50}
            if destination_code:
                params["arr_iata"] = destination_code
            response = requests.get(
                f"{AIRLABS_BASE_URL}/schedules", params=params, timeout=15
            )
            if response.status_code in {401, 403}:
                raise RuntimeError("AirLabs rejected AIRLABS_API_KEY.")
            if response.status_code == 429:
                raise RuntimeError("AirLabs monthly query limit has been reached.")
            if response.status_code != 200:
                raise RuntimeError(f"AirLabs request failed with HTTP {response.status_code}.")

            payload = response.json()
            live_flights = payload.get("response") or []
            if isinstance(live_flights, dict):
                live_flights = [live_flights]
            if isinstance(live_flights, list):
                total_count = len(live_flights)
                flights = [
                    {
                        "flight_number": flight.get("flight_iata")
                        or flight.get("flight_number")
                        or "Unknown",
                        "airline": flight.get("airline_iata") or "Unknown airline",
                        "source": flight.get("dep_iata") or source_code,
                        "destination": flight.get("arr_iata") or "Unknown",
                        "price": None,
                        "departure": flight.get("dep_estimated")
                        or flight.get("dep_time")
                        or "Unavailable",
                        "arrival": flight.get("arr_estimated")
                        or flight.get("arr_time")
                        or "Unavailable",
                        "status": flight.get("status") or "Status unavailable",
                    }
                    for flight in live_flights
                    if isinstance(flight, dict)
                ][:50]
                result_note = (
                    f"showing 50 of {total_count} records"
                    if total_count > 50
                    else f"found {len(flights)} flight(s)"
                )
                return {
                    "message": f"AirLabs schedules cover departures up to 10 hours ahead; {result_note}.",
                    "count": len(flights),
                    "data_source": "AirLabs live schedules",
                    "flights": flights,
                }
        except (requests.RequestException, ValueError, TypeError, RuntimeError):
            pass

    flights = [
        flight
        for flight in FLIGHTS
        if normalize_text(flight["source"]) == source_norm
        and (not destination_norm or normalize_text(flight["destination"]) == destination_norm)
    ]

    if not flights:
        route = f" from {source}" + (f" to {destination}" if destination_norm else "")
        return {
            "message": f"No sample flights found{route}.",
            "count": 0,
            "data_source": "sample_data",
            "flights": [],
        }

    return {
        "message": f"Found {len(flights)} sample flight(s) from {source}"
        + (f" to {destination}." if destination_norm else ". Destination not filtered."),
        "count": len(flights),
        "data_source": "sample_data",
        "flights": [
            {
                "flight_number": flight["flight_number"],
                "airline": flight["airline"],
                "source": flight["source"],
                "destination": flight["destination"],
                "price": flight["price"],
                "departure": flight["departure"],
                "arrival": flight["arrival"],
                "status": flight["status"],
            }
            for flight in flights
        ],
    }


def get_flight_price(source, destination):
    flights = _find_flights(source, destination)

    if not flights:
        raise ValueError(f"No flight found from {source} to {destination}.")

    chosen = flights[0]
    return {
        "flight": chosen["flight_number"],
        "airline": chosen["airline"],
        "source": chosen["source"],
        "destination": chosen["destination"],
        "price": chosen["price"],
        "data_source": "sample_data",
        "departure": chosen["departure"],
        "arrival": chosen["arrival"],
        "status": chosen["status"],
    }


def get_flight_status(flight_number):
    if not flight_number or not str(flight_number).strip():
        raise ValueError("Flight number is required.")

    api_key = os.getenv("AIRLABS_API_KEY", "").strip()
    if api_key:
        try:
            response = requests.get(
                f"{AIRLABS_BASE_URL}/flight",
                params={"api_key": api_key, "flight_iata": str(flight_number).strip().upper()},
                timeout=15,
            )
            if response.status_code in {401, 403}:
                raise RuntimeError("AirLabs rejected AIRLABS_API_KEY. Check the key in backend/.env.")
            if response.status_code == 429:
                raise RuntimeError("AirLabs monthly query limit has been reached.")
            if response.status_code != 200:
                raise RuntimeError(f"AirLabs request failed with HTTP {response.status_code}.")

            payload = response.json()
            live_flight = payload.get("response")
            if isinstance(live_flight, list):
                live_flight = live_flight[0] if live_flight else None

            if isinstance(live_flight, dict):
                matching_sample = next(
                    (
                        item
                        for item in FLIGHTS
                        if normalize_text(item["flight_number"])
                        == normalize_text(flight_number)
                    ),
                    {},
                )
                return {
                    "flight_number": live_flight.get("flight_iata")
                    or live_flight.get("flight_number")
                    or str(flight_number).strip().upper(),
                    "airline": matching_sample.get("airline")
                    or live_flight.get("airline_iata")
                    or "Unknown airline",
                    "source": live_flight.get("dep_iata")
                    or live_flight.get("dep_icao")
                    or "Unknown",
                    "destination": live_flight.get("arr_iata")
                    or live_flight.get("arr_icao")
                    or "Unknown",
                    "status": live_flight.get("status") or "Status unavailable",
                    "departure": live_flight.get("dep_estimated")
                    or live_flight.get("dep_time")
                    or "Unavailable",
                    "arrival": live_flight.get("arr_estimated")
                    or live_flight.get("arr_time")
                    or "Unavailable",
                    "data_source": "AirLabs live data",
                }
        except RuntimeError as exc:
            live_lookup_note = f"{exc} Showing sample data instead."
        except requests.RequestException as exc:
            live_lookup_note = "AirLabs could not be reached; showing sample data."
        except (ValueError, TypeError):
            live_lookup_note = "AirLabs returned an unreadable response; showing sample data."
        else:
            live_lookup_note = "AirLabs has no live result for this flight; showing sample data."
    else:
        live_lookup_note = "AIRLABS_API_KEY is not configured; showing sample data."

    flight = next(
        (
            item
            for item in FLIGHTS
            if normalize_text(item["flight_number"]) == normalize_text(flight_number)
        ),
        None,
    )

    if not flight:
        if api_key:
            raise ValueError(f"No live or sample result found for flight {flight_number}.")
        raise ValueError(f"Flight {flight_number} not found in sample data. Configure AIRLABS_API_KEY for live status.")

    return {
        "flight_number": flight["flight_number"],
        "airline": flight["airline"],
        "source": flight["source"],
        "destination": flight["destination"],
        "status": flight["status"],
        "departure": flight["departure"],
        "arrival": flight["arrival"],
        "data_source": f"sample_data: {live_lookup_note}",
    }


def get_baggage_policy(airline):
    if not airline or not str(airline).strip():
        raise ValueError("Airline name is required.")

    key = normalize_text(airline)
    policy = BAGGAGE_POLICIES.get(key)

    if not policy:
        return {
            "airline": airline,
            "message": f"No baggage policy found for {airline}. Please contact the airline directly.",
        }

    return {
        "airline": airline,
        "carry_on": policy["carry_on"],
        "checked_in": policy["checked_in"],
        "extra_baggage": policy["extra_baggage"],
    }
