# Multi-LLM Support Configuration

## Overview

PPIPilot now supports multiple Large Language Model (LLM) providers, including:
- **OpenAI** (GPT-4, GPT-3.5)
- **Qwen (Alibaba Cloud)** (Qwen Plus, Qwen Turbo, Qwen Max)
- **DeepSeek** (DeepSeek Chat, DeepSeek Coder)

## Installation

Make sure you have the required dependencies installed:

```bash
pip install -r requirements.txt
```

## Usage

### 1. Starting the Application

Run the Streamlit interface as usual:

**Standard Mode:**
```bash
streamlit run interface_2.py
```

**Batch Mode:**
```bash
streamlit run interface_batch.py
```

Both interfaces now support multiple LLM providers.

### 2. Selecting an LLM Provider

In the web interface, you'll now see two new dropdown menus:

1. **Select LLM Provider**: Choose between "OpenAI", "Qwen (Alibaba Cloud)", or "DeepSeek"
2. **Select Model**: Choose the specific model you want to use (options change based on provider)

### 3. Configuring API Keys

#### For OpenAI:
- Select "OpenAI" as provider
- Choose a model (e.g., "GPT-4 Turbo")
- Enter your OpenAI API key in the "Set API key" field

#### For Qwen (Alibaba Cloud):
- Select "Qwen (Alibaba Cloud)" as provider
- Choose a model (e.g., "Qwen Plus")
- Enter your Qwen API key in the "Set API key" field

#### For DeepSeek:
- Select "DeepSeek" as provider
- Choose a model (e.g., "DeepSeek Chat")
- Enter your DeepSeek API key in the "Set API key" field

## Configuration Examples

### Qwen Configuration

The Qwen integration uses the OpenAI-compatible API endpoint provided by Alibaba Cloud:

```python
from openai import OpenAI

client = OpenAI(
    api_key="your-qwen-api-key",
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
)

completion = client.chat.completions.create(
    model="qwen-plus",
    messages=[
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': 'Who are you?'}
    ]
)
```

### DeepSeek Configuration

The DeepSeek integration uses the OpenAI-compatible API:

```python
from openai import OpenAI

client = OpenAI(
    api_key="your-deepseek-api-key",
    base_url="https://api.deepseek.com",
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False
)
```

## Available Models

### OpenAI Models:
- **GPT-4 Turbo** (gpt-4-0125-preview) - Recommended
- **GPT-4** (gpt-4)
- **GPT-3.5 Turbo** (gpt-3.5-turbo)

### Qwen Models:
- **Qwen Plus** (qwen-plus) - Recommended, balanced performance
- **Qwen Turbo** (qwen-turbo) - Faster, lower cost
- **Qwen Max** (qwen-max) - Most capable

### DeepSeek Models:
- **DeepSeek Chat** (deepseek-chat) - Recommended, general purpose
- **DeepSeek Coder** (deepseek-coder) - Optimized for code generation

## Adding New LLM Providers

To add support for additional LLM providers, edit the `llm_config.py` file:

1. Create a new provider class that inherits from `LLMProvider`
2. Implement the `get_client()` method
3. Define the available models in the `MODELS` dictionary
4. Add the provider to `LLMConfig.PROVIDERS`

Example:

```python
class NewProvider(LLMProvider):
    MODELS = {
        "Model Name": "model-id",
    }
    
    def __init__(self, api_key: str, model_name: str = "Model Name"):
        model = self.MODELS.get(model_name, "model-id")
        super().__init__(api_key, model)
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.provider.com/v1",
        )
    
    def get_client(self):
        return self.client
```

## Technical Details

### Architecture

The multi-LLM support is implemented through:

1. **llm_config.py**: Core configuration module with provider classes
2. **interface_2.py**: Standard mode UI with provider/model selection
3. **interface_batch.py**: Batch mode UI with provider/model selection
4. **fromLogtoPPI_prompt_pipeline_goal.py**: Updated pipeline to accept model parameter

### Key Changes

- All LLM completion calls now accept a `model` parameter
- The selected model is stored in `st.session_state.model`
- The client is created dynamically based on provider selection
- All error correction and retry mechanisms support the model parameter

## Troubleshooting

### "ModuleNotFoundError: No module named 'openai'"
Run: `pip install -r requirements.txt`

### "Authentication Error"
- Verify your API key is correct
- For Qwen: Ensure you're using the international API key from DashScope
- For OpenAI: Check your API key has sufficient credits
- For DeepSeek: Verify your API key from the DeepSeek platform

### "Model not found"
- Verify the model name matches the provider's available models
- Check if you have access to the selected model with your API key

## API Key Resources

- **OpenAI API Keys**: https://platform.openai.com/api-keys
- **Qwen API Keys**: https://dashscope.console.aliyun.com/
- **DeepSeek API Keys**: https://platform.deepseek.com/

## Notes

- The model selection is persistent across sessions (stored in session state)
- All existing functionality (error correction, retry mechanisms) works with any provider
- The system automatically uses the OpenAI-compatible API format for all providers
