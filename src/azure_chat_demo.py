import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

# Load environment variables from .env if present
load_dotenv()


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def build_llm() -> AzureChatOpenAI:
    deployment = get_required_env("AZURE_OPENAI_DEPLOYMENT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-06-01-preview")

    # Azure credentials are read from AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT
    llm = AzureChatOpenAI(
        azure_deployment=deployment,
        api_version=api_version,
        temperature=0,
        max_retries=2,
    )
    return llm


def run_demo() -> None:
    llm = build_llm()

    messages = [
        (
            "system",
            "You are a helpful assistant that translates English to French. Translate the user sentence.",
        ),
        ("human", "I love programming."),
    ]

    ai_msg = llm.invoke(messages)
    print(ai_msg.content)


if __name__ == "__main__":
    # Validate required envs explicitly for clear errors early
    _ = get_required_env("AZURE_OPENAI_API_KEY")
    _ = get_required_env("AZURE_OPENAI_ENDPOINT")
    _ = get_required_env("AZURE_OPENAI_DEPLOYMENT")
    # AZURE_OPENAI_API_VERSION is optional

    run_demo()
