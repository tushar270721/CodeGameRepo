import requests
from requests.auth import HTTPBasicAuth

# Auth API Configuration
AUTH_ENDPOINT = "https://nexus-az.dev.enablon.io/authentication/connect/token"
DATAPLANE_ENDPOINT = "https://nexus-az.dev.enablon.io/ehs/api/dataplane/tenant-events"

# Credentials
CLIENT_ID = "2c65d3b5-3e24-4187-a30e-e284946d0900"
CLIENT_SECRET = "MBBW9rPJrvdfSOwhH4LeAOvPOASu4bitnorCT7eOmCfwBtBLyF2ydKAwpvfdlVYuCC7PXoRaAzUSrpCKCDKJb5KzeRiEZnNUnmNC349ArdcTfra4qD2ya719O0iHxqVQ3mm8xqvfVjmipoOt9FPYX2n5hE2Z9XL6G3YxCimD7g"
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
