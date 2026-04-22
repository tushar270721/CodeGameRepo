import requests
from requests.auth import HTTPBasicAuth

ORG = "enablon"
PROJECT = "ART - New SaaS"
PAT = ""

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
