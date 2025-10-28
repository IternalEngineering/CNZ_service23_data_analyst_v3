"""
Unified LLM Client Configuration
Provides OpenAI/OpenRouter client with cost tracking and model selection
"""
import os
from typing import Literal

class LLMClient:
    """Wrapper for LLM client with metadata"""
    def __init__(self, model: str, temperature: float = 0.7, max_tokens: int = 4096):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Cost estimates per 1M tokens (rough averages)
        self.cost_map = {
            "gpt-4o-mini": 0.15,
            "gpt-4o": 2.50,
            "gpt-4": 30.0,
            "gemini-flash-1.5": 0.075,
            "claude-3-haiku": 0.25,
        }
        self.estimated_cost = self.cost_map.get(model, 1.0)

def get_llm_client(
    task_type: Literal["analysis", "generation", "expensive"] = "analysis",
    temperature: float = 0.7,
    max_tokens: int = 4096
) -> LLMClient:
    """
    Get LLM client based on task type
    
    Args:
        task_type: Type of task (analysis=cheap, generation=medium, expensive=high-quality)
        temperature: Sampling temperature
        max_tokens: Maximum tokens in response
        
    Returns:
        LLMClient with model and cost metadata
    """
    # Model selection based on task type
    model_map = {
        "analysis": "gpt-4o-mini",      # Cheap tier
        "generation": "gpt-4o",         # Medium tier
        "expensive": "gpt-4",           # High-quality tier
    }
    
    model = model_map.get(task_type, "gpt-4o-mini")
    
    return LLMClient(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens
    )
