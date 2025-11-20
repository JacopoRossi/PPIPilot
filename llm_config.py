"""
LLM Configuration Module
Supports multiple LLM providers including OpenAI and Qwen
"""

from openai import OpenAI
from typing import Dict, Any, Optional

class LLMProvider:
    """Base class for LLM providers"""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.client = None
    
    def get_client(self):
        """Returns the configured client"""
        raise NotImplementedError
    
    def get_model_name(self):
        """Returns the model name to use"""
        return self.model


class OpenAIProvider(LLMProvider):
    """OpenAI provider configuration"""
    
    MODELS = {
        "GPT-4 Turbo": "gpt-4-0125-preview",
        "GPT-4": "gpt-4",
        "GPT-3.5 Turbo": "gpt-3.5-turbo",
    }
    
    def __init__(self, api_key: str, model_name: str = "GPT-4 Turbo"):
        model = self.MODELS.get(model_name, "gpt-4-0125-preview")
        super().__init__(api_key, model)
        self.client = OpenAI(api_key=api_key)
    
    def get_client(self):
        return self.client


class QwenProvider(LLMProvider):
    """Qwen (Alibaba Cloud) provider configuration"""
    
    MODELS = {
        "Qwen Plus": "qwen-plus",
        "Qwen Turbo": "qwen-turbo",
        "Qwen Max": "qwen-max",
        "Qwen 3 Max": "qwen3-max",
    }
    
    def __init__(self, api_key: str, model_name: str = "Qwen 3 Max"):
        model = self.MODELS.get(model_name, "qwen3-max")
        super().__init__(api_key, model)
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        )
    
    def get_client(self):
        return self.client


class DeepSeekProvider(LLMProvider):
    """DeepSeek provider configuration"""
    
    MODELS = {
        "DeepSeek Chat": "deepseek-chat",
        "DeepSeek Coder": "deepseek-coder",
    }
    
    def __init__(self, api_key: str, model_name: str = "DeepSeek Chat"):
        model = self.MODELS.get(model_name, "deepseek-chat")
        super().__init__(api_key, model)
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
        )
    
    def get_client(self):
        return self.client


class LLMConfig:
    """Main configuration class for LLM management"""
    
    PROVIDERS = {
        "OpenAI": OpenAIProvider,
        "Qwen (Alibaba Cloud)": QwenProvider,
        "DeepSeek": DeepSeekProvider,
    }
    
    @staticmethod
    def create_provider(provider_name: str, api_key: str, model_name: str) -> LLMProvider:
        """
        Factory method to create an LLM provider
        
        Args:
            provider_name: Name of the provider (e.g., "OpenAI", "Qwen (Alibaba Cloud)")
            api_key: API key for the provider
            model_name: Model name to use
        
        Returns:
            Configured LLMProvider instance
        """
        provider_class = LLMConfig.PROVIDERS.get(provider_name)
        if not provider_class:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        return provider_class(api_key, model_name)
    
    @staticmethod
    def get_available_providers():
        """Returns list of available provider names"""
        return list(LLMConfig.PROVIDERS.keys())
    
    @staticmethod
    def get_models_for_provider(provider_name: str):
        """Returns available models for a given provider"""
        provider_class = LLMConfig.PROVIDERS.get(provider_name)
        if not provider_class:
            return []
        return list(provider_class.MODELS.keys())


def get_completion(client, prompt: str, model: str, temperature: float = 0) -> str:
    """
    Universal completion function that works with any OpenAI-compatible client
    
    Args:
        client: OpenAI-compatible client instance
        prompt: The prompt to send
        model: Model name to use
        temperature: Temperature parameter (default: 0)
    
    Returns:
        Completion text from the model
    """
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    
    return response.choices[0].message.content
