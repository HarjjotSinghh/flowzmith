from typing import Dict, Any, Optional
from src.config import settings
import openai
import groq

class LLMService:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.groq_client = groq.Groq(api_key=settings.GROQ_API_KEY)
        self.default_provider = settings.DEFAULT_LLM_PROVIDER

    async def generate_contract(
        self,
        prompt: str,
        provider: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate Cadence smart contract from natural language prompt"""
        provider = provider or self.default_provider

        system_prompt = """You are an expert Cadence smart contract developer for the Flow blockchain.
        Generate complete, secure, and efficient Cadence smart contracts based on user requirements.
        Follow Flow blockchain best practices and include proper access control, resource management,
        and error handling."""

        user_prompt = f"""
        Requirements: {prompt}

        Context: {context if context else 'No additional context provided'}

        Generate a complete Cadence smart contract that meets these requirements.
        Include proper comments and documentation.
        """

        if provider.upper() == "OPENAI":
            response = await self._generate_with_openai(system_prompt, user_prompt)
        elif provider.upper() == "GROQ":
            response = await self._generate_with_groq(system_prompt, user_prompt)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        return response

    async def _generate_with_openai(self, system_prompt: str, user_prompt: str) -> str:
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        return response.choices[0].message.content

    async def _generate_with_groq(self, system_prompt: str, user_prompt: str) -> str:
        response = self.groq_client.chat.completions.create(
            model="llama2-70b-4096",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        return response.choices[0].message.content

    async def optimize_contract(self, contract_code: str) -> str:
        """Optimize existing Cadence contract for better performance and security"""
        prompt = f"""
        Optimize the following Cadence smart contract for better performance, security, and gas efficiency:

        {contract_code}

        Provide the optimized version with explanations of changes made.
        """
        return await self.generate_contract(prompt)