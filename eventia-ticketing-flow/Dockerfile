FROM node:18

WORKDIR /app

# Install dependencies first (for better caching)
COPY package*.json ./
RUN npm install

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 8080

# Command to run the app
CMD ["npm", "run", "dev"]

# Fix for missing 'start' script in package.json
RUN if ! grep -q '"start"' package.json; then \
    sed -i 's/"scripts": {/"scripts": {\n    "start": "react-scripts start",/g' package.json; \
    fi
    
# Fix for missing 'dev' script in package.json
RUN if ! grep -q '"dev"' package.json; then \
    sed -i 's/"scripts": {/"scripts": {\n    "dev": "react-scripts start",/g' package.json; \
    fi

# Use development command - this will be overridden by docker-compose command
CMD ["npm", "run", "dev"]
