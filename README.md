# AI-Powered Airline Customer Support Agent

A small React + FastAPI chatbot that uses Grok function calling for sample airline data and OpenRouter for selected general travel questions. Flight data is local and demonstrative; it is not live airline inventory.

## Requirements

- Python 3.10 or newer
- Node.js 18 or newer
- Grok and/or OpenRouter API key for AI responses

## Configure API keys

From the `backend` directory, copy `.env.example` to `.env` and set the keys there:

```env
GROK_API_KEY=your_grok_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
AIRLABS_API_KEY=your_airlabs_api_key
```

Keys remain in the Python backend and must not be added to frontend files. The `.env` file is ignored by Git.
AirLabs is used for live flight status when configured. Flight searches and prices still use local sample data; AirLabs does not provide ticket-price quotes through this integration. Its free plan has a monthly query limit and personal-use restrictions, so check its current plan terms.

## Run the backend

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

The API runs at `http://localhost:8000`; interactive API documentation is at `http://localhost:8000/docs`.

## Run the frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Vite prints the local frontend URL (normally `http://localhost:5173`).

## Example questions

1. Find flights from Delhi to Paris.
2. What's the price of a flight from Delhi to Paris?
3. Check flight AI202.
4. What is the baggage allowance for Air India?
5. What documents do I need for international travel?

Flight status uses AirLabs when `AIRLABS_API_KEY` is configured; otherwise, matching sample flights are returned with a sample-data label. Flight searches and prices use local sample data. Selected general questions can use OpenRouter when its key is configured.
