"""
Travel Agent - CLI Entry Point
Interactive command-line interface for the travel agent.
"""

import argparse
import json
import sys
import os

from src.config import load_config, Config
from src.agent import create_agent


# ANSI color codes for terminal styling
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'


def print_colored(text: str, color: str = Colors.WHITE):
    """Print text with color."""
    print(f"{color}{text}{Colors.RESET}")


def print_header():
    """Print the application header."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print()
    print_colored("╔══════════════════════════════════════════════════════════════╗", Colors.CYAN)
    print_colored("║                                                              ║", Colors.CYAN)
    print_colored("║   ✈️   TRAVEL AGENT - AI Workflow Orchestrator   🏨          ║", Colors.CYAN + Colors.BOLD)
    print_colored("║                                                              ║", Colors.CYAN)
    print_colored("╚══════════════════════════════════════════════════════════════╝", Colors.CYAN)
    print()


def print_capabilities():
    """Print agent capabilities."""
    print_colored("  What I can do for you:", Colors.WHITE + Colors.BOLD)
    print()
    capabilities = [
        ("✈️ ", "Search flights", "between any airports worldwide"),
        ("🏨", "Find hotels", "in cities and near landmarks"),
        ("🗺️ ", "Plan your trip", "AI-powered itinerary with places to visit"),
        ("🏛️ ", "Discover attractions", "top sights, food, activities by category"),
        ("💰", "Estimate costs", "with detailed breakdowns"),
        ("🎫", "Book trips", "with safe dry-run preview"),
    ]
    for emoji, title, desc in capabilities:
        print(f"    {emoji}  {Colors.GREEN}{title}{Colors.RESET} {Colors.DIM}- {desc}{Colors.RESET}")
    print()


def print_help():
    """Print help commands."""
    print_colored("─" * 64, Colors.DIM)
    print(f"  {Colors.DIM}Commands:{Colors.RESET}  {Colors.YELLOW}quit{Colors.RESET}/{Colors.YELLOW}exit{Colors.RESET} to end  •  {Colors.YELLOW}reset{Colors.RESET} for new conversation  •  {Colors.YELLOW}help{Colors.RESET} for tips")
    print_colored("─" * 64, Colors.DIM)
    print()


def print_tips():
    """Print usage tips."""
    print()
    print_colored("  💡 Tips for better results:", Colors.YELLOW + Colors.BOLD)
    print()
    tips = [
        "Use airport codes: MAA (Chennai), SIN (Singapore), DXB (Dubai)",
        "Specify dates: 2025-01-15 (YYYY-MM-DD format)",
        "Include passenger count: '2 adults'",
        "Mention preferences: 'economy class', 'near Marina Bay'",
    ]
    for tip in tips:
        print(f"    {Colors.DIM}•{Colors.RESET} {tip}")
    print()
    print_colored("  Example queries:", Colors.CYAN + Colors.BOLD)
    print(f"    {Colors.DIM}→{Colors.RESET} Find flights from Chennai to Singapore for 2 adults on 2025-02-01")
    print(f"    {Colors.DIM}→{Colors.RESET} Search hotels near Marina Bay, Singapore, Feb 1-5, 2025")
    print(f"    {Colors.DIM}→{Colors.RESET} {Colors.YELLOW}Plan a 5 day trip to Bali with focus on beaches and food{Colors.RESET}")
    print(f"    {Colors.DIM}→{Colors.RESET} {Colors.YELLOW}What are the top attractions in Paris?{Colors.RESET}")
    print()


def format_json_output(data: dict) -> str:
    """Format JSON output with colors."""
    formatted = json.dumps(data, indent=2, ensure_ascii=False)
    
    # Add some color highlighting for keys
    lines = formatted.split('\n')
    colored_lines = []
    for line in lines:
        if '":' in line:
            # Color the key
            parts = line.split('":')
            key_part = parts[0].replace('"', f'{Colors.CYAN}"') + f'"{Colors.RESET}:'
            value_part = '":'.join(parts[1:])
            
            # Color values based on type
            if 'true' in value_part:
                value_part = value_part.replace('true', f'{Colors.GREEN}true{Colors.RESET}')
            elif 'false' in value_part:
                value_part = value_part.replace('false', f'{Colors.RED}false{Colors.RESET}')
            elif 'null' in value_part:
                value_part = value_part.replace('null', f'{Colors.DIM}null{Colors.RESET}')
            
            colored_lines.append(key_part + value_part)
        else:
            colored_lines.append(line)
    
    return '\n'.join(colored_lines)


def print_response(data: dict):
    """Print the agent response in a structured way."""
    print()
    
    success = data.get("success", False)
    
    if success:
        print_colored("  ✅ Response:", Colors.GREEN + Colors.BOLD)
    else:
        print_colored("  ❌ Error:", Colors.RED + Colors.BOLD)
    
    print_colored("  " + "─" * 60, Colors.DIM)
    
    # Check if there's a text message
    if "message" in data and data["message"]:
        print()
        message = data["message"]
        # Wrap long messages
        for line in message.split('\n'):
            print(f"  {line}")
        print()
    
    # Check if there are tool results
    tool_results = data.get("tool_results", [])
    if tool_results:
        print_colored(f"  📊 Function calls: {len(tool_results)}", Colors.YELLOW)
        for i, tr in enumerate(tool_results, 1):
            func_name = tr.get("function", "unknown")
            print(f"      {Colors.DIM}{i}.{Colors.RESET} {Colors.CYAN}{func_name}(){Colors.RESET}")
    
    # Check for error
    if "error" in data and data["error"]:
        print()
        print_colored(f"  Error: {data['error']}", Colors.RED)
    
    # If the response has actual data (flights, hotels, etc.), show summary
    for tr in tool_results:
        result = tr.get("result", {})
        if "flights" in result:
            flights = result["flights"]
            print()
            print_colored(f"  ✈️  Found {len(flights)} flight options:", Colors.GREEN)
            for i, f in enumerate(flights[:3], 1):  # Show top 3
                airline = f.get("airline", {}).get("name", "Unknown")
                price = f.get("price", {}).get("total", 0)
                currency = f.get("price", {}).get("currency", "INR")
                print(f"      {i}. {airline} - {currency} {price:,}")
            if len(flights) > 3:
                print(f"      {Colors.DIM}... and {len(flights) - 3} more{Colors.RESET}")
        
        if "hotels" in result:
            hotels = result["hotels"]
            print()
            print_colored(f"  🏨 Found {len(hotels)} hotel options:", Colors.GREEN)
            for i, h in enumerate(hotels[:3], 1):  # Show top 3
                name = h.get("name", "Unknown")
                price = h.get("price", {}).get("total_from", 0) or h.get("price", {}).get("total", 0)
                # Handle price as string, float, or int
                if isinstance(price, str):
                    price = float(price.replace(",", "").replace("$", "")) if price else 0
                price = int(price) if price else 0
                currency = h.get("price", {}).get("currency", "USD")
                # Rating might be float like 4.1, convert to int for stars
                rating_val = h.get("rating", 0) or h.get("hotel_class", 0)
                rating = "⭐" * int(rating_val) if rating_val else ""
                print(f"      {i}. {name} {rating} - {currency} {price:,}")
            if len(hotels) > 3:
                print(f"      {Colors.DIM}... and {len(hotels) - 3} more{Colors.RESET}")
        
        # Show itinerary from destination planner
        if "itinerary" in result:
            print()
            print_colored("  🗺️  Trip Itinerary (AI-Generated):", Colors.GREEN + Colors.BOLD)
            print()
            itinerary = result.get("itinerary", "")
            # Print itinerary with proper formatting
            for line in itinerary.split('\n')[:30]:  # Limit to 30 lines
                print(f"  {line}")
            if itinerary.count('\n') > 30:
                print(f"  {Colors.DIM}... (truncated){Colors.RESET}")
        
        # Show attractions
        if "attractions" in result:
            print()
            print_colored("  🏛️  Top Attractions:", Colors.GREEN + Colors.BOLD)
            print()
            attractions = result.get("attractions", "")
            for line in attractions.split('\n')[:20]:  # Limit to 20 lines
                print(f"  {line}")
    
    # After showing flight/hotel results, suggest planning
    has_destination = False
    destination = None
    for tr in tool_results:
        func = tr.get("function", "")
        if func in ["search_flights", "search_hotels"]:
            result = tr.get("result", {})
            # Try to extract destination
            if "query" in result:
                destination = result["query"].get("destination") or result["query"].get("city_code")
                if destination:
                    has_destination = True
    
    if has_destination and destination:
        print()
        print(f"  {Colors.YELLOW}💡 Tip:{Colors.RESET} Want to know what to do in {Colors.CYAN}{destination}{Colors.RESET}?")
        print(f"     Try: {Colors.DIM}'Plan a trip to {destination}' or 'Top attractions in {destination}'{Colors.RESET}")
    
    print()
    print_colored("  " + "─" * 60, Colors.DIM)
    print()


def interactive_mode(agent, dry_run: bool = False):
    """Run the agent in interactive mode."""
    print_header()
    print_capabilities()
    print_help()
    
    if dry_run:
        print_colored("  🔒 DRY-RUN MODE: Bookings will be simulated only", Colors.YELLOW)
        print()
    
    while True:
        try:
            # User prompt
            print(f"  {Colors.GREEN}You:{Colors.RESET} ", end="")
            user_input = input().strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["quit", "exit", "q"]:
                print()
                print_colored("  👋 Goodbye! Safe travels!", Colors.CYAN)
                print()
                break
            
            if user_input.lower() == "reset":
                agent.reset_conversation()
                print()
                print_colored("  🔄 Conversation reset. Starting fresh!", Colors.YELLOW)
                print()
                continue
            
            if user_input.lower() == "help":
                print_tips()
                continue
            
            # Processing indicator
            print()
            print(f"  {Colors.DIM}⏳ Processing your request...{Colors.RESET}")
            
            result = agent.process_request(user_input)
            print_response(result)
            
        except KeyboardInterrupt:
            print()
            print()
            print_colored("  👋 Session interrupted. Goodbye!", Colors.CYAN)
            print()
            break
        except Exception as e:
            print()
            print_colored(f"  ❌ Unexpected error: {e}", Colors.RED)
            print()


def single_query_mode(agent, query: str):
    """Process a single query and exit."""
    print()
    print_colored("  📝 Query:", Colors.CYAN)
    print(f"  {query}")
    print()
    print(f"  {Colors.DIM}⏳ Processing...{Colors.RESET}")
    
    result = agent.process_request(query)
    print_response(result)
    
    return 0 if result.get("success", False) else 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Travel Agent - LLM-powered travel workflow automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
      Start interactive mode
  
  python main.py --query "Find flights from Chennai to Singapore for 2 adults"
      Process a single query
  
  python main.py --dry-run --query "Book a flight..."
      Process with dry-run mode (no actual bookings)
        """
    )
    
    parser.add_argument(
        "--query", "-q",
        type=str,
        help="Single query to process (non-interactive mode)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Enable dry-run mode (bookings will be simulated)"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Groq model to use (default: from GROQ_MODEL_ID in .env)"
    )
    
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output"
    )
    
    args = parser.parse_args()
    
    # Disable colors if requested or not supported
    if args.no_color or not sys.stdout.isatty():
        Colors.HEADER = ''
        Colors.BLUE = ''
        Colors.CYAN = ''
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.RED = ''
        Colors.WHITE = ''
        Colors.BOLD = ''
        Colors.DIM = ''
        Colors.RESET = ''
    
    # Load configuration
    try:
        config = load_config()
    except ValueError as e:
        print()
        print_colored(f"  ❌ Configuration Error: {e}", Colors.RED)
        print()
        print_colored("  Please set your GROQ_API_KEY in .env file or environment variable.", Colors.YELLOW)
        print_colored("  Get your free API key at: https://console.groq.com", Colors.CYAN)
        print()
        sys.exit(1)
    
    # Override config with CLI arguments
    if args.dry_run:
        config.dry_run_mode = True
    if args.model:
        config.model_name = args.model
    
    # Create agent
    agent = create_agent(config)
    
    # Run in appropriate mode
    if args.query:
        if config.dry_run_mode:
            print_colored("\n  🔒 DRY-RUN MODE ENABLED", Colors.YELLOW)
        sys.exit(single_query_mode(agent, args.query))
    else:
        interactive_mode(agent, config.dry_run_mode)


if __name__ == "__main__":
    main()
