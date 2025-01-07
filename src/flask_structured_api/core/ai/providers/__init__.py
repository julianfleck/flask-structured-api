from typing import Dict, Type
from flask_structured_api.core.ai.providers.base import BaseProvider
from flask_structured_api.core.ai.providers.openai import OpenAIProvider
from flask_structured_api.core.ai.providers.azure import AzureProvider
from flask_structured_api.core.ai.providers.anthropic import AnthropicProvider
from flask_structured_api.core.config import settings

PROVIDER_REGISTRY: Dict[str, Type[BaseProvider]] = {
    "openai": OpenAIProvider,
    "azure": AzureProvider,
    "anthropic": AnthropicProvider
}


def get_provider(provider_name: str) -> BaseProvider:
    """Get provider instance by name"""
    provider_class = PROVIDER_REGISTRY.get(provider_name.lower())
    if not provider_class:
        raise ValueError("Unsupported AI provider: {}".format(provider_name))

    return provider_class()


__all__ = [
    'BaseProvider',
    'OpenAIProvider',
    'AzureProvider',
    'AnthropicProvider',
    'get_provider',
    'PROVIDER_REGISTRY'
]
