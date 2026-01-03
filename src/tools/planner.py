"""
Destination planning tools using Hugging Face Mistral 7B.
Provides AI-powered recommendations for places to visit.
"""

import os
from typing import Any

from huggingface_hub import InferenceClient

from ..utils.logger import get_logger


# Hugging Face model for destination planning
HF_MODEL = "meta-llama/Meta-Llama-3-8B"


def _get_hf_client() -> InferenceClient:
    """Get Hugging Face inference client."""
    token = os.getenv("HUGGINGFACE_API_TOKEN") or os.getenv("HF_API_TOKEN")
    if not token:
        raise ValueError("HUGGINGFACE_API_TOKEN not set. Please add your Hugging Face API token to .env")
    return InferenceClient(token=token)


def _build_destination_prompt(
    destination: str,
    days: int,
    interests: list[str] | None,
    travel_style: str | None
) -> str:
    """Build the prompt for destination planning."""
    interests_str = ", ".join(interests) if interests else "general sightseeing"
    style_str = travel_style or "balanced"
    
    prompt = f"""<s>[INST] You are a travel planning expert. Create a detailed day-by-day itinerary for visiting {destination}.

Trip Details:
- Duration: {days} days
- Interests: {interests_str}
- Travel Style: {style_str}

Provide a structured itinerary with:
1. Day-by-day plan with specific places to visit
2. Best time to visit each place
3. Estimated time at each location
4. Local tips and recommendations
5. Must-try local food/restaurants

Format your response as a clear, structured plan. Be specific with place names and timings. [/INST]</s>"""
    
    return prompt


def plan_destination(
    destination: str,
    days: int = 3,
    interests: list[str] | None = None,
    travel_style: str | None = None,
    budget: str | None = None
) -> dict[str, Any]:
    """
    Plan places to visit at a destination using AI.
    
    Args:
        destination: The destination city/country to plan for
        days: Number of days for the trip (default: 3)
        interests: List of interests (e.g., ["history", "food", "nature"])
        travel_style: Style preference ("budget", "luxury", "adventure", "relaxed")
        budget: Budget level ("budget", "moderate", "luxury")
    
    Returns:
        Dictionary with the itinerary and recommendations
    """
    logger = get_logger()
    
    params = {
        "destination": destination,
        "days": days,
        "interests": interests,
        "travel_style": travel_style,
        "budget": budget
    }
    
    try:
        client = _get_hf_client()
        prompt = _build_destination_prompt(destination, days, interests, travel_style)
        
        # Call Mistral 7B via Hugging Face Inference API
        response = client.text_generation(
            prompt,
            model=HF_MODEL,
            max_new_tokens=1500,
            temperature=0.7,
            do_sample=True,
            return_full_text=False
        )
        
        # Parse the response into structured format
        itinerary_text = response.strip()
        
        result = {
            "success": True,
            "destination": destination,
            "days": days,
            "travel_style": travel_style or "balanced",
            "interests": interests or ["general sightseeing"],
            "itinerary": itinerary_text,
            "generated_by": "Mistral-7B-Instruct",
            "disclaimer": "This is an AI-generated itinerary. Please verify opening hours and availability before visiting."
        }
        
        logger.log("plan_destination", params, {"success": True, "destination": destination})
        return result
        
    except ValueError as e:
        error_result = {
            "success": False,
            "error": str(e),
            "destination": destination
        }
        logger.log("plan_destination", params, error_result, success=False, error=str(e))
        return error_result
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"Failed to generate itinerary: {str(e)}",
            "destination": destination
        }
        logger.log("plan_destination", params, error_result, success=False, error=str(e))
        return error_result


def get_attractions(
    destination: str,
    category: str | None = None,
    limit: int = 10
) -> dict[str, Any]:
    """
    Get top attractions for a destination.
    
    Args:
        destination: The destination to get attractions for
        category: Category filter (e.g., "museums", "nature", "food")
        limit: Maximum number of attractions to return
    
    Returns:
        Dictionary with list of attractions
    """
    logger = get_logger()
    
    params = {
        "destination": destination,
        "category": category,
        "limit": limit
    }
    
    try:
        client = _get_hf_client()
        
        category_str = f" in the {category} category" if category else ""
        prompt = f"""<s>[INST] List the top {limit} must-visit attractions in {destination}{category_str}.

For each attraction, provide:
- Name
- Type (museum, park, landmark, etc.)
- Brief description (1-2 sentences)
- Typical visit duration
- Best time to visit

Format as a numbered list. Be specific and accurate. [/INST]</s>"""
        
        response = client.text_generation(
            prompt,
            model=HF_MODEL,
            max_new_tokens=1000,
            temperature=0.7,
            do_sample=True,
            return_full_text=False
        )
        
        result = {
            "success": True,
            "destination": destination,
            "category": category,
            "attractions": response.strip(),
            "generated_by": "Mistral-7B-Instruct"
        }
        
        logger.log("get_attractions", params, {"success": True, "destination": destination})
        return result
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"Failed to get attractions: {str(e)}",
            "destination": destination
        }
        logger.log("get_attractions", params, error_result, success=False, error=str(e))
        return error_result
