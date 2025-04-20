# Eventia Ticketing Platform - Deployment Guide

This guide provides instructions for deploying the Eventia Ticketing Platform in both development and production environments.

## Prerequisites

- Docker and Docker Compose
- Git
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- MongoDB 6.0+ (for local development)

## Development Deployment

### Option 1: Using Docker Compose

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/eventia-ticketing-platform.git
   cd eventia-ticketing-platform
   ```

2. Start the development environment:
   ```bash
   docker-compose -f docker-compose.dev.yml up
   ```

3. Access the application:
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:3000/api
   - MongoDB: mongodb://localhost:27017/eventia

### Option 2: Manual Setup

#### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd eventia-backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start MongoDB:
   ```bash
   # Using Docker
   docker run -d -p 27017:27017 --name mongodb mongo:6.0
   ```

5. Run the backend server:
   ```bash
   python flask_server.py
   ```

#### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd eventia-ticketing-flow
   ```

2. Install dependencies:
   ```bash
   yarn install
   ```

3. Start the development server:
   ```bash
   yarn dev
   ```

## Production Deployment

### Using Docker Compose

1. Create a `.env.prod` file with appropriate settings:
   ```
   ADMIN_TOKEN=your_secure_token_here
   MONGO_URI=mongodb://mongodb:27017/eventia
   ```

2. Build and start the production containers:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. The application will be accessible at:
   - Frontend: http://localhost (port 80)
   - Backend API: http://localhost/api (proxied through Nginx)
   - Admin UI: http://localhost/admin-ui/ (protected with basic auth)

### Using Docker Swarm (for High Availability)

1. Initialize a Docker Swarm:
   ```bash
   docker swarm init
   ```

2. Deploy the stack:
   ```bash
   docker stack deploy -c docker-compose.prod.yml eventia
   ```

3. Scale services as needed:
   ```bash
   docker service scale eventia_backend=3 eventia_frontend=2
   ```

## Environment Variables

### Backend (.env.prod)

| Variable | Description | Default |
|----------|-------------|---------|
| ADMIN_TOKEN | Token for admin authentication | supersecuretoken123 |
| PORT | Backend server port | 3000 |
| FLASK_ENV | Environment (development/production) | production |
| MONGO_URI | MongoDB connection string | mongodb://mongodb:27017/eventia |

### Frontend (.env.production)

| Variable | Description | Default |
|----------|-------------|---------|
| NODE_ENV | Node environment | production |
| VITE_API_URL | Backend API URL | https://api.eventia.com/api |

## SSL Setup

For production environments, configure SSL certificates:

1. Get SSL certificates (Let's Encrypt recommended)
2. Update the Nginx configuration in `docker-compose.prod.yml`
3. Add volume mappings for SSL certificates

## Database Backups

Set up regular MongoDB backups:

```bash
# Add to crontab
0 2 * * * docker exec eventia-mongodb-prod mongodump --out /backup/$(date +%Y-%m-%d)
```

## Monitoring

- Use Prometheus and Grafana for monitoring
- Set up log aggregation with ELK stack or similar
- Configure health checks for all services

## Troubleshooting

- Check logs: `docker-compose -f docker-compose.prod.yml logs -f [service]`
- Verify network connectivity between containers
- Test API endpoints directly using curl or Postman
- Check MongoDB connection and data integrity 

## Project Structure

```
eventia/
├── backend/                # Flask/FastAPI backend
│   ├── app/
│   │   ├── routers/        # Route definitions
│   │   │   ├── models/         # Data models
│   │   │   ├── schemas/        # Pydantic schemas
│   │   │   ├── utils/          # Helpers and utilities
│   │   │   └── config.py       # Configuration management
│   │   ├── .env                # Environment variables
│   │   └── main.py             # Application entry point
│   ├── frontend/               # React frontend
│   │   ├── src/
│   │   │   ├── components/     # UI components
│   │   │   │   ├── atomic/     # Atomic/base components
│   │   │   │   ├── molecules/  # Compound components
│   │   │   │   └── organisms/  # Complex components
│   │   │   ├── pages/          # Page components
│   │   │   ├── lib/            # Utilities, hooks, etc.
│   │   │   ├── config/         # Config management
│   │   │   └── mock/           # Mock data
│   │   └── .env                # Frontend environment variables
│   ├── docker/                 # Docker configuration
│   └── nginx/                  # Nginx configuration
└── scripts/                # Deployment scripts 
```

# backend/app/config.py
import os
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    # Core settings
    ENV: str = Field("development", env="FLASK_ENV")
    DEBUG: bool = Field(True, env="DEBUG")
    
    # API settings
    API_PREFIX: str = "/api"
    
    # MongoDB settings
    MONGO_URI: str = Field("mongodb://localhost:27017/eventia", env="MONGO_URI")
    
    # Authentication
    SECRET_KEY: str = Field("supersecuretoken123", env="SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 3600  # 1 hour
    
    # Payment settings
    DEFAULT_PAYMENT_VPA: str = "eventia@upi"
    
    class Config:
        env_file = ".env"
        
settings = Settings()

# backend/app/utils/auth.py
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_jwt_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None