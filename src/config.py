"""
Configuration management for Travel Agent.
Loads settings from environment variables.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class Config:
    """Application configuration."""
    groq_api_key: str
    dry_run_mode: bool = False
    model_name: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    log_file: str = "logs/audit.jsonl"
    
    def __post_init__(self):
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY is required. Set it in .env file or environment.")


def load_config() -> Config:
    """Load configuration from environment variables."""
    load_dotenv()
    
    return Config(
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        dry_run_mode=os.getenv("DRY_RUN_MODE", "false").lower() == "true",
        model_name=os.getenv("GROQ_MODEL_ID", "meta-llama/llama-4-scout-17b-16e-instruct"),
        log_file=os.getenv("LOG_FILE", "logs/audit.jsonl")
    )
