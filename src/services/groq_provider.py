"""
Groq LLM provider implementation with a safe HTTP fallback client.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Iterator, Any as AnyType
import requests

from .llm_provider import LLMProvider, LLMProviderType, LLMResponse
from .llm_provider import PromptTemplateManager, PromptTemplate

# Try to import the official Groq SDK (if installed)
try:
    from groq import Groq  # adjust import if SDK name differs
    GROQ_AVAILABLE = True
except Exception:
    GROQ_AVAILABLE = False
    Groq = None

logger = logging.getLogger(__name__)


class GroqHTTPClient:
    """
    Thin HTTP client wrapper exposing `chat.completions.create(..., stream=...)`
    that is compatible with existing streaming code expecting objects with:
        chunk.choices[0].delta.content
    """

    def __init__(self, api_key: str, base_url: Optional[str] = None, timeout: int = 300):
        self.api_key = api_key
        self.base_url = (base_url or os.getenv("GROQ_BASE_URL", "https://api.groq.com")).rstrip("/")
        self.timeout = timeout

    class _Chat:
        def __init__(self, outer: "GroqHTTPClient"):
            self._outer = outer

        class _Completions:
            def __init__(self, outer: "GroqHTTPClient"):
                self._outer = outer

            def create(self, model: str, messages: list, temperature: float = 0.3,
                       max_tokens: Optional[int] = None, top_p: float = 0.9,
                       stream: bool = False, **kwargs) -> AnyType:
                url = f"{self._outer.base_url}/chat/completions"
                headers = {
                    "Authorization": f"Bearer {self._outer.api_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                }
                if max_tokens:
                    payload["max_tokens"] = max_tokens
                payload.update(kwargs or {})

                if stream:
                    # streaming: use requests and yield chunk-like objects
                    with requests.post(url, headers=headers, json=payload, stream=True, timeout=self._outer.timeout) as resp:
                        resp.raise_for_status()
                        for raw_line in resp.iter_lines(decode_unicode=True):
                            if not raw_line:
                                continue
                            line = raw_line.strip()
                            # skip keepalive / [done]
                            if not line or line.lower() in ("[done]", "data: [done]"):
                                continue
                            # remove SSE "data: " prefix if present
                            if line.startswith("data:"):
                                line = line[len("data:"):].strip()
                            # try to parse json
                            try:
                                data = json.loads(line)
                            except Exception:
                                # build a minimal chunk-like object with delta.content
                                chunk = type("C", (), {})()
                                chunk.choices = [type("Ch", (), {"delta": type("D", (), {"content": line})()})()]
                                yield chunk
                                continue

                            # If the provider sends choices/delta structure, wrap into object
                            if isinstance(data, dict) and "choices" in data:
                                class _Chunk:
                                    def __init__(self, raw):
                                        self.raw = raw
                                        self.choices = []
                                        for ch in raw.get("choices", []):
                                            delta = ch.get("delta", {})
                                            obj_delta = type("D", (), {})()
                                            setattr(obj_delta, "content", delta.get("content"))
                                            obj_choice = type("Ch", (), {"delta": obj_delta})()
                                            self.choices.append(obj_choice)
                                yield _Chunk(data)
                            else:
                                # fallback raw text chunk
                                chunk = type("C", (), {})()
                                chunk.choices = [type("Ch", (), {"delta": type("D", (), {"content": str(data)})()})()]
                                yield chunk
                else:
                    # non-streaming: return parsed JSON
                    with requests.post(url, headers=headers, json=payload, timeout=self._outer.timeout) as resp:
                        resp.raise_for_status()
                        return resp.json()

            @property
            def completions(self):
                return GroqHTTPClient._Chat._Completions(self._outer)

        def __init__(self, outer):
            self._outer = outer

    @property
    def chat(self):
        return GroqHTTPClient._Chat(self)


class GroqProvider(LLMProvider):
    """Groq API provider implementation with safe client initialization."""

    def __init__(self, api_key: str, model: str = "llama2-70b-4096"):
        # Initialize client before calling super() because validate_credentials() needs it
        self.base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com")
        self.provider_type = LLMProviderType.GROQ

        # Try to initialize the official SDK client if available and usable
        self.client = None
        if GROQ_AVAILABLE and Groq is not None:
            try:
                sdk_client = Groq(api_key=api_key)  # adapt if constructor differs
                # If SDK exposes chat or completions directly, use it
                # Normalize to expect .chat.completions.create interface
                if hasattr(sdk_client, "chat"):
                    self.client = sdk_client
                elif hasattr(sdk_client, "client") and hasattr(sdk_client.client, "chat"):
                    # some SDKs expose a .client wrapper
                    self.client = sdk_client.client
                else:
                    # SDK available but not in expected shape -> fallback to HTTP wrapper
                    logger.warning("Groq SDK imported but doesn't expose chat.completions; falling back to HTTP client.")
                    self.client = GroqHTTPClient(api_key=api_key, base_url=self.base_url)
            except Exception as e:
                logger.exception("Failed to initialize Groq SDK client; falling back to HTTP wrapper: %s", e)
                self.client = GroqHTTPClient(api_key=api_key, base_url=self.base_url)
        else:
            # SDK not available -> use HTTP wrapper
            self.client = GroqHTTPClient(api_key=api_key, base_url=self.base_url)

        # Call parent constructor after client is initialized
        super().__init__(api_key, model)

    def validate_credentials(self) -> bool:
        """Validate Groq API credentials by making a small non-streaming chat call."""
        try:
            # simple non-streaming ping call; adapt messages as needed
            messages = [{"role": "system", "content": "Validate credentials"}, {"role": "user", "content": "ping"}]
            # call the client's create in non-streaming mode
            resp = self.client.chat.completions.create(model=self.model, messages=messages, stream=False)
            # If response is dict-like and no exception, assume credentials ok
            if isinstance(resp, dict):
                logger.info("Groq credentials validated (received dict response).")
                return True
            # Some SDKs may return objects; treat success if no exception thrown
            logger.info("Groq credential check succeeded.")
            return True
        except Exception as e:
            logger.error("Groq credential validation failed: %s", e)
            raise ValueError(f"Invalid Groq API key: {e}")

    async def generate_contract(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """Generate contract code using Groq (non-streaming)."""
        prompt_manager = PromptTemplateManager()
        if system_prompt is None:
            # Use the detailed Cadence 1.0 template as default system prompt
            system_prompt = prompt_manager.get_template("cadence_v1_detailed").template
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            # Use non-streaming create call with conservative token limits
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens or 2000,  # Reduced from 4000 to 2000 for Groq API limits
                top_p=0.9,
                stream=False
            )

            # response may be dict or SDK object — handle dict first
            if isinstance(response, dict):
                # defensive extraction
                choices = response.get("choices", [])
                usage = response.get("usage", {})
                text = ""
                finish_reason = None
                if choices:
                    first = choices[0]
                    # SDK-style: first.get("message", {}).get("content")
                    text = first.get("message", {}).get("content") or first.get("text") or ""
                    finish_reason = first.get("finish_reason")
                tokens_used = usage.get("total_tokens", 0)
            else:
                # SDK object: try to access expected attributes
                try:
                    text = response.choices[0].message.content
                    tokens_used = getattr(response.usage, "total_tokens", 0)
                    finish_reason = getattr(response.choices[0], "finish_reason", None)
                except Exception:
                    # fallback
                    text = str(response)
                    tokens_used = 0
                    finish_reason = None

            cost = self._calculate_cost(tokens_used)

            return LLMResponse(
                content=text,
                provider=LLMProviderType.GROQ,
                model=self.model,
                tokens_used=tokens_used,
                cost=cost,
                metadata={
                    "finish_reason": finish_reason
                }
            )

        except Exception as e:
            logger.exception("Groq contract generation failed: %s", e)
            raise RuntimeError(f"Groq API error: {e}")

    async def analyze_deployment_logs(
        self,
        logs: str,
        contract_code: str
    ) -> LLMResponse:
        """Analyze deployment logs for learning."""
        prompt_manager = PromptTemplateManager()
        system_prompt = "You are an expert Flow blockchain deployment analyst. Analyze deployment logs to identify patterns, errors, and optimization opportunities. Provide structured insights in JSON format, ensuring Cadence 1.0 compliance checks."
        prompt_template = prompt_manager.get_template("log_analysis")
        prompt = prompt_template.template.format(contract_code=contract_code, logs=logs)
        try:
            # Use the formatted log analysis template with 1.0 awareness
            return await self.generate_contract(prompt=prompt, system_prompt=system_prompt, temperature=0.2)

        except Exception as e:
            logger.error(f"Groq log analysis failed: {e}")
            raise RuntimeError(f"Groq log analysis error: {e}")

    async def validate_configuration(
        self,
        config: Dict[str, Any],
        contract_code: str
    ) -> LLMResponse:
        """Validate generated configuration."""
        prompt_manager = PromptTemplateManager()
        # Adapt flow_config for validation
        validation_template = PromptTemplate(
            name="config_validation",
            template="""Validate the following flow.json configuration for the Cadence 1.0 smart contract:

Contract Code:
{contract_code}

Configuration to Validate:
{config_json}

Validation Checklist (Cadence 1.0):
1. Correct contract interface definitions (inheritance, no restricted types)
2. Proper network settings with 1.0 accounts and entitlements
3. Valid account addresses and capability controllers
4. Complete alias definitions for deployed contracts
5. Deployment compatibility (v2 token support if applicable)
6. No deprecated syntax or migration issues

Return a JSON response with:
- valid: boolean
- issues: list of problems
- suggestions: list of fixes
- compliance_score: 0-100""",
            variables=["contract_code", "config_json"],
            description="Validation template for 1.0 configs"
        )
        prompt = validation_template.template.format(
            contract_code=contract_code,
            config_json=json.dumps(config, indent=2)
        )
        system_prompt = "You are an expert Flow blockchain configuration validator for Cadence 1.0. Ensure full migration compliance."
        try:
            # Use the formatted validation template with 1.0 awareness
            return await self.generate_contract(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.1
            )

        except Exception as e:
            logger.error(f"Groq configuration validation failed: {e}")
            raise RuntimeError(f"Groq validation error: {e}")

    def _calculate_cost(self, total_tokens: int) -> float:
        """Approximate cost placeholder."""
        return total_tokens * 0.000001  # placeholder


# Register the provider
from .llm_provider import LLMProviderFactory
LLMProviderFactory.register_provider(LLMProviderType.GROQ, GroqProvider)
