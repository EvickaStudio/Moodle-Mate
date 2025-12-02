from typing import Dict

from .calculate import ModelPricing, ModelType


# Centralized catalog for supported AI models and their pricing.
DEFAULT_MODEL_PRICING: Dict[str, ModelPricing] = {
    ModelType.GPT4O.value: ModelPricing(2.50, 10.00),
    ModelType.GPT4O_MINI.value: ModelPricing(0.15, 0.60),
    ModelType.O1.value: ModelPricing(15.00, 60.00),
    ModelType.O1_MINI.value: ModelPricing(1.10, 4.40),
    ModelType.O3_MINI.value: ModelPricing(1.10, 4.40),
    ModelType.GPT51.value: ModelPricing(1.25, 10.00),
    ModelType.GPT5.value: ModelPricing(1.25, 10.00),
    ModelType.GPT5_MINI.value: ModelPricing(0.25, 2.00),
    ModelType.GPT5_NANO.value: ModelPricing(0.05, 0.40),
}


def get_default_model_pricing() -> Dict[str, ModelPricing]:
    """Return a copy of the default model pricing catalog."""
    return dict(DEFAULT_MODEL_PRICING)


def register_default_model(model: str, pricing: ModelPricing) -> None:
    """
    Register a model in the default catalog.

    This is useful for bootstrap code that wants to extend the catalog
    before GPT is instantiated.
    """
    DEFAULT_MODEL_PRICING[model] = pricing
