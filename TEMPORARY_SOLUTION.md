# Temporary Solution for Eventia Project

Since you're experiencing SSL and package installation issues, here's a temporary solution to get your frontend working with mock data.

## Option 1: Use the Mock API in the Frontend

We've modified `eventia-ticketing-flow/src/lib/api.ts` to use mock data instead of making actual API calls. This should allow your frontend to display the events page without any backend running.

1. Start your frontend server as usual:
   ```bash
   cd eventia-ticketing-flow
   npm run dev
   ```

2. Navigate to http://localhost:8080/events in your browser

## Option 2: Run the Simple API Server

We've created a simple API server that doesn't require additional packages:

1. Run the simple API server:
   ```bash
   python simple_api_server.py
   ```

2. The server will start on port 8000 and serve:
   - API endpoints at http://localhost:8000/api/v1/
   - Static files at http://localhost:8000/static/

3. You need to update the frontend API URL to use this server:
   ```
   // In eventia-ticketing-flow/src/lib/api.ts
   export const api = axios.create({
     baseURL: 'http://localhost:8000/api/v1',
     headers: {
       'Content-Type': 'application/json',
     },
   });
   ```

## Fixing the React Router Warnings

The React Router warnings are just informational about future changes in v7 and can be ignored for now. If you want to suppress them, you can add future flags to your Router configuration:

```jsx
import { 
  createBrowserRouter, 
  RouterProvider,
  createRoutesFromElements,
  Route
} from 'react-router-dom';
import { UNSTABLE_useBlocker } from 'react-router-dom';

const router = createBrowserRouter(
  createRoutesFromElements(
    // Your routes
  ),
  {
    future: {
      v7_startTransition: true,
      v7_relativeSplatPath: true
    }
  }
);
```

## Long-term Solution

To properly fix the issues:

1. **Fix SSL for Python**: 
   - Reinstall Python with SSL support
   - Or use a Python distribution like Anaconda that includes SSL

2. **Install Dependencies**:
   ```bash
   pip install fastapi uvicorn pymongo motor pydantic
   ```

3. **Set up Local MongoDB**:
   - Install MongoDB Community Edition
   - Start the MongoDB service

4. **Run the Full Backend**:
   ```bash
   cd eventia-backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ``` 