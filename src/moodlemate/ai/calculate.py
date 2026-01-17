from dataclasses import dataclass
from enum import Enum


class ModelType(Enum):
    """Supported OpenAI model types."""

    GPT4O = "gpt-4o"
    GPT4O_MINI = "gpt-4o-mini"
    O1 = "o1"
    O1_MINI = "o1-mini"
    O3_MINI = "o3-mini"
    GPT51 = "gpt-5.1"
    GPT5 = "gpt-5"
    GPT5_MINI = "gpt-5-mini"
    GPT5_NANO = "gpt-5-nano"


@dataclass
class ModelPricing:
    """Pricing information for a model."""

    input_cost_per_1m: float
    output_cost_per_1m: float

    def calculate_costs(
        self, input_tokens: int, output_tokens: int
    ) -> tuple[float, float, float]:
        """Calculate costs for token usage."""
        input_cost = input_tokens * (self.input_cost_per_1m / 1_000_000)
        output_cost = output_tokens * (self.output_cost_per_1m / 1_000_000)
        return input_cost, output_cost, input_cost + output_cost
