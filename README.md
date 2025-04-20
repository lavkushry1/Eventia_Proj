# 🎟️ Eventia – Future-Proof IPL Ticketing & Event Management System  

A mobile-native, future-ready platform for booking IPL match and event tickets. Built with a separate **React frontend** and **FastAPI + MongoDB backend**. Supports **ticket booking without login**, **QR-based payments**, and **home delivery in 2 days**. Fully managed via an **admin dashboard** with no OTP hassles.

---

## 📁 Project Structure  

```bash
eventia/
├── eventia-gather-spot/  # Frontend (React + TS + Tailwind + shadcn/ui)
├── eventia-backend/      # Backend (FastAPI + MongoDB)
└── README.md             # You're here!
```

---

## 🚀 Key Features  

### 🎫 User-Side (No Login Needed)  
- Browse events & IPL matches with gesture-based navigation  
- **One-Click Payment Popup** for seamless transactions  
- QR-based payment with UTR submission  
- Ticket delivery to user's home in 2 days  
- AR venue preview before booking  

### 🧠 Admin-Side  
- Add / Update / Delete events  
- Update custom UPI VPA  
- Manage UTRs & dispatch tickets  
- Admin login via secure token (no OTP)  
- **Real-Time Analytics Dashboard** to monitor bookings, revenue, and user activity  

---

## 🌐 Frontend – eventia-gather-spot  

### 🛠 Tech Stack  
- React + TypeScript  
- Tailwind CSS for styling  
- shadcn/ui for components  
- Framer Motion for dynamic animations & transitions  
- React Router for navigation  
- TanStack Query for API calls  
- date-fns for formatting  
- lucide-react for icons  
- React Spring for fluid animations & microinteractions  
- Chakra UI for accessible components  
- Chart.js or Recharts for data visualization  

### 🧩 New Admin Analytics Dashboard Components  

#### Analytics Overview Page  
1. **Bookings Summary:** Total bookings, successful payments, and pending UTRs.  
2. **Revenue Insights:** Daily, weekly, and monthly revenue trends.  
3. **Event Performance:** Most popular events based on ticket sales.  

#### Data Visualizations:  
Use interactive charts and graphs to display analytics:  
```tsx
import { BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';

const data = [
  { name: 'Event A', ticketsSold: 120 },
  { name: 'Event B', ticketsSold: 80 },
  { name: 'Event C', ticketsSold: 150 },
];
```

#### Real-Time Updates:  
Use WebSocket integration to update analytics in real-time as new bookings occur.

---

## 📦 Updated Setup Instructions  

### Frontend  

```bash
cd eventia-gather-spot
npm install
npm run dev
```

Frontend runs at 👉 [http://localhost:3000](http://localhost:3000)  

---

### Backend  

```bash
cd eventia-backend
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at 👉 [http://localhost:8000](http://localhost:8000)  

---

## 📬 Updated Ticket Booking Flow  

1. User selects event → enters address.  
2. Clicks **"Proceed to Payment"** → Payment popup appears with QR Code & UTR input field.  
3. System validates UTR → dispatches ticket → updates admin analytics dashboard in real-time.

---

## 🔐 Admin Panel (FastAPI)  

| Endpoint           | Description                     | Method |
|--------------------|---------------------------------|--------|
| `/events`          | List all events                 | GET    |
| `/events`          | Add a new event                 | POST   |
| `/events/{id}`     | Update an event                 | PUT    |
| `/events/{id}`     | Delete an event                 | DELETE |
| `/book`            | Book ticket (no auth needed)    | POST   |
| `/submit-utr`      | Submit UTR after payment        | POST   |
| `/payment-vpa`     | Update UPI VPA                  | PUT    |
| `/analytics`       | Fetch admin analytics dashboard | GET    |

🔐 Admin actions require a token in the request header:  

```plaintext
Authorization: Bearer supersecuretoken123
```

---

## ✨ Analytics Dashboard Features  

### Key Metrics:
1. **Total Bookings:** Number of tickets booked across all events.
2. **Revenue Insights:** Revenue generated per day/week/month.
3. **Event Popularity:** Events ranked by ticket sales.
4. **UTR Status:** Pending vs verified UTR submissions.
5. **User Activity:** Number of users accessing the platform daily.

### Interactive Charts:
1. Bar charts for ticket sales per event.
2. Line charts for revenue trends.
3. Pie charts for payment methods distribution.

### Real-Time Updates:
1. WebSocket integration to reflect live booking data.
2. Auto-refresh every minute for analytics updates.

---

## 🤖 GitHub Copilot Prompt  

Build a mobile-first event ticketing platform with:
- React + TypeScript + Tailwind CSS + shadcn/ui frontend   
- FastAPI + MongoDB backend   
- Book tickets without login or OTP   
- Use QR payment + UTR ID verification   
- Admin dashboard to manage events, payments, and analytics   
- Separate folders for frontend and backend   

---

With the addition of the **Admin Analytics Dashboard**, Eventia empowers administrators to monitor platform performance effectively while providing actionable insights into user behavior and revenue trends! 🚀

---

## Project info

**URL**: https://lovable.dev/projects/64251d08-44af-4630-94df-97e048e84279

## How can I edit this code?

There are several ways of editing your application.

**Use Lovable**

Simply visit the [Lovable Project](https://lovable.dev/projects/64251d08-44af-4630-94df-97e048e84279) and start prompting.

Changes made via Lovable will be committed automatically to this repo.

**Use your preferred IDE**

If you want to work locally using your own IDE, you can clone this repo and push changes. Pushed changes will also be reflected in Lovable.

The only requirement is having Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

Follow these steps:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project directory.
cd <YOUR_PROJECT_NAME>

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Start the development server with auto-reloading and an instant preview.
npm run dev
```

**Edit a file directly in GitHub**

- Navigate to the desired file(s).
- Click the "Edit" button (pencil icon) at the top right of the file view.
- Make your changes and commit the changes.

**Use GitHub Codespaces**

- Navigate to the main page of your repository.
- Click on the "Code" button (green button) near the top right.
- Select the "Codespaces" tab.
- Click on "New codespace" to launch a new Codespace environment.
- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

This project is built with:

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## 🗄️ MongoDB Setup

To connect the project to MongoDB Atlas:

1. Create a `.env` file in the backend directory:

```bash
cd eventia-backend
touch .env
```

2. Add the MongoDB connection string to the `.env` file:

```
MONGODB_URI=mongodb://frdweb12:G5QMAprruao49p2u@mongodb-shard-00-00.s8fgq.mongodb.net:27017,mongodb-shard-00-01.s8fgq.mongodb.net:27017,mongodb-shard-00-02.s8fgq.mongodb.net:27017/?replicaSet=atlas-11uw3h-shard-0&ssl=true&authSource=admin&retryWrites=true&w=majority&appName=MongoDB
```

3. In your backend code, use this environment variable to connect to MongoDB:

```python
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB connection string
mongodb_uri = os.getenv("MONGODB_URI")

# Connect to MongoDB
client = MongoClient(mongodb_uri)
db = client.eventia_db
```

4. Make sure to install the required Python packages:

```bash
pip install pymongo python-dotenv
```

## 🚀 Running the Complete Project

### 1. Start the Backend

```bash
cd eventia-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install pymongo python-dotenv  # Install MongoDB dependencies
uvicorn main:app --reload
```

The backend API will be available at [http://localhost:8000](http://localhost:8000)

### 2. Start the Frontend

In a new terminal:

```bash
cd eventia-gather-spot
npm install
npm run dev
```

The frontend will be available at [http://localhost:3000](http://localhost:3000)

### 3. Verify MongoDB Connection

To verify your MongoDB connection is working:

1. Access the FastAPI Swagger UI at [http://localhost:8000/docs](http://localhost:8000/docs)
2. Try using the `/events` GET endpoint to check if data is being fetched from MongoDB

## How can I deploy this project?

Simply open [Lovable](https://lovable.dev/projects/64251d08-44af-4630-94df-97e048e84279) and click on Share -> Publish.

## Can I connect a custom domain to my Lovable project?

Yes, you can!

To connect a domain, navigate to Project > Settings > Domains and click Connect Domain.

Read more here: [Setting up a custom domain](https://docs.lovable.dev/tips-tricks/custom-domain#step-by-step-guide)

# Eventia IPL Ticketing Platform

A production-grade IPL ticketing platform built with React/TypeScript frontend and FastAPI/MongoDB backend.

## TL;DR

Plan meticulously, code with quality, test exhaustively, automate deployment, secure relentlessly, monitor constantly, and be ready to recover instantly.

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Quick Start](#quick-start)
5. [Development Guide](#development-guide)
6. [Testing](#testing)
7. [Deployment](#deployment)
8. [Security & Compliance](#security--compliance)
9. [Monitoring & Observability](#monitoring--observability)
10. [Incident Response](#incident-response)

## Overview

Eventia is a complete ticketing solution for IPL matches and other events. It allows users to browse events, book tickets without login, make payments via QR code/UTR, and receive physical tickets. Admins can manage events, verify payments, and access analytics.

## Features

### User Features
- Browse events and IPL matches
- Select seats and quantity
- Book tickets without login
- Pay via QR code with UTR submission
- Get physical tickets delivered within 2 days

### Admin Features
- Manage events and ticket inventory
- Verify UTR payments
- Dispatch tickets
- Update payment VPA
- View analytics dashboard

## Tech Stack

### Frontend
- React with TypeScript
- Tailwind CSS with shadcn/ui
- Tanstack Query for data fetching
- React Router for navigation

### Backend
- FastAPI (Python)
- MongoDB for database
- JWT for admin authentication

### Infrastructure
- Docker for containerization
- Nginx for reverse proxy and SSL termination
- Let's Encrypt for SSL certificates

## Quick Start

### Development

```bash
# Clone the repository
git clone https://github.com/yourusername/eventia.git
cd eventia

# Start the development environment
docker-compose -f docker-compose.dev.yml up
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Production

```bash
# Set up environment variables
cp .env.prod.sample .env.prod
# Edit .env.prod with your production values

# Initialize SSL certificates (first time only)
docker-compose -f docker-compose.prod.yml run --rm certbot certonly --webroot -w /var/www/certbot --email admin@example.com -d eventia.example.com --agree-tos

# Start the production environment
docker-compose -f docker-compose.prod.yml up -d
```

## Development Guide

### Project Structure

```
eventia/
├── eventia-ticketing-flow/    # Frontend (React)
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── lib/               # Utility functions and API client
│   │   ├── pages/             # Page components
│   │   └── main.tsx           # Entry point
│   └── ...
├── eventia-backend/           # Backend (FastAPI)
│   ├── main.py                # FastAPI application
│   ├── seed_data.py           # Demo data generation
│   ├── db_init.py             # Database initialization
│   └── tests/                 # Backend tests
├── nginx/                     # Nginx configuration
├── docker-compose.dev.yml     # Development Docker Compose
└── docker-compose.prod.yml    # Production Docker Compose
```

### Code Standards

We follow industry best practices for code quality:

**Frontend**
- ESLint for JavaScript/TypeScript linting
- Prettier for code formatting
- TypeScript for type safety

**Backend**
- Black for code formatting
- Flake8 for linting
- Pytest for testing

### Branching Strategy

We use GitFlow for development:

- `main`: Production code
- `develop`: Integration branch
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `release/*`: Release preparation
- `hotfix/*`: Production fixes

## Testing

### Frontend Testing

```bash
# Run frontend tests
cd eventia-ticketing-flow
yarn test

# Run with coverage
yarn test --coverage
```

### Backend Testing

```bash
# Run backend tests
cd eventia-backend
pytest

# Run with coverage
pytest --cov=app
```

### End-to-End Testing

```bash
# Run end-to-end tests
cd eventia-ticketing-flow
yarn test:e2e
```

## Deployment

### Local Development

For local development, we use Docker Compose to set up the entire stack:

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  backend:
    build:
      context: ./eventia-backend
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - ./eventia-backend:/app
    environment:
      - ENVIRONMENT=development
      - MONGODB_URI=mongodb://mongodb:27017/eventia
      - ADMIN_TOKEN=dev-token-123
      - CUSTOM_VPA=eventia@upi
      - SEED_DATA=true
      - LOG_LEVEL=DEBUG
    depends_on:
      - mongodb

  frontend:
    build:
      context: ./eventia-ticketing-flow
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - ./eventia-ticketing-flow:/app
      - /app/node_modules
    environment:
      - VITE_API_URL=http://localhost:8000/api
    depends_on:
      - backend

  mongodb:
    image: mongo:6.0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    networks:
      - eventia-network

networks:
  eventia-network:
    driver: bridge

volumes:
  mongodb_data:
```

### Production Deployment

For production, we use a more robust setup with Nginx for SSL termination:

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./data/certbot/conf:/etc/letsencrypt
      - ./data/certbot/www:/var/www/certbot
    command: "/bin/sh -c 'while :; do sleep 6h & wait $${!}; nginx -s reload; done & nginx -g \"daemon off;\"'"
    depends_on:
      - backend
      - frontend
    networks:
      - eventia-network
    restart: always

  frontend:
    build:
      context: ./eventia-ticketing-flow
      dockerfile: Dockerfile.prod
    expose:
      - "80"
    networks:
      - eventia-network
    restart: always
    environment:
      - VITE_API_URL=/api

  backend:
    build:
      context: ./eventia-backend
      dockerfile: Dockerfile.prod
    expose:
      - "8000"
    environment:
      - ENVIRONMENT=production
      - MONGODB_URI=${MONGODB_URI}
      - ADMIN_TOKEN=${ADMIN_TOKEN}
      - CUSTOM_VPA=${CUSTOM_VPA}
    restart: always
    depends_on:
      - mongodb
    networks:
      - eventia-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  mongodb:
    image: mongo:6.0
    volumes:
      - mongodb_data:/data/db
    environment:
      - MONGO_INITDB_ROOT_USERNAME=${MONGO_INITDB_ROOT_USERNAME}
      - MONGO_INITDB_ROOT_PASSWORD=${MONGO_INITDB_ROOT_PASSWORD}
    command: mongod --quiet --auth
    restart: always
    networks:
      - eventia-network
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/admin -u $${MONGO_INITDB_ROOT_USERNAME} -p $${MONGO_INITDB_ROOT_PASSWORD} --quiet
      interval: 10s
      timeout: 5s
      retries: 3

  certbot:
    image: certbot/certbot
    volumes:
      - ./data/certbot/conf:/etc/letsencrypt
      - ./data/certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
    networks:
      - eventia-network

networks:
  eventia-network:
    driver: bridge

volumes:
  mongodb_data:
```

### CI/CD Pipeline

We use GitHub Actions for CI/CD:

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test-backend:
    # ... backend testing job
    
  test-frontend:
    # ... frontend testing job
    
  build-and-deploy:
    # ... build and deploy job
```

## Security & Compliance

### Authentication & Authorization

- Admin authentication via JWT tokens
- API access protection
- CORS configuration for frontend-backend communication

### Data Protection

- HTTPS everywhere
- Secure cookie handling
- Input validation
- MongoDB authentication

### Compliance Considerations

- GDPR compliance for customer data
- Secure payment handling
- Data retention policies

## Monitoring & Observability

### Metrics

- API response times
- Error rates
- User engagement metrics
- Business KPIs

### Logging

- Centralized logging with ELK stack
- Structured logging format
- Log rotation and retention

### Alerting

- Critical error alerting
- Performance degradation alerts
- Business metric anomalies

## Incident Response

### Incident Classification

- Severity levels (P0-P3)
- Response SLAs
- Escalation paths

### Runbooks

- Common failure scenarios
- Troubleshooting guides
- Recovery procedures

### Post-Incident Analysis

- Root cause analysis
- Blameless postmortems
- Action items for prevention

## Docker Setup

The Eventia Ticketing Platform can be deployed using Docker containers for both development and production environments.

### Development Environment

1. Make sure you have Docker and Docker Compose installed
2. Run the development environment:
   ```
   docker-compose -f docker-compose.dev.yml up
   ```
3. The services will be available at:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:3000/api
   - MongoDB: localhost:27017

### Production Environment

1. Make sure you have Docker and Docker Compose installed
2. Build and run the production containers:
   ```
   docker-compose -f docker-compose.prod.yml up -d
   ```
3. The application will be available at:
   - Web Application: http://localhost (port 80)
   - Backend API (through the frontend proxy): http://localhost/api

### Environment Variables

- `.env.dev` - Contains environment variables for development
- `.env.prod` - Contains environment variables for production

### Docker Compose Files

- `docker-compose.yml` - Base configuration for both environments
- `docker-compose.dev.yml` - Development environment configuration
- `docker-compose.prod.yml` - Production environment configuration
# Eventia_Proj
