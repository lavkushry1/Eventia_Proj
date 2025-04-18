# Eventia Error Handling Guide

This document outlines the error handling approach used throughout the Eventia application.

## Backend Error Handling

### API Endpoints

All API endpoints follow these error handling practices:

1. **Specific HTTP Status Codes**:
   - 400: Bad request (client error, invalid input)
   - 401: Unauthorized (missing or invalid authentication)
   - 403: Forbidden (authenticated but insufficient permissions)
   - 404: Not found (resource doesn't exist)
   - 500: Internal server error (unexpected server issues)

2. **Structured Error Responses**:
   ```json
   {
     "detail": "Human-readable error message",
     "code": "ERROR_CODE",
     "params": {}
   }
   ```

3. **Comprehensive Logging**: All errors are logged with context for debugging.

## Frontend Error Handling

### API Client

The frontend API client (`src/lib/api.ts`) handles errors by:

1. Logging errors to console with request context
2. Transforming errors into user-friendly messages
3. Handling authentication errors globally
4. Maintaining correlation IDs for tracing

### Error Boundary

React Error Boundary (`src/components/ErrorBoundary.tsx`) catches unhandled
errors in the component tree and:

1. Displays a user-friendly fallback UI
2. Provides error details in development
3. Offers recovery options
4. Logs error with context information

### Form Validation

Form validation uses Zod schemas to validate inputs before submission.

## Debugging Tips

1. Check browser console for detailed error logs
2. Look for correlation IDs in both frontend and backend logs
3. Enable debug mode with `localStorage.setItem('debug', 'eventia:*')`
4. Review server logs for detailed backend errors

## Error Reporting

Critical errors are automatically reported to administrators via:

1. Server-side logging
2. Error monitoring in the admin dashboard
3. Correlation IDs for cross-referencing issues
