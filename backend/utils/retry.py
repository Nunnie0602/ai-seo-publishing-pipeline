import logging
import time
from collections.abc import Callable
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


def with_retry(
    fn: Callable[[], T],
    *,
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    label: str = "operation",
    retry_on: Callable[[Exception], bool] | None = None,
) -> T:
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except Exception as exc:
            last_error = exc
            if retry_on is not None and not retry_on(exc):
                logger.warning(
                    "[WARN] %s failed (non-retryable): %s",
                    label,
                    exc,
                )
                raise
            logger.warning(
                "[WARN] %s failed (attempt %s/%s): %s",
                label,
                attempt,
                max_attempts,
                exc,
            )
            if attempt < max_attempts:
                time.sleep(delay_seconds * attempt)
    raise last_error  # type: ignore[misc]
