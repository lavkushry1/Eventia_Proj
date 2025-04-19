# How to Run Frontend and Backend

## Prerequisites
- Python 3.8+ (for backend)
- Node.js 14+ and npm/yarn (for frontend)
- MongoDB (running locally or accessible via connection string)

## Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd eventia-backend
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (create a `.env` file in the `eventia-backend` directory):
   ```
   # Required MongoDB Configuration
   MONGODB_URL=mongodb://localhost:27017
   MONGODB_DB=eventia
   
   # API Configuration
   SECRET_KEY=your_secret_key
   CORS_ORIGINS=http://localhost:3000
   
   # Payment Configuration (optional)
   PAYMENT_VPA=eventia@axis
   DEFAULT_MERCHANT_NAME=Eventia Ticketing
   DEFAULT_VPA=eventia@axis
   MERCHANT_NAME=Eventia Ticketing
   VPA_ADDRESS=eventia@axis
   ```

5. Run the backend server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

   The backend API will be available at http://localhost:8000
