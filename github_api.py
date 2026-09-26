import os
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")

def github_headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

def get_repositories():
    """Get repositories from the connected GitHub account."""

    if not GITHUB_TOKEN or not GITHUB_USERNAME:
        return []

    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"

    response = requests.get(
        url,
        headers=github_headers(),
        timeout=10
    )

    if response.status_code != 200:
        return []

    return response.json()
