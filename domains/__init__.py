"""
Zuup Domain Definitions
=======================
"""

from .taxonomy import (
    Domain,
    Category,
    ScoringDimension,
    DimensionWeight,
    DOMAINS,
    get_domain,
    get_all_domains,
    get_domain_choices,
    get_category_choices,
    get_dimension_info,
)

from .prompt_generator import (
    SeedPrompt,
    SEED_PROMPTS,
    get_random_prompt,
    get_all_prompts,
    get_prompts_by_difficulty,
    get_prompt_stats,
    generate_prompt_pair,
)

__all__ = [
    "Domain",
    "Category", 
    "ScoringDimension",
    "DimensionWeight",
    "DOMAINS",
    "get_domain",
    "get_all_domains",
    "get_domain_choices",
    "get_category_choices",
    "get_dimension_info",
    "SeedPrompt",
    "SEED_PROMPTS",
    "get_random_prompt",
    "get_all_prompts",
    "get_prompts_by_difficulty",
    "get_prompt_stats",
    "generate_prompt_pair",
]

