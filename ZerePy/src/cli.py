# src/cli.py
import logging
from typing import Dict, Any, Callable

logger = logging.getLogger("zerepycli")

class ZerePyCLI:
    """Simple CLI for registering and executing actions"""
    
    def __init__(self):
        self.actions = {}
    
    def register_action(self, action_name: str, action_func: Callable = None):
        """Register an action with the CLI"""
        def decorator(func):
            self.actions[action_name] = func
            logger.debug(f"Registered action: {action_name}")
            return func
        
        if action_func:
            return decorator(action_func)
        return decorator
    
    def perform_action(self, action_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a registered action"""
        if action_name not in self.actions:
            logger.error(f"Action not found: {action_name}")
            return {"success": False, "error": f"Action not found: {action_name}"}
        
        try:
            logger.debug(f"Executing action: {action_name}")
            return self.actions[action_name](**kwargs)
        except Exception as e:
            logger.error(f"Error executing action {action_name}: {str(e)}")
            return {"success": False, "error": f"Error executing action: {str(e)}"}
