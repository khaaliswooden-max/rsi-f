"""Zuup Domain Definitions and Prompt Generation."""

from .taxonomy import DOMAINS, Domain, EvaluationDimension, get_domain, get_all_domains
from .prompt_generator import PromptGenerator

__all__ = [
    "DOMAINS",
    "Domain", 
    "EvaluationDimension",
    "get_domain",
    "get_all_domains",
    "PromptGenerator",
]

