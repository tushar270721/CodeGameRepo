import requests
from requests.auth import HTTPBasicAuth
import os
from pathlib import Path

ORG = "enablon"
PROJECT = "ART - New SaaS"

# PAT Token - Priority order:
# 1. Environment variable (AZURE_DEVOPS_PAT)
# 2. .env file in current directory
# 3. Placeholder for local development
PAT = os.getenv('AZURE_DEVOPS_PAT')

# Try to load from .env file if not found in environment
if not PAT:
    env_file = Path('.env')
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv()
            PAT = os.getenv('AZURE_DEVOPS_PAT')
        except ImportError:
            # Parse .env manually if python-dotenv not installed
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('AZURE_DEVOPS_PAT='):
                        PAT = line.split('=', 1)[1].strip().strip('"').strip("'")
                        break

# If still not found, use placeholder
if not PAT:
    PAT = "YOUR_PAT_TOKEN"
    print("⚠️  Warning: PAT token not found")
    print("   Set AZURE_DEVOPS_PAT environment variable or create .env file")

BASE_URL = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/wit/workitems"

def get_bug(bug_id):
    url = f"{BASE_URL}/{bug_id}?api-version=7.0"
    
    response = requests.get(
        url,
        auth=HTTPBasicAuth('', PAT),
        verify=False
    )

    return response.json()


def add_comment(bug_id, comment):
    url = f"{BASE_URL}/{bug_id}/comments?api-version=7.0-preview.3"
    
    data = {
        "text": comment
    }

    response = requests.post(
        url,
        json=data,
        auth=HTTPBasicAuth('', PAT),
        verify=False
    )

    return response.json()


def get_comments(bug_id):
    url = f"{BASE_URL}/{bug_id}/comments?api-version=7.0-preview.3"
    
    response = requests.get(
        url,
        auth=HTTPBasicAuth('', PAT),
        verify=False
    )

    return response.json()
