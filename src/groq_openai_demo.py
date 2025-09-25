from openai import OpenAI
import os

from dotenv import load_dotenv
load_dotenv()


client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url=os.environ.get("GROQ_ENDPOINT"),
)

response = client.responses.create(
    input="Which model are you? What is your context limit? Can we attach files like .txt files? If yes, what is your file size upload limit (all files total)?",
    model="meta-llama/llama-4-maverick-17b-128e-instruct",
)
print(response.output_text)


