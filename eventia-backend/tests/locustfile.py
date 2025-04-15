from locust import HttpUser, task, between
import json
import random

class EventTicketingUser(HttpUser):
    wait_time = between(1, 5)  # Wait between 1 and 5 seconds between tasks
    
    def on_start(self):
        # Initialize user with a correlation ID
        self.correlation_id = f"test-user-{random.randint(10000, 99999)}"
        self.headers = {"X-Correlation-ID": self.correlation_id}
        
        # Load available events
        self.events = []
        response = self.client.get("/api/events", headers=self.headers)
        if response.status_code == 200:
            self.events = response.json()
    
    @task(10)
    def view_events(self):
        """Browse events - most common task."""
        self.client.get("/api/events", headers=self.headers)
    
    @task(5)
    def view_event_by_category(self):
        """Browse events by category."""
        categories = ["IPL", "Concert"]
        category = random.choice(categories)
        self.client.get(f"/api/events?category={category}", headers=self.headers)
    
    @task(3)
    def view_event_details(self):
        """View details of a specific event."""
        if not self.events:
            return
        
        event = random.choice(self.events)
        self.client.get(f"/api/events/{event['id']}", headers=self.headers)
    
    @task(1)
    def create_booking(self):
        """Create a booking for an event."""
        if not self.events:
            return
        
        event = random.choice(self.events)
        
        # Customer data
        customer_info = {
            "name": f"Test User {random.randint(1000, 9999)}",
            "email": f"test{random.randint(1000, 9999)}@example.com",
            "phone": f"98{random.randint(10000000, 99999999)}"
        }
        
        # Create a booking
        booking_data = {
            "event_id": event["id"],
            "quantity": random.randint(1, 4),
            "customer_info": customer_info
        }
        
        response = self.client.post(
            "/api/bookings",
            json=booking_data,
            headers=self.headers
        )
        
        if response.status_code == 200:
            booking_response = response.json()
            self.booking_id = booking_response["booking_id"]
            self.verify_payment()
    
    def verify_payment(self):
        """Submit UTR for a booking."""
        if not hasattr(self, "booking_id"):
            return
        
        # Generate a fake UTR
        utr = f"UTR{random.randint(100000000, 999999999)}"
        
        # Submit UTR
        payment_data = {
            "booking_id": self.booking_id,
            "utr": utr
        }
        
        self.client.post(
            "/api/verify-payment",
            json=payment_data,
            headers=self.headers
        )
        
        # Clear booking ID
        del self.booking_id
    
    @task(1)
    def check_health(self):
        """Check API health."""
        self.client.get("/health", headers=self.headers)
    
    @task(0.5)
    def view_metrics(self):
        """View API metrics."""
        self.client.get("/metrics", headers=self.headers)
    
    @task(0.2)
    def access_invalid_endpoint(self):
        """Access an invalid endpoint to test error handling."""
        self.client.get(f"/invalid-endpoint-{random.randint(1, 100)}", headers=self.headers)

# Run the load test:
# locust -f tests/locustfile.py --host=http://localhost:3002 --users=1000 --spawn-rate=10
# For headless mode:
# locust -f tests/locustfile.py --host=http://localhost:3002 --users=1000 --spawn-rate=10 --run-time=5m --headless --html=locust-report.html 