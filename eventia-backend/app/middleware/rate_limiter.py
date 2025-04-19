from typing import List
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import time


class RateLimiter(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        rate_limit: int,
        time_window: int,
        exempted_routes: List[str],
        exempted_ips: List[str],
    ):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.exempted_routes = exempted_routes
        self.exempted_ips = exempted_ips
        self.request_counts = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        route_path = request.url.path

        if client_ip in self.exempted_ips or route_path in self.exempted_routes:
            return await call_next(request)

        current_time = time.time()
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []

        self.request_counts[client_ip] = [
            req_time
            for req_time in self.request_counts[client_ip]
            if current_time - req_time < self.time_window
        ]

        if len(self.request_counts[client_ip]) >= self.rate_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )

        self.request_counts[client_ip].append(current_time)
        return await call_next(request)