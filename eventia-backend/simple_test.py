#!/usr/bin/env python
import requests
import socket
import sys
import time

def check_port(host, port):
    """Check if a port is open on the host."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

def test_endpoints(host, port):
    """Test various endpoints on the server."""
    endpoints = [
        "/",
        "/api/events",
        "/api/health",
        "/api/config/public",
        "/docs",
    ]
    
    results = []
    for endpoint in endpoints:
        url = f"http://{host}:{port}{endpoint}"
        try:
            response = requests.get(url, timeout=2)
            status = f"✅ {response.status_code}"
            content = response.text[:50].replace('\n', ' ') + "..." if response.text else "Empty response"
            results.append((endpoint, status, content))
        except Exception as e:
            results.append((endpoint, f"❌ Error", str(e)))
    
    return results

def main():
    ports_to_check = [3002, 3003, 5000, 5001, 8000]
    
    print("Checking for available servers...\n")
    for port in ports_to_check:
        if check_port('localhost', port):
            print(f"✅ Server found on port {port}")
            
            # Test endpoints on this port
            results = test_endpoints('localhost', port)
            print(f"\nEndpoint tests for port {port}:")
            print("-" * 60)
            for endpoint, status, content in results:
                print(f"{endpoint:15} | {status:12} | {content}")
            print("-" * 60)
            print()
        else:
            print(f"❌ No server on port {port}")

if __name__ == "__main__":
    main() 