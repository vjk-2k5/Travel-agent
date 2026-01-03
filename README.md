# 🌍 AI Travel Agent - Workflow Orchestrator

A powerful terminal-based travel assistant that leverages LLM reasoning (Groq) and real-world APIs to automate travel planning. It searches live flights and hotels, generates detailed AI itineraries, and provides cost estimates through a conversational interface.

## ✨ Key Features

| Feature | Provider | Description |
|:---|:---|:---|
| ✈️ **Flight Search** | FlightAPI.io | Real-time pricing and schedules from 700+ airlines |
| 🏨 **Hotel Search** | SearchAPI.io | Live hotel data, ratings, and amenity filtering via Google Hotels |
| 🗺️ **Trip Planning** | Mistral/Groq | AI-generated day-by-day itineraries tailored to your style |
| 🏛️ **Sightseeing** | Mistral/Groq | Categorized top attractions, local food, and activities |
| 💰 **Cost Engine** | Custom | Detailed trip cost estimation with tax and fee breakdowns |
| 🎫 **Secure Booking** | Internal | Dry-run mode for safe booking previews and validation |

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
Copy `.env.example` to `.env` and add your keys:
```bash
cp .env.example .env
```

**Required:**
- `GROQ_API_KEY` - LLM orchestration via Groq [Required]
- `.env` file (copied from `.env.example`)

**Optional (for real-time data):**
- `FLIGHT_API` - [FlightAPI.io](https://www.flightapi.io)
- `SEARCH_API` - [SearchAPI.io](https://www.searchapi.io)
- `HUGGINGFACE_API_TOKEN` - [HuggingFace.co](https://huggingface.co)

### 3. Run the Agent
```bash
python main.py
```

## 💬 Example Queries

```
# Flight search
Find flights from Chennai to Singapore for 2 adults on 2025-02-01

# Hotel search  
Search hotels in Phuket for 4 adults, Jan 15-20, 2025

# Trip planning
Plan a 5 day trip to Bali with focus on beaches and food

# Attractions
What are the top attractions in Paris for history lovers?

# Cost estimation
Estimate total cost with flight ₹50000 and hotel ₹30000
```

## 📁 Project Structure

```
Travel-agent/
├── main.py                 # CLI entry point
├── src/
│   ├── agent.py           # LLM orchestrator (Groq)
│   ├── config.py          # Configuration
│   ├── schemas.py         # Function schemas for LLM
│   ├── api/
│   │   ├── flightapi.py   # FlightAPI.io client
│   │   └── searchapi.py   # SearchAPI.io client
│   ├── tools/
│   │   ├── flights.py     # Flight search & booking
│   │   ├── hotels.py      # Hotel search & booking
│   │   ├── planner.py     # AI trip planning (Mistral 7B)
│   │   └── pricing.py     # Cost estimation
│   └── utils/
│       ├── logger.py      # Audit logging
│       └── validators.py  # Input validation
├── logs/                   # Audit logs (JSONL)
├── requirements.txt
└── .env.example
```

## 🔧 CLI Options

```bash
# Interactive mode
python main.py

# Single query
python main.py --query "Find flights from Delhi to Dubai"

# Dry-run mode (no actual bookings)
python main.py --dry-run

# Disable colors
python main.py --no-color
```

## 🛡️ Features

- **Real-time data** - Live flight and hotel prices
- **AI trip planning** - Mistral 7B generates detailed itineraries
- **Audit logging** - Every action logged to `logs/audit.jsonl`
- **Dry-run mode** - Preview bookings without committing
- **Graceful fallback** - Uses mock data if APIs fail
- **Structured output** - JSON responses for easy integration

## 📊 API Data Sources

| API | Purpose | Free Tier |
|-----|---------|-----------|
| Groq | LLM orchestration | Yes |
| FlightAPI.io | Flight prices | 20 credits free |
| SearchAPI.io | Hotel search | 100 searches/month |
| Hugging Face | Trip planning | Free inference |

## 📝 License

MIT
