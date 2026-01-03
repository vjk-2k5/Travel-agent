"""
Audit logging system for Travel Agent.
Logs all function calls with timestamps for traceability.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Optional


class AuditLogger:
    """Structured JSON audit logger for all agent actions."""
    
    def __init__(self, log_file: str = "logs/audit.jsonl"):
        self.log_file = log_file
        self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        """Create log directory if it doesn't exist."""
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    
    def _generate_audit_id(self) -> str:
        """Generate a unique audit log ID."""
        return f"AUD-{uuid.uuid4().hex[:8].upper()}"
    
    def log(
        self,
        function_name: str,
        parameters: dict,
        result: Any,
        success: bool = True,
        error: Optional[str] = None
    ) -> str:
        """
        Log a function call with all details.
        
        Returns:
            str: The audit log ID for this entry.
        """
        audit_id = self._generate_audit_id()
        
        log_entry = {
            "audit_id": audit_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "function": function_name,
            "parameters": parameters,
            "result": result if success else None,
            "success": success,
            "error": error
        }
        
        # Write to file
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        return audit_id
    
    def log_agent_decision(
        self,
        user_input: str,
        decision: str,
        tools_selected: list[str]
    ) -> str:
        """Log an agent decision/reasoning step."""
        return self.log(
            function_name="_agent_decision",
            parameters={
                "user_input": user_input,
                "tools_selected": tools_selected
            },
            result={"decision": decision},
            success=True
        )
    
    def log_refusal(
        self,
        user_input: str,
        reason: str
    ) -> str:
        """Log when the agent refuses to act."""
        return self.log(
            function_name="_agent_refusal",
            parameters={"user_input": user_input},
            result={"reason": reason},
            success=True
        )


# Global logger instance
_logger: Optional[AuditLogger] = None


def get_logger(log_file: str = "logs/audit.jsonl") -> AuditLogger:
    """Get or create the global audit logger."""
    global _logger
    if _logger is None:
        _logger = AuditLogger(log_file)
    return _logger
