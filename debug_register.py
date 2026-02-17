import urllib.request
import json
import urllib.error

BASE_URL = "http://localhost:8000"

def test_register():
    url = f"{BASE_URL}/auth/register"
    payload = {
        "username": "test_debug_user_v2",
        "password": "password123",
        "email": None
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    print(f"Sending POST to {url} with payload: {payload}")
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Status Code: {response.getcode()}")
            print("Response:", response.read().decode('utf-8'))
            
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        print("Response:", e.read().decode('utf-8'))
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
        print("Make sure the server is running on localhost:8000")

if __name__ == "__main__":
    test_register()
