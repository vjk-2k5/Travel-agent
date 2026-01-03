"""
Travel Agent - LLM Orchestrator using Groq API.
Interprets natural language requests and executes travel functions.
"""

import json
from typing import Any, Callable

from groq import Groq

from .config import Config
from .schemas import get_tool_schemas
from .tools import (
    search_flights,
    get_flight_pricing,
    book_flight,
    search_hotels,
    check_hotel_availability,
    book_hotel,
    estimate_total_cost,
    plan_destination,
    get_attractions
)
from .utils.logger import AuditLogger, get_logger


# System prompt for the travel agent
SYSTEM_PROMPT = """You are a Travel Workflow Orchestrator Agent.

YOUR ROLE:
1. Parse user intent from natural language travel requests
2. Call the appropriate travel functions with validated parameters
3. Return results from function calls

CRITICAL RULES:
- You can ONLY call these functions: search_flights, get_flight_pricing, search_hotels, check_hotel_availability, estimate_total_cost, book_flight, book_hotel, plan_destination, get_attractions
- Do NOT attempt to call any other functions or tools (no "json" tool exists)
- If you need to ask for clarification, just respond with a plain text message - do NOT use function calls for clarifications
- All dates must be in YYYY-MM-DD format
- Airport codes must be 3-letter IATA codes (e.g., MAA for Chennai, SIN for Singapore)
- For bookings, always use dry_run=true unless user explicitly confirms booking

FUNCTION REFERENCE:
- search_flights(origin, destination, departure_date, adults, return_date?, cabin_class?)
- get_flight_pricing(flight_offer_id, currency?)
- search_hotels(check_in, check_out, adults, city_code?, location?, rooms?, amenities?)
- check_hotel_availability(hotel_id, check_in, check_out, rooms?)
- estimate_total_cost(flight_price, hotel_price, currency, include_taxes?, additional_costs?)
- book_flight(flight_offer_id, passengers, dry_run?)
- book_hotel(hotel_offer_id, guests, payment_info?, dry_run?)
- plan_destination(destination, days?, interests?, travel_style?, budget?) - AI-powered itinerary planning
- get_attractions(destination, category?, limit?) - Get top attractions for a destination

For any invalid or unambigious query , let the user know or ask clarification 
ex:I need to go to delhi via fox (here what is fox)(ask user for clarification in these kinda cases)

When you have results from functions, summarize them clearly. If you need more information from the user, ask in plain text."""


class TravelAgent:
    """
    LLM-based travel agent using Groq for function calling.
    Orchestrates travel workflows through tool execution.
    """
    
    def __init__(self, config: Config):
        """Initialize the agent with configuration."""
        self.config = config
        self.groq_client = Groq(api_key=config.groq_api_key)
        self.logger = get_logger(config.log_file)
        self.tools = get_tool_schemas()
        
        # Map function names to actual implementations
        self.function_map: dict[str, Callable] = {
            "search_flights": search_flights,
            "get_flight_pricing": get_flight_pricing,
            "book_flight": self._book_flight_with_dry_run,
            "search_hotels": search_hotels,
            "check_hotel_availability": check_hotel_availability,
            "book_hotel": self._book_hotel_with_dry_run,
            "estimate_total_cost": estimate_total_cost,
            "plan_destination": plan_destination,
            "get_attractions": get_attractions
        }
        
        # Conversation history for multi-turn interactions
        self.messages: list[dict] = []
    
    def _book_flight_with_dry_run(self, **kwargs) -> dict:
        """Wrapper to enforce dry_run based on config."""
        if self.config.dry_run_mode:
            kwargs["dry_run"] = True
        return book_flight(**kwargs)
    
    def _book_hotel_with_dry_run(self, **kwargs) -> dict:
        """Wrapper to enforce dry_run based on config."""
        if self.config.dry_run_mode:
            kwargs["dry_run"] = True
        return book_hotel(**kwargs)
    
    def _execute_tool(self, tool_name: str, arguments: dict) -> dict[str, Any]:
        """Execute a tool and return the result."""
        if tool_name not in self.function_map:
            return {
                "success": False,
                "error": f"Unknown function: {tool_name}"
            }
        
        try:
            func = self.function_map[tool_name]
            result = func(**arguments)
            return result
        except TypeError as e:
            return {
                "success": False,
                "error": f"Invalid arguments for {tool_name}: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Function execution failed: {str(e)}"
            }
    
    def process_request(self, user_input: str) -> dict[str, Any]:
        """
        Process a natural language travel request.
        
        Args:
            user_input: The user's travel request in natural language
        
        Returns:
            Structured JSON response with results
        """
        # Initialize conversation if empty
        if not self.messages:
            self.messages.append({
                "role": "system",
                "content": SYSTEM_PROMPT
            })
        
        # Add user message
        self.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Log the incoming request
        self.logger.log_agent_decision(
            user_input=user_input,
            decision="Processing request",
            tools_selected=[]
        )
        
        # Track all tool calls and results
        all_tool_results = []
        iteration = 0
        max_iterations = 10  # Prevent infinite loops
        
        while iteration < max_iterations:
            iteration += 1
            
            # Call Groq with tools
            try:
                response = self.groq_client.chat.completions.create(
                    model=self.config.model_name,
                    messages=self.messages,
                    tools=self.tools,
                    tool_choice="auto"
                )
            except Exception as e:
                error_result = {
                    "success": False,
                    "error": f"LLM API error: {str(e)}",
                    "tool_results": all_tool_results
                }
                self.logger.log(
                    "_agent_error",
                    {"user_input": user_input},
                    error_result,
                    success=False,
                    error=str(e)
                )
                return error_result
            
            message = response.choices[0].message
            
            # Check if there are tool calls
            if message.tool_calls:
                # Add assistant message with tool calls
                self.messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in message.tool_calls
                    ]
                })
                
                # Execute each tool call
                for tool_call in message.tool_calls:
                    func_name = tool_call.function.name
                    
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        arguments = {}
                    
                    # Log which tools are being called
                    self.logger.log_agent_decision(
                        user_input=user_input,
                        decision=f"Calling {func_name}",
                        tools_selected=[func_name]
                    )
                    
                    # Execute the tool
                    result = self._execute_tool(func_name, arguments)
                    all_tool_results.append({
                        "function": func_name,
                        "arguments": arguments,
                        "result": result
                    })
                    
                    # Add tool result to messages
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })
            else:
                # No more tool calls, LLM has final response
                final_content = message.content or ""
                
                # Try to parse as JSON, otherwise wrap it
                try:
                    final_response = json.loads(final_content)
                except json.JSONDecodeError:
                    final_response = {
                        "message": final_content,
                        "tool_results": all_tool_results
                    }
                
                # Add success indicator if not present
                if "success" not in final_response:
                    final_response["success"] = True
                
                # Add tool results if we have them
                if all_tool_results and "tool_results" not in final_response:
                    final_response["tool_results"] = all_tool_results
                
                # Add assistant's final message to history
                self.messages.append({
                    "role": "assistant",
                    "content": final_content
                })
                
                return final_response
        
        # Max iterations reached
        return {
            "success": False,
            "error": "Maximum iterations reached",
            "tool_results": all_tool_results
        }
    
    def reset_conversation(self):
        """Reset the conversation history."""
        self.messages = []
    
    def get_conversation_history(self) -> list[dict]:
        """Get the current conversation history."""
        return self.messages.copy()


def create_agent(config: Config | None = None) -> TravelAgent:
    """
    Factory function to create a TravelAgent instance.
    
    Args:
        config: Optional configuration. If not provided, loads from environment.
    
    Returns:
        Configured TravelAgent instance
    """
    if config is None:
        from .config import load_config
        config = load_config()
    
    return TravelAgent(config)
