import requests
from requests.auth import HTTPBasicAuth
import os
from pathlib import Path

# Auth API Configuration
AUTH_ENDPOINT = "https://nexus-az.dev.enablon.io/authentication/connect/token"
DATAPLANE_ENDPOINT = "https://nexus-az.dev.enablon.io/ehs/api/dataplane/tenant-events"

# Credentials - Load from environment variables
CLIENT_ID = os.getenv('ENABLON_CLIENT_ID')
CLIENT_SECRET = os.getenv('ENABLON_CLIENT_SECRET')

# Try to load from .env file if not found in environment
if not CLIENT_ID or not CLIENT_SECRET:
    env_file = Path('.env')
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv()
            CLIENT_ID = os.getenv('ENABLON_CLIENT_ID')
            CLIENT_SECRET = os.getenv('ENABLON_CLIENT_SECRET')
        except ImportError:
            # Parse .env manually if python-dotenv not installed
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('ENABLON_CLIENT_ID='):
                        CLIENT_ID = line.split('=', 1)[1].strip().strip('"').strip("'")
                    elif line.startswith('ENABLON_CLIENT_SECRET='):
                        CLIENT_SECRET = line.split('=', 1)[1].strip().strip('"').strip("'")

# If still not found, use fallback values (for testing only)
if not CLIENT_ID:
    CLIENT_ID = "2c65d3b5-3e24-4187-a30e-e284946d0900"
if not CLIENT_SECRET:
    CLIENT_SECRET = ""
    print("⚠️  Warning: ENABLON_CLIENT_SECRET not found")
    print("   Set ENABLON_CLIENT_ID and ENABLON_CLIENT_SECRET environment variables or create .env file")

SCOPE = "enablon-data"
GRANT_TYPE = "client_credentials"
AUDIENCE = "api"

# Cache for access token
_access_token = None
_token_expiry = None


def get_access_token():
    """Get access token from Auth API"""
    global _access_token, _token_expiry
    
    auth_payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": SCOPE,
        "grant_type": GRANT_TYPE,
        "audience": AUDIENCE
    }
    
    try:
        response = requests.post(
            AUTH_ENDPOINT,
            data=auth_payload,
            verify=False
        )
        
        response.raise_for_status()
        token_data = response.json()
        
        _access_token = token_data.get("access_token")
        _token_expiry = token_data.get("expires_in")
        
        print(f"✅ Access token obtained (expires in {_token_expiry}s)")
        return _access_token
        
    except Exception as e:
        print(f"❌ Error getting access token: {str(e)}")
        raise


def send_event(event_type, enablon_tenant_id, payload):
    """Send event to Dataplane API"""
    
    # Get access token
    token = get_access_token()
    
    # Construct request body
    event_body = {
        "eventType": event_type,
        "enablonTenantId": enablon_tenant_id,
        "payload": payload
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            DATAPLANE_ENDPOINT,
            json=event_body,
            headers=headers,
            verify=False
        )
        
        result = response.json()
        
        if response.status_code == 200:
            print(f"✅ Event sent successfully")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            if result.get('errors'):
                print(f"   Errors:")
                for error in result.get('errors', []):
                    print(f"     - {error}")
        
        return result
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {str(e)}")
        try:
            error_detail = e.response.json()
            print(f"   Error Detail: {error_detail}")
        except:
            print(f"   Response: {e.response.text}")
        raise
    except Exception as e:
        print(f"❌ Error sending event: {str(e)}")
        raise


# Example usage
if __name__ == "__main__":
    # Test Auth API
    print("🔐 Testing Auth API...")
    try:
        token = get_access_token()
        print(f"Token: {token[:50]}...")
    except Exception as e:
        print(f"Auth failed: {e}")
    
    # Test Dataplane API
    print("\n📡 Testing Dataplane API...")
    try:
        # Invalid payload (to test bug scenario)
        payload = {
            "serviceName": "APPLICATIONSERVER",
            "rootUrl": "invalid-url",  # ❌ Invalid URL
            "aiServicesApiUrl": "",  # ❌ Empty
            "navigationAssistantStatus": "INVALID",  # ❌ Wrong type (should be boolean)
            "aiConversationalInterfaceStatus": True
        }
        
        result = send_event(
            event_type="ServiceEntitled",
            enablon_tenant_id="",  # ❌ Empty tenant ID
            payload=payload
        )
        
        print(f"Response: {result}")
        
    except Exception as e:
        print(f"Dataplane failed: {e}")
