from typing import Any, Dict, List, Tuple

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_INSUFFICIENT_CONTEXT_MSG = (
    "The available documents do not contain enough information "
    "to answer this question confidently."
)

_SYSTEM_PROMPT = """You are a precise document assistant. Answer the user's question
using ONLY the context passages provided below. Do not use any prior knowledge.

Rules:
- If the context does not contain enough information, say exactly:
  "The available documents do not contain enough information to answer this question confidently."
- Never invent facts, citations, or statistics.
- Be concise and direct.
- Cite the source document and page number when possible.

Context:
{context}"""


class GeneratorService:
    """
    Generates answers from retrieved chunks.

    Modes:
        llm_generated   — calls an OpenAI-compatible API using retrieved context as prompt.
        retrieval_only  — assembles the top-chunk texts as the answer; no LLM needed.

    The fallback mode (retrieval_only) is always available without an API key.
    """

    def generate(
        self,
        question: str,
        chunks: List[Dict[str, Any]],
    ) -> Tuple[str, float, str]:
        """
        Generate an answer for the question given the retrieved chunks.

        Returns:
            answer (str): the generated or assembled answer
            confidence (float): 0–1 score based on top retrieval similarity
            mode (str): 'llm_generated' or 'retrieval_only'
        """
        if not chunks:
            return _INSUFFICIENT_CONTEXT_MSG, 0.0, "retrieval_only"

        top_score = chunks[0]["score"] if chunks else 0.0

        if settings.llm_enabled:
            answer, mode = self._llm_generate(question, chunks)
        else:
            answer, mode = self._retrieval_only(chunks)

        # Confidence is anchored to the top retrieval score
        confidence = round(min(top_score, 1.0), 4)
        return answer, confidence, mode

    def _retrieval_only(self, chunks: List[Dict[str, Any]]) -> Tuple[str, str]:
        """Assemble the top-k chunks into a readable answer without an LLM."""
        lines = []
        for i, chunk in enumerate(chunks[:3], start=1):
            meta = chunk.get("metadata", {})
            source = f"{meta.get('filename', 'Unknown')} (page {meta.get('page_number', '?')})"
            lines.append(f"[Source {i}: {source}]\n{chunk['text']}")

        answer = "\n\n".join(lines)
        logger.info("Retrieval-only response assembled.", chunk_count=len(chunks))
        return answer, "retrieval_only"

    def _llm_generate(
        self,
        question: str,
        chunks: List[Dict[str, Any]],
    ) -> Tuple[str, str]:
        """Call an OpenAI-compatible LLM with the retrieved context."""
        try:
            from openai import OpenAI

            context_parts = []
            for chunk in chunks:
                meta = chunk.get("metadata", {})
                header = (
                    f"[{meta.get('filename', 'doc')} | "
                    f"page {meta.get('page_number', '?')}]"
                )
                context_parts.append(f"{header}\n{chunk['text']}")

            context = "\n\n---\n\n".join(context_parts)
            system_message = _SYSTEM_PROMPT.format(context=context)

            client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
            )

            response = client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": question},
                ],
                max_tokens=settings.LLM_MAX_TOKENS,
                temperature=settings.LLM_TEMPERATURE,
            )

            answer = response.choices[0].message.content or _INSUFFICIENT_CONTEXT_MSG
            logger.info("LLM generation complete.", model=settings.LLM_MODEL)
            return answer, "llm_generated"

        except Exception as e:
            logger.error("LLM generation failed; falling back to retrieval-only.", error=str(e))
            return self._retrieval_only(chunks)


generator_service = GeneratorService()
