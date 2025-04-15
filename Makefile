.PHONY: dev stop seed clean logs setup check-files fix-permissions prod-up prod-down prod-logs setup-ssl frontend-deps backend-deps

# Development environment
dev:
	@echo "Starting development environment..."
	@$(MAKE) check-files
	@$(MAKE) fix-permissions
	docker-compose -f docker-compose.dev.yml up --build

dev-detach:
	@echo "Starting development environment in detached mode..."
	@$(MAKE) check-files
	@$(MAKE) fix-permissions
	docker-compose -f docker-compose.dev.yml up --build -d

stop:
	@echo "Stopping development environment..."
	docker-compose -f docker-compose.dev.yml down

seed:
	@echo "Seeding database with sample data..."
	docker-compose -f docker-compose.dev.yml exec backend python seed_data.py

logs:
	@echo "Showing logs for development environment..."
	docker-compose -f docker-compose.dev.yml logs -f

# Production environment
prod-up:
	@echo "Starting production environment..."
	@$(MAKE) check-files
	@$(MAKE) fix-permissions
	mkdir -p ./nginx/conf.d ./nginx/ssl ./certbot/conf ./certbot/www
	@if [ ! -f ./nginx/conf.d/default.conf ]; then \
		echo "Creating default Nginx configuration..."; \
		echo 'server { \
			listen 80; \
			server_name _; \
			location / { \
				proxy_pass http://backend:8000; \
				proxy_set_header Host $$host; \
				proxy_set_header X-Real-IP $$remote_addr; \
			} \
			location /.well-known/acme-challenge/ { \
				root /var/www/certbot; \
			} \
		}' > ./nginx/conf.d/default.conf; \
	fi
	docker-compose -f docker-compose.prod.yml up -d

prod-down:
	@echo "Stopping production environment..."
	docker-compose -f docker-compose.prod.yml down

prod-logs:
	@echo "Showing logs for production environment..."
	docker-compose -f docker-compose.prod.yml logs -f

setup-ssl:
	@echo "Setting up SSL certificates with Let's Encrypt..."
	@read -p "Enter your domain name (e.g., example.com): " domain; \
	read -p "Enter your email address: " email; \
	docker-compose -f docker-compose.prod.yml run --rm certbot certonly --webroot -w /var/www/certbot/ --email $$email -d $$domain --agree-tos --no-eff-email
	@echo "Now updating Nginx configuration to use SSL..."
	@read -p "Enter your domain name again: " domain; \
	echo "server { \
		listen 80; \
		server_name $$domain; \
		location /.well-known/acme-challenge/ { \
			root /var/www/certbot; \
		} \
		location / { \
			return 301 https://$$domain\$$request_uri; \
		} \
	} \
	server { \
		listen 443 ssl; \
		server_name $$domain; \
		ssl_certificate /etc/letsencrypt/live/$$domain/fullchain.pem; \
		ssl_certificate_key /etc/letsencrypt/live/$$domain/privkey.pem; \
		location / { \
			proxy_pass http://backend:8000; \
			proxy_set_header Host $$host; \
			proxy_set_header X-Real-IP $$remote_addr; \
		} \
	}" > ./nginx/conf.d/default.conf
	docker-compose -f docker-compose.prod.yml restart nginx

# Development dependencies
frontend-deps:
	@echo "Installing frontend dependencies..."
	cd ./eventia-ticketing-flow && npm install

backend-deps:
	@echo "Installing backend dependencies..."
	cd ./eventia-backend && pip install -r requirements.txt

# Maintenance
clean:
	@echo "Cleaning up Docker resources..."
	docker-compose -f docker-compose.dev.yml down -v || true
	docker-compose -f docker-compose.prod.yml down -v || true
	docker system prune -f

# Utility targets
check-files:
	@echo "Checking if required files exist..."
	@if [ ! -f ./eventia-backend/main.py ]; then \
		echo "Creating a minimal main.py file..."; \
		mkdir -p ./eventia-backend; \
		echo 'from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get("/")\ndef read_root():\n    return {"message": "Welcome to Eventia API"}' > ./eventia-backend/main.py; \
	fi
	@if [ ! -f ./eventia-backend/requirements.txt ]; then \
		echo "Creating minimal requirements.txt..."; \
		mkdir -p ./eventia-backend; \
		echo 'fastapi==0.105.0\nuvicorn==0.24.0\npython-dotenv==1.0.0\nmotor==3.3.1\npymongo==4.6.0\ngunicorn==21.2.0' > ./eventia-backend/requirements.txt; \
	fi
	@if [ ! -d ./eventia-ticketing-flow ]; then \
		echo "Creating minimal frontend setup..."; \
		mkdir -p ./eventia-ticketing-flow; \
		echo '{\n  "name": "eventia-ticketing-flow",\n  "version": "0.1.0",\n  "private": true,\n  "scripts": {\n    "dev": "vite",\n    "start": "vite",\n    "build": "vite build",\n    "preview": "vite preview"\n  },\n  "dependencies": {\n    "react": "^18.2.0",\n    "react-dom": "^18.2.0",\n    "@tanstack/react-query": "^4.35.3",\n    "tailwindcss": "^3.3.3"\n  },\n  "devDependencies": {\n    "@vitejs/plugin-react": "^4.0.4",\n    "vite": "^4.4.9",\n    "typescript": "^5.1.6"\n  }\n}' > ./eventia-ticketing-flow/package.json; \
	fi
	@if [ ! -f ./eventia-backend/entrypoint.sh ]; then \
		echo "Creating entrypoint script..."; \
		mkdir -p ./eventia-backend; \
		echo '#!/bin/bash\nset -e\n\n# Wait for MongoDB to be ready\necho "Waiting for MongoDB to be ready..."\nMAX_ATTEMPTS=30\nATTEMPTS=0\n\n# Using a more reliable connection check with mongo/mongosh\nuntil mongo --host mongodb --eval "db.stats()" > /dev/null 2>&1 || mongosh --host mongodb --quiet --eval "db.stats()" > /dev/null 2>&1; do\n  ATTEMPTS=$$(ATTEMPTS+1))\n  if [ $$ATTEMPTS -ge $$MAX_ATTEMPTS ]; then\n    echo "MongoDB not available after $$MAX_ATTEMPTS attempts, giving up"\n    exit 1\n  fi\n  echo "MongoDB not ready yet, waiting... (attempt $$ATTEMPTS/$$MAX_ATTEMPTS)"\n  sleep 2\ndone\n\necho "MongoDB is ready!"\n\n# Run the seed script if SEED_DATA is set to true\nif [ "$${SEED_DATA}" = "true" ]; then\n    echo "Seeding database with sample data..."\n    python seed_data.py\nfi\n\n# Execute the CMD from Dockerfile (or docker-compose)\nexec "$$@"' > ./eventia-backend/entrypoint.sh; \
	fi

fix-permissions:
	@echo "Fixing script permissions..."
	@chmod +x ./eventia-backend/entrypoint.sh 2>/dev/null || true
