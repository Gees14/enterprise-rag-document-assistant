from fastapi import APIRouter, HTTPException

from app.core.logging import get_logger
from app.schemas.evaluation import EvalRunResponse
from app.services.evaluator import run_evaluation

router = APIRouter(prefix="/eval", tags=["evaluation"])
logger = get_logger(__name__)


@router.post("/run", response_model=EvalRunResponse)
async def run_eval(top_k: int = 5) -> EvalRunResponse:
    """
    Run RAG evaluation against the predefined question set in data/eval/questions.json.

    Metrics returned:
        - precision@k
        - recall@k
        - mean reciprocal rank (MRR)
        - average keyword coverage
        - average retrieval latency (ms)
    """
    try:
        result = run_evaluation(top_k=top_k)
        logger.info(
            "Evaluation complete.",
            questions=result.metrics.total_questions,
            mrr=result.metrics.mean_reciprocal_rank,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Evaluation failed.", error=str(e))
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {e}")
