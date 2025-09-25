## Azure Chat OpenAI with LangChain (Python)

Minimal runnable example using LangChain's `AzureChatOpenAI`.

Reference: [LangChain AzureChatOpenAI docs](https://python.langchain.com/docs/integrations/chat/azure_chat_openai/)

### Setup

1) Activate the virtual environment

```bash
source "env/bin/activate"
```

2) Install dependencies

```bash
pip install -r requirements.txt
```

3) Configure environment variables

Create a `.env` file in the project root with:

```bash
AZURE_OPENAI_API_KEY=YOUR_KEY
AZURE_OPENAI_ENDPOINT=https://YOUR-ENDPOINT.openai.azure.com/
AZURE_OPENAI_API_VERSION=2023-06-01-preview
AZURE_OPENAI_DEPLOYMENT=gpt-35-turbo
# Optional LangSmith
# LANGSMITH_API_KEY=...
# LANGSMITH_TRACING=true
```

4) Run the demo

```bash
python src/azure_chat_demo.py
```

Expected output: a French translation of the example text.
