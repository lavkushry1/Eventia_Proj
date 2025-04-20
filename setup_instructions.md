# Eventia Project Setup Instructions

## Fixing Database Connection and API Issues

Follow these steps to fix the "500 Internal Server Error" when accessing `/events`:

### Step 1: Install MongoDB Locally

1. Download and install MongoDB Community Edition from https://www.mongodb.com/try/download/community
2. Start the MongoDB service:
   - **Mac**: `brew services start mongodb-community`
   - **Windows**: MongoDB should run as a service after installation
   - **Linux**: `sudo systemctl start mongod`

### Step 2: Run the Database Initialization Script

```bash
# Navigate to project root
cd /Users/lavkushkumar/Desktop/untitled\ folder/Eventia_Proj

# Run the database initialization script
python db_init.py
```

### Step 3: Start the Backend Server

```bash
# Navigate to the backend directory
cd eventia-backend

# Start the server on port 8000
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Start the Frontend Server

```bash
# In a new terminal, navigate to the frontend directory
cd /Users/lavkushkumar/Desktop/untitled\ folder/Eventia_Proj/eventia-ticketing-flow

# Install dependencies if needed
npm install

# Start the development server
npm run dev
```

## Troubleshooting

If you still see the "500 Internal Server Error":

1. **Check MongoDB Connection**:
   - Ensure MongoDB is running: `mongo` or `mongosh` should connect
   - Check logs for MongoDB connection errors

2. **Check Server Logs**:
   - Look for errors in the FastAPI server logs
   - Connection issues will be visible in the terminal where the server is running

3. **API Configuration**:
   - We've updated the API URLs to use port 8000 instead of 3000
   - Make sure the frontend is pointing to the correct backend URL

4. **CORS Issues**:
   - We've updated the CORS settings to allow `localhost:8080`
   - If you're accessing from a different port, update the CORS settings

5. **SSL Issues**:
   - We're now using a local MongoDB instance to avoid SSL problems
   - If you need to use the remote DB, you'll need to fix the SSL configuration

## React Router Warnings

The React Router warnings you're seeing are just informational about future changes in v7 and can be ignored for now:

```
⚠️ React Router Future Flag Warning: React Router will begin wrapping state updates in `React.startTransition` in v7...
⚠️ React Router Future Flag Warning: Relative route resolution within Splat routes is changing in v7...
```

You can suppress these by adding future flags to your Router configuration if desired. 