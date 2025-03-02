from functools import wraps
from typing import Callable, List

from fastapi import HTTPException, Request


def require_query_params(*required_params: List[str]):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            query_params = dict(request.query_params)
            missing_params = [
                param for param in required_params if param not in query_params
            ]
            if missing_params:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Missing required query parameters",
                        "missing_params": missing_params,
                    },
                )
            return await func(request, *args, **kwargs)

        return wrapper

    return decorator
