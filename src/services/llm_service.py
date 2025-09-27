"""
Main LLM service for Flowzmith.
"""

from typing import Dict, Any, Optional, List, AsyncGenerator
import logging
from enum import Enum
from sqlalchemy.orm import Session
import os

from dotenv import load_dotenv
load_dotenv()


from .llm_provider import (
    LLMProviderFactory,
    LLMProviderType,
    PromptTemplateManager,
    LLMResponse
)
from .streaming_llm_provider import (
    StreamingLLMService,
    StreamingProgressTracker
)
from ..models import (
    ContractSubmission,
    GeneratedConfiguration,
    DeploymentLog,
    LearningFeedbackLoop,
    PatternType
)
from ..config import get_settings
from .openai_provider import OpenAIProvider  # ensure provider registration
from .groq_provider import GroqProvider  # ensure provider registration

logger = logging.getLogger(__name__)


class LLMService:
    """Main service for LLM operations."""

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.settings = get_settings()
        self.prompt_manager = PromptTemplateManager()
        self.providers: Dict[LLMProviderType, Any] = {}

        openai_api_key = self._clean(os.getenv('OPENAI_API_KEY'))
        groq_api_key = self._clean(os.getenv('GROQ_API_KEY'))

        # Persist cleaned values back to settings
        self.settings.openai_api_key = openai_api_key
        self.settings.groq_api_key = groq_api_key

        # Initialize OpenAI provider if configured
        if openai_api_key:
            try:
                self.providers[LLMProviderType.OPENAI] = LLMProviderFactory.create_provider(
                    LLMProviderType.OPENAI,
                    openai_api_key,
                    os.getenv('OPENAI_MODEL') or "gpt-4"
                )
                logger.info("OpenAI provider initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI provider: {e}")

        # Initialize Groq provider if configured
        if groq_api_key:
            try:    
                self.providers[LLMProviderType.GROQ] = LLMProviderFactory.create_provider(
                    LLMProviderType.GROQ,
                    groq_api_key,
                    os.getenv('GROQ_MODEL') or "meta-llama/llama-4-maverick-17b-128e-instruct"
                )
                logger.info("Groq provider initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Groq provider: {e}")

        if not openai_api_key and not groq_api_key:
            raise ValueError("No LLM providers configured. Please configure at least one provider.")
        # Ensure providers actually initialized; fail fast with clear message if none
        if not self.providers:
            raise ValueError("No LLM providers initialized successfully. Check your API keys and provider configuration.")
        self.streaming_service = StreamingLLMService(self.providers)

    def _clean(self, val: Optional[str]) -> Optional[str]:
            return val.strip().strip('\'"') if isinstance(val, str) else val

    def _initialize_providers(self):
        """Initialize configured LLM providers."""
        self.providers: Dict[LLMProviderType, Any] = {}

        # Read from pydantic settings (which loads .env), not raw os.environ
        def _clean(val: Optional[str]) -> Optional[str]:
            return val.strip().strip('\'"') if isinstance(val, str) else val

        openai_api_key = _clean(os.getenv('OPENAI_API_KEY'))
        groq_api_key = _clean(os.getenv('GROQ_API_KEY'))

        # Persist cleaned values back to settings
        self.settings.openai_api_key = openai_api_key
        self.settings.groq_api_key = groq_api_key

        # Initialize OpenAI provider if configured
        if openai_api_key:
            try:
                self.providers[LLMProviderType.OPENAI] = LLMProviderFactory.create_provider(
                    LLMProviderType.OPENAI,
                    openai_api_key,
                    os.getenv('OPENAI_MODEL') or "gpt-4"
                )
                logger.info("OpenAI provider initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI provider: {e}")

        # Initialize Groq provider if configured
        if groq_api_key:
            try:    
                self.providers[LLMProviderType.GROQ] = LLMProviderFactory.create_provider(
                    LLMProviderType.GROQ,
                    groq_api_key,
                    os.getenv('GROQ_MODEL') or "meta-llama/llama-4-maverick-17b-128e-instruct"
                )
                logger.info("Groq provider initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Groq provider: {e}")

        if not openai_api_key and not groq_api_key:
            raise ValueError("No LLM providers configured. Please configure at least one provider.")
        # # If API keys were provided but initialization failed, ensure we fail clearly here
        # if not :
        #     raise ValueError("No LLM providers initialized successfully. Check your API keys and provider configuration.")

    def get_preferred_provider(self) -> LLMProviderType:
        """Get the preferred LLM provider."""
        # Try explicit preferred provider from env
        preferred_provider = os.getenv('PREFERRED_PROVIDER')
        if preferred_provider:
            try:
                preferred_enum = LLMProviderType[preferred_provider.upper()]
                if preferred_enum in self.providers:
                    return preferred_enum
                else:
                    logger.warning(f"Preferred provider '{preferred_provider}' not initialized; falling back.")
            except Exception:
                logger.warning(f"Invalid PREFERRED_PROVIDER value: {preferred_provider}; falling back.")

        # Try default LLM provider fallback
        default_llm_provider = os.getenv('DEFAULT_LLM_PROVIDER')
        if default_llm_provider:
            try:
                default_enum = LLMProviderType[default_llm_provider.upper()]
                if default_enum in self.providers:
                    return default_enum
                else:
                    logger.warning(f"Default LLM provider '{default_llm_provider}' not initialized; falling back.")
            except Exception:
                logger.warning(f"Invalid DEFAULT_LLM_PROVIDER value: {default_llm_provider}; falling back.")

        # Fall back to first available provider if any
        if self.providers:
            return next(iter(self.providers.keys()))

        # No providers available
        raise ValueError("No LLM providers are available. Please configure at least one provider.")

    async def generate_contract_from_submission(
        self,
        submission: ContractSubmission
    ) -> GeneratedConfiguration:
        """Generate contract and configuration from a submission."""
        try:
            provider_type = self.get_preferred_provider()
            provider = self.providers[provider_type]

            # Format the prompt based on input type
            if submission.input_type.value == "NATURAL_LANGUAGE":
                prompt = self.prompt_manager.format_prompt(
                    "cadence_contract",
                    requirements=submission.content,
                    pre_conditions=submission.pre_conditions or {},
                    post_conditions=submission.post_conditions or {}
                )
            else:
                # For file inputs, we might need to analyze the content first
                prompt = f"""
                Convert the following {submission.input_type.value} code to a complete Cadence smart contract:

                {submission.content}

                The contract should:
                1. Follow Cadence best practices
                2. Include proper error handling
                3. Be deployable on Flow testnet/mainnet
                4. Include necessary resource definitions and interfaces

                Pre-conditions: {submission.pre_conditions or {}}
                Post-conditions: {submission.post_conditions or {}}
                """

            # Generate the contract code
            response = await provider.generate_contract(prompt)

            # Generate the flow.json configuration
            config_response = await self._generate_configuration(
                provider,
                response.content
            )

            # Create and save the generated configuration
            config_data = self._parse_config_response(config_response.content)

            generated_config = GeneratedConfiguration(
                submission_id=submission.id,
                config_content=config_data,
                generated_contract_code=response.content,
                validation_status="PENDING"
            )

            self.db_session.add(generated_config)
            self.db_session.commit()

            # Log the generation
            logger.info(f"Generated contract for submission {submission.id} using {provider_type.value}")

            return generated_config

        except Exception as e:
            logger.error(f"Contract generation failed for submission {submission.id}: {e}")
            raise RuntimeError(f"Contract generation failed: {e}")

    async def generate_contract_with_external_context(
        self,
        submission: ContractSubmission,
        external_context: Optional[str] = None
    ) -> GeneratedConfiguration:
        """Generate contract and configuration using external markdown context."""
        try:
            provider_type = self.get_preferred_provider()
            provider = self.providers[provider_type]

            prompt = self.prompt_manager.format_prompt(
                "cadence_contract_with_context",
                requirements=submission.content,
                external_context=external_context or "",
                pre_conditions=submission.pre_conditions or {},
                post_conditions=submission.post_conditions or {}
            )

            # Generate the contract code
            response = await provider.generate_contract(prompt)

            # Generate the flow.json configuration
            config_response = await self._generate_configuration(
                provider,
                response.content
            )

            # Create and save the generated configuration
            config_data = self._parse_config_response(config_response.content)

            generated_config = GeneratedConfiguration(
                submission_id=submission.id,
                config_content=config_data,
                generated_contract_code=response.content,
                validation_status="PENDING"
            )

            self.db_session.add(generated_config)
            self.db_session.commit()

            # Log the generation
            logger.info(
                f"Generated contract (with external context) for submission {submission.id} using {provider_type.value}"
            )

            return generated_config
        except Exception as e:
            logger.error(f"Context-based contract generation failed for submission {submission.id}: {e}")
            raise RuntimeError(f"Context-based contract generation failed: {e}")

    async def generate_contract_with_external_context_streaming(
        self,
        submission: ContractSubmission,
        external_context: Optional[str] = None,
        progress_tracker: Optional[StreamingProgressTracker] = None
    ) -> AsyncGenerator[str, None]:
        """Generate contract with external context using streaming."""
        try:
            provider_type = self.get_preferred_provider()
            
            prompt = self.prompt_manager.format_prompt(
                "cadence_contract_with_context",
                requirements=submission.content,
                external_context=external_context or "",
                pre_conditions=submission.pre_conditions or {},
                post_conditions=submission.post_conditions or {}
            )
            
            # Update progress for contract generation phase
            if progress_tracker:
                progress_tracker.update_phase("generating_contract", 0.0)
            
            # Stream the contract generation
            contract_content = ""
            async for chunk in self.streaming_service.generate_contract_with_streaming(
                provider_type=provider_type,
                prompt=prompt,
                progress_tracker=progress_tracker
            ):
                contract_content += chunk
                yield chunk
            
            # Update progress for configuration generation
            if progress_tracker:
                progress_tracker.update_phase("generating_config", 0.0)
            
            # Generate configuration (non-streaming for now)
            config_response = await self._generate_configuration(
                self.providers[provider_type],
                contract_content
            )
            
            # Create and save the generated configuration
            config_data = self._parse_config_response(config_response.content)
            
            generated_config = GeneratedConfiguration(
                submission_id=submission.id,
                config_content=config_data,
                generated_contract_code=contract_content,
                validation_status="PENDING"
            )
            
            self.db_session.add(generated_config)
            self.db_session.commit()
            
            logger.info(
                f"Generated contract (with external context and streaming) for submission {submission.id} using {provider_type.value}"
            )
            
            # Yield configuration as final chunk
            yield f"\n\n<!-- CONFIG_START -->{config_response.content}<!-- CONFIG_END -->\n"
            
        except Exception as e:
            logger.error(f"Streaming context-based contract generation failed for submission {submission.id}: {e}")
            raise RuntimeError(f"Streaming context-based contract generation failed: {e}")

    async def _generate_configuration(
        self,
        provider: Any,
        contract_code: str
    ) -> LLMResponse:
        """Generate flow.json configuration from contract code."""
        prompt = self.prompt_manager.format_prompt(
            "flow_config",
            contract_code=contract_code
        )

        return await provider.generate_contract(prompt)

    def _parse_config_response(self, config_content: str) -> Dict[str, Any]:
        """Parse the configuration response into JSON."""
        try:
            import json
            # Try to extract JSON from the response
            start_idx = config_content.find("{")
            end_idx = config_content.rfind("}")

            if start_idx != -1 and end_idx != -1:
                json_str = config_content[start_idx:end_idx + 1]
                return json.loads(json_str)
            else:
                # Fallback: create basic configuration structure
                return {
                    "contracts": {},
                    "networks": {},
                    "accounts": {}
                }
        except Exception as e:
            logger.error(f"Failed to parse configuration response: {e}")
            return {
                "contracts": {},
                "networks": {},
                "accounts": {}
            }

    async def analyze_deployment_logs(
        self,
        deployment_log: DeploymentLog
    ) -> List[LearningFeedbackLoop]:
        """Analyze deployment logs for learning patterns."""
        try:
            provider = self.providers[self.get_preferred_provider()]

            # Get the contract code from the submission
            contract_code = deployment_log.contract_submission.content
            if deployment_log.generated_configuration:
                contract_code = deployment_log.generated_configuration.generated_contract_code

            prompt = self.prompt_manager.format_prompt(
                "log_analysis",
                contract_code=contract_code,
                logs=deployment_log.log_content
            )

            response = await provider.analyze_deployment_logs(
                deployment_log.log_content,
                contract_code
            )

            # Parse the analysis results and create learning feedback entries
            feedback_entries = self._parse_analysis_response(
                response,
                deployment_log
            )

            for entry in feedback_entries:
                self.db_session.add(entry)

            self.db_session.commit()

            logger.info(f"Analyzed deployment logs for deployment {deployment_log.id}")

            return feedback_entries

        except Exception as e:
            logger.error(f"Log analysis failed for deployment {deployment_log.id}: {e}")
            return []

    def _parse_analysis_response(
        self,
        response: LLMResponse,
        deployment_log: DeploymentLog
    ) -> List[LearningFeedbackLoop]:
        """Parse analysis response into learning feedback entries."""
        feedback_entries = []

        try:
            import json
            # Try to parse JSON from the response
            start_idx = response.content.find("{")
            end_idx = response.content.rfind("}")

            if start_idx != -1 and end_idx != -1:
                json_str = response.content[start_idx:end_idx + 1]
                analysis_data = json.loads(json_str)

                # Create feedback entries based on patterns found
                if "error_patterns" in analysis_data:
                    for pattern in analysis_data["error_patterns"]:
                        entry = LearningFeedbackLoop(
                            submission_id=deployment_log.submission_id,
                            log_id=deployment_log.id,
                            pattern_type=PatternType.ERROR_PATTERN,
                            insights=pattern,
                            confidence_score=pattern.get("confidence", 0.7)
                        )
                        feedback_entries.append(entry)

                if "success_patterns" in analysis_data:
                    for pattern in analysis_data["success_patterns"]:
                        entry = LearningFeedbackLoop(
                            submission_id=deployment_log.submission_id,
                            log_id=deployment_log.id,
                            pattern_type=PatternType.SUCCESS_PATTERN,
                            insights=pattern,
                            confidence_score=pattern.get("confidence", 0.7)
                        )
                        feedback_entries.append(entry)

                if "optimization_opportunities" in analysis_data:
                    for pattern in analysis_data["optimization_opportunities"]:
                        entry = LearningFeedbackLoop(
                            submission_id=deployment_log.submission_id,
                            log_id=deployment_log.id,
                            pattern_type=PatternType.OPTIMIZATION_OPPORTUNITY,
                            insights=pattern,
                            confidence_score=pattern.get("confidence", 0.7)
                        )
                        feedback_entries.append(entry)

        except Exception as e:
            logger.error(f"Failed to parse analysis response: {e}")

            # Create a fallback feedback entry
            entry = LearningFeedbackLoop(
                submission_id=deployment_log.submission_id,
                log_id=deployment_log.id,
                pattern_type=PatternType.ERROR_PATTERN,
                insights={"raw_analysis": response.content},
                confidence_score=0.5
            )
            feedback_entries.append(entry)

        return feedback_entries

    async def validate_configuration(
        self,
        generated_config: GeneratedConfiguration
    ) -> bool:
        """Validate a generated configuration."""
        try:
            provider = self.providers[self.get_preferred_provider()]

            response = await provider.validate_configuration(
                generated_config.config_content,
                generated_config.generated_contract_code
            )

            # Parse validation results
            validation_results = self._parse_validation_response(response.content)

            # Update the configuration with validation results
            generated_config.validation_status = (
                "VALID" if validation_results.get("valid", False) else "INVALID"
            )
            generated_config.validation_errors = validation_results.get("errors", [])

            self.db_session.commit()

            return generated_config.validation_status == "VALID"

        except Exception as e:
            logger.error(f"Configuration validation failed for config {generated_config.id}: {e}")
            return False

    def _parse_validation_response(self, validation_content: str) -> Dict[str, Any]:
        """Parse validation response into structured data."""
        try:
            import json
            # Try to parse JSON from the response
            start_idx = validation_content.find("{")
            end_idx = validation_content.rfind("}")

            if start_idx != -1 and end_idx != -1:
                json_str = validation_content[start_idx:end_idx + 1]
                return json.loads(json_str)
            else:
                return {"valid": False, "errors": ["Validation response could not be parsed"]}
        except Exception as e:
            logger.error(f"Failed to parse validation response: {e}")
            return {"valid": False, "errors": [str(e)]}