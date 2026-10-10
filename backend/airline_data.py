FLIGHTS = [
    {
        "flight_number": "AI202",
        "airline": "Air India",
        "source": "Delhi",
        "destination": "Paris",
        "price": 45000,
        "departure": "10:30 AM",
        "arrival": "06:20 PM",
        "status": "Scheduled",
    },
    {
        "flight_number": "AI204",
        "airline": "Air India",
        "source": "Delhi",
        "destination": "Paris",
        "price": 49000,
        "departure": "08:15 PM",
        "arrival": "04:25 AM",
        "status": "Scheduled",
    },
    {
        "flight_number": "EK508",
        "airline": "Emirates",
        "source": "Delhi",
        "destination": "Dubai",
        "price": 32000,
        "departure": "11:45 AM",
        "arrival": "01:50 PM",
        "status": "On Time",
    },
    {
        "flight_number": "BA117",
        "airline": "British Airways",
        "source": "Delhi",
        "destination": "London",
        "price": 61000,
        "departure": "09:10 PM",
        "arrival": "11:55 AM",
        "status": "Delayed by 30 min",
    },
    {
        "flight_number": "AI312",
        "airline": "Air India",
        "source": "Mumbai",
        "destination": "London",
        "price": 54000,
        "departure": "07:00 AM",
        "arrival": "09:50 AM",
        "status": "Scheduled",
    },
    {
        "flight_number": "6E230",
        "airline": "IndiGo",
        "source": "Lucknow",
        "destination": "Delhi",
        "price": 6800,
        "departure": "06:20 AM",
        "arrival": "07:45 AM",
        "status": "Scheduled",
    },
    {
        "flight_number": "DL201",
        "airline": "Delta Air Lines",
        "source": "Delhi",
        "destination": "New York",
        "price": 75000,
        "departure": "10:00 PM",
        "arrival": "07:30 AM",
        "status": "Scheduled",
    },
]

BAGGAGE_POLICIES = {
    "air india": {
        "carry_on": "7 kg",
        "checked_in": "25 kg",
        "extra_baggage": "₹1,500 per extra kg",
    },
    "emirates": {
        "carry_on": "7 kg",
        "checked_in": "30 kg",
        "extra_baggage": "₹1,800 per extra kg",
    },
    "british airways": {
        "carry_on": "10 kg",
        "checked_in": "23 kg",
        "extra_baggage": "₹1,400 per extra kg",
    },
    "indigo": {
        "carry_on": "7 kg",
        "checked_in": "15 kg",
        "extra_baggage": "₹1,200 per extra kg",
    },
    "delta air lines": {
        "carry_on": "10 kg",
        "checked_in": "23 kg",
        "extra_baggage": "₹1,700 per extra kg",
    },
}

CITY_AIRPORT_CODES = {
    "delhi": "DEL",
    "dubai": "DXB",
    "london": "LHR",
    "lucknow": "LKO",
    "mumbai": "BOM",
    "paris": "CDG",
}


def normalize_text(value):
    return (value or "").strip().lower()
