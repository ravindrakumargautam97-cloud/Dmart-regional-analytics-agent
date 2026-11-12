
import time


def run_with_retry(operation, max_attempts=3, delay=0):
    """Retry an operation after temporary failures."""
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    for attempt in range(1, max_attempts + 1):
        try:
            data = operation()
            return {
                "success": True,
                "data": data,
                "attempts": attempt,
                "error": None,
            }
        except (ConnectionError, TimeoutError) as exc:
            if attempt == max_attempts:
                return {
                    "success": False,
                    "data": None,
                    "attempts": attempt,
                    "error": str(exc),
                }

            if delay > 0:
                time.sleep(delay)
