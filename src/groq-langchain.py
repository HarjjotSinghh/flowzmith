import os
import getpass

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate


def ensure_groq_api_key_loaded() -> None:
    """Load GROQ_API_KEY from environment or prompt the user securely once."""
    load_dotenv()
    if "GROQ_API_KEY" not in os.environ or not os.environ.get("GROQ_API_KEY"):
        os.environ["GROQ_API_KEY"] = getpass.getpass("Enter your Groq API key: ")


def demo_basic_invoke() -> None:
    """Instantiate ChatGroq and run a simple invocation following the guide."""
    llm = ChatGroq(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        temperature=0,
        max_tokens=None,
        reasoning_format="parsed",
        timeout=None,
        max_retries=2,
    )

    messages = [
        (
            "system",
            "Answer all questions asked honestly.",
        ),
        ("human", "Which model are you? What is your context limit? Can we attach files like .txt files? If yes, what is your file size upload limit (all files total)?"),
    ]

    ai_msg = llm.invoke(messages)
    print("--- Basic invoke result ---")
    print(ai_msg.content)


def demo_prompt_chaining() -> None:
    """Demonstrate chaining with ChatPromptTemplate and ChatGroq."""
    llm = ChatGroq(
        model="deepseek-r1-distill-llama-70b",
        temperature=0,
        max_tokens=None,
        reasoning_format="parsed",
        timeout=None,
        max_retries=2,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant that translates {input_language} to {output_language}.",
            ),
            ("human", "{input}"),
        ]
    )

    chain = prompt | llm
    ai_msg = chain.invoke(
        {
            "input_language": "English",
            "output_language": "German",
            "input": "I love programming.",
        }
    )

    print("--- Chaining result ---")
    print(ai_msg.content)


if __name__ == "__main__":
    ensure_groq_api_key_loaded()
    demo_basic_invoke()
    demo_prompt_chaining()


