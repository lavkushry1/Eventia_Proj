# Eventia Debugging & Performance Monitoring Guide

This guide explains the debugging, logging, and performance monitoring tools integrated into the Eventia project. These tools help identify bugs, track performance issues, and ensure the reliability of the application.

## 1. Structured Logging

The backend uses structured JSON logging to capture important information in a consistent format:

```python
from utils.logger import logger

# Simple logging
logger.info("User logged in", user_id="123")

# With correlation ID (for tracing requests across services)
logger.info("Payment processed", correlation_id="abc-123", amount=1000)
```

### Correlation IDs

Correlation IDs track requests across the system:

- Generated automatically for each request
- Passed from frontend to backend in X-Correlation-ID header
- Included in all logs for a request
- Returned in error responses

## 2. Performance Metrics

The `/metrics` endpoint provides Prometheus-compatible metrics:

- Response times for all endpoints (min, max, avg, p95)
- Request counts and error rates
- Function execution times

Access the metrics at: `http://localhost:0/metrics`

## 3. Health Checks

The `/health` endpoint provides application health information:

- Overall status (healthy/unhealthy)
- Database connection status and latency
- Memory usage statistics

Access the health check at: `http://localhost:3000/health`

## 4. Memory Profiling

Critical endpoints are monitored for memory usage:

```python
from utils.memory_profiler import profile_memory

@profile_memory
def my_function():
    # Function execution is monitored for memory usage
    pass
```

Memory usage warnings appear in logs if memory consumption is high.

## 5. Load Testing

A Locust configuration is included for load testing:

```bash
# Run load test against local server with 1000 users
cd eventia-backend
python -m locust -f tests/locustfile.py --host=http://localhost:3000 --users=1000 --spawn-rate=10
```

For headless mode:

```bash
python -m locust -f tests/locustfile.py --host=http://localhost:3000 --users=1000 --spawn-rate=10 --run-time=5m --headless --html=locust-report.html
```

## 6. End-to-End Testing

Playwright tests check the full user journey:

```bash
# Install Playwright dependencies
cd eventia-ticketing-flow
npm install -D @playwright/test
npx playwright install

# Run tests
npx playwright test tests/e2e.js
```

The tests generate screenshots for any failures in `tests/screenshots/`.

## 7. Cross-Browser Testing

The Playwright configuration tests across multiple browsers:

```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
npx playwright test --project=mobile-chrome
npx playwright test --project=mobile-safari
```

## 8. CI/CD Integration

The GitHub Actions workflow runs all tests automatically:

- Pytest for backend code
- Vitest/RTL for frontend components
- Locust for load testing
- Playwright for end-to-end tests

## 9. Debugging Tips

### Backend Issues

1. Check logs for correlation IDs:
   ```
   grep "correlation_id" flask_server.log
   ```

2. Check memory usage:
   ```
   curl http://localhost:3000/health | jq .memory
   ```

3. Check slow endpoints:
   ```
   curl http://localhost:3000/metrics | grep "api_endpoint_response_time_ms"
   ```

### Frontend Issues

1. Enable debug logging in the browser console:
   ```javascript
   localStorage.setItem('debug', 'eventia:*');
   ```

2. Use the React Developer Tools to inspect component renders and state

## 10. Alerting

The CI pipeline sends Slack alerts on test failures. For local development, the memory profiler logs warnings when memory usage is high. 