# 🌍 Travel Agent - AI Workflow Orchestrator

An LLM-powered travel agent that searches **real flights and hotels**, plans itineraries, and estimates costs using function calling.

## ✨ Features

| Feature | API Source | Description |
|---------|------------|-------------|
| ✈️ Flight Search | FlightAPI.io | Real-time prices from 700+ airlines |
| 🏨 Hotel Search | SearchAPI.io | Google Hotels data with ratings & amenities |
| 🗺️ Trip Planning | Mistral 7B | AI-powered day-by-day itineraries |
| 🏛️ Attractions | Mistral 7B | Top sights, food, activities by category |
| 💰 Cost Estimation | Built-in | Detailed trip cost breakdowns |
| 🎫 Booking Preview | Built-in | Dry-run mode for safe previews |

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
- `GROQ_API_KEY` - Get from [console.groq.com](https://console.groq.com)

**Optional (for real data):**
- `FLIGHT_API` - Get from [flightapi.io](https://www.flightapi.io)
- `SEARCH_API` - Get from [searchapi.io](https://www.searchapi.io)
- `HUGGINGFACE_API_TOKEN` - Get from [huggingface.co](https://huggingface.co)

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
