import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from groq import APIStatusError, NotFoundError
import logging
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import GenerationChunk, ChatResult, ChatGenerationChunk
from typing import Any, List, Optional, Iterator, AsyncIterator
from langchain_core.messages import BaseMessage
from langchain_core.callbacks import CallbackManagerForLLMRun

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GroqModelRotator(BaseChatModel):
    models: list[str]
    temperature: float = 0.7
    api_key: str = os.getenv("GROQ_API_KEY")
    current_model_index: int = 0

    @property
    def model_name(self) -> str:
        return self.models[self.current_model_index]

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        max_retries = len(self.models)
        for attempt in range(max_retries):
            try:
                llm = self._get_llm()
                # The actual call to the underlying ChatGroq model
                response = llm._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
                return response
            except (APIStatusError, NotFoundError) as e:
                if isinstance(e, NotFoundError) or (isinstance(e, APIStatusError) and e.status_code == 429):
                    logger.warning(f"API error with model: {self.models[self.current_model_index]}. Rotating. Error: {e}")
                    self._rotate_model()
                    if attempt == max_retries - 1:
                        logger.error("All models failed. Raising exception.")
                        raise e
                else:
                    raise e # Re-raise other API errors
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")
                raise e
        raise Exception("Should not reach here")


    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        max_retries = len(self.models)
        for attempt in range(max_retries):
            try:
                llm = self._get_llm()
                # The actual call to the underlying ChatGroq model stream
                for chunk in llm._stream(messages, stop=stop, run_manager=run_manager, **kwargs):
                    yield chunk
                return # If stream is successful, exit the loop
            except (APIStatusError, NotFoundError) as e:
                if isinstance(e, NotFoundError) or (isinstance(e, APIStatusError) and e.status_code == 429):
                    logger.warning(f"API error with model: {self.models[self.current_model_index]}. Rotating. Error: {e}")
                    self._rotate_model()
                    if attempt == max_retries - 1:
                        logger.error("All models failed. Raising exception.")
                        raise e
                else:
                    raise e # Re-raise other API errors
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")
                raise e
        raise Exception("Should not reach here")

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        max_retries = len(self.models)
        for attempt in range(max_retries):
            try:
                llm = self._get_llm()
                # The actual call to the underlying ChatGroq model
                response = await llm._agenerate(messages, stop=stop, run_manager=run_manager, **kwargs)
                return response
            except (APIStatusError, NotFoundError) as e:
                if isinstance(e, NotFoundError) or (isinstance(e, APIStatusError) and e.status_code == 429):
                    logger.warning(f"API error with model: {self.models[self.current_model_index]}. Rotating. Error: {e}")
                    self._rotate_model()
                    if attempt == max_retries - 1:
                        logger.error("All models failed. Raising exception.")
                        raise e
                else:
                    raise e # Re-raise other API errors
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")
                raise e
        raise Exception("Should not reach here")

    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        max_retries = len(self.models)
        for attempt in range(max_retries):
            try:
                llm = self._get_llm()
                # The actual call to the underlying ChatGroq model async stream
                async for chunk in llm._astream(messages, stop=stop, run_manager=run_manager, **kwargs):
                    yield chunk
                return # If stream is successful, exit the loop
            except (APIStatusError, NotFoundError) as e:
                if isinstance(e, NotFoundError) or (isinstance(e, APIStatusError) and e.status_code == 429):
                    logger.warning(f"API error with model: {self.models[self.current_model_index]}. Rotating. Error: {e}")
                    self._rotate_model()
                    if attempt == max_retries - 1:
                        logger.error("All models failed. Raising exception.")
                        raise e
                else:
                    raise e # Re-raise other API errors
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")
                raise e
        raise Exception("Should not reach here")

    def _get_llm(self) -> ChatGroq:
        model_name = self.models[self.current_model_index]
        return ChatGroq(
            model=model_name,
            temperature=self.temperature,
            api_key=self.api_key
        )

    def _rotate_model(self):
        self.current_model_index = (self.current_model_index + 1) % len(self.models)
        logger.info(f"Rotated to model: {self.models[self.current_model_index]}")

    @property
    def _llm_type(self) -> str:
        return "groq_model_rotator"
