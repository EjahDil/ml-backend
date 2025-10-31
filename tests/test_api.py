import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_register():
    print("Test 1: Registering a new user...")
    payload = {
        "username": "tiana_test",
        "password": "secret123",
        "full_name": "Tiana Test",
        "team": "Retention Team",
        "role": "Test Analyst"
    }
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=payload)
        if response.status_code == 200:
            user = response.json()
            print(f"User created! ID: {user['id']}")
            print(f"Name: {user['full_name']}, Team: {user['team']}")
            return True
        else:
            print(f"Registration failed: {response.status_code}")
            print(response.json())
            return False
    except Exception as e:
        print(f"Network error: {e}")
        return False

