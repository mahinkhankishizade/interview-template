from abc import ABC, abstractmethod
from enum import Enum


class LLMType(str, Enum):
    """Which mock LLM to use for a response."""

    A = "A"
    B = "B"


class LLMService(ABC):
    """Common interface for the mock LLM backends. Each one takes an input
    query string and returns a canned response, so the rest of the app can
    treat them interchangeably."""

    @abstractmethod
    def respond(self, query: str) -> str:
        ...


class LLMServiceA(LLMService):
    def respond(self, query: str) -> str:
        return "hi, we are checking your query"


class LLMServiceB(LLMService):
    def respond(self, query: str) -> str:
        return "hi, please provide your fullname"


# Ready-to-use singletons: the mocks are stateless, so one instance each is
# enough to share across the app.
llm_a = LLMServiceA()
llm_b = LLMServiceB()

_REGISTRY: dict[LLMType, LLMService] = {
    LLMType.A: llm_a,
    LLMType.B: llm_b,
}


def get_llm(llm_type: LLMType) -> LLMService:
    """Resolve an LLMType to its backing service."""
    return _REGISTRY[llm_type]
