"""
Test script for LLM configuration module
"""

import llm_config

def test_providers():
    """Test that all providers are available"""
    print("Testing LLM Configuration Module")
    print("=" * 50)
    
    # Test available providers
    providers = llm_config.LLMConfig.get_available_providers()
    print(f"\nAvailable providers: {providers}")
    
    # Test models for each provider
    for provider in providers:
        models = llm_config.LLMConfig.get_models_for_provider(provider)
        print(f"\n{provider} models:")
        for model in models:
            print(f"  - {model}")
    
    print("\n" + "=" * 50)
    print("✅ Configuration module loaded successfully!")
    print("\nTo use OpenAI:")
    print("1. Select 'OpenAI' as provider")
    print("2. Choose a model (e.g., 'GPT-4 Turbo')")
    print("3. Enter your OpenAI API key")
    print("\nTo use Qwen:")
    print("1. Select 'Qwen (Alibaba Cloud)' as provider")
    print("2. Choose a model (e.g., 'Qwen Plus')")
    print("3. Enter your Qwen API key")
    print("\nTo use DeepSeek:")
    print("1. Select 'DeepSeek' as provider")
    print("2. Choose a model (e.g., 'DeepSeek Chat')")
    print("3. Enter your DeepSeek API key")

if __name__ == "__main__":
    test_providers()
