import os
from typing import Dict, List, Tuple
import requests
from dotenv import load_dotenv, find_dotenv

class URLChecker:
    """A class to handle URL safety checks."""

    # Standard threat types for Google Safe Browsing API
    THREAT_TYPES = [
        "MALWARE",
        "SOCIAL_ENGINEERING",
        "UNWANTED_SOFTWARE",
        "POTENTIALLY_HARMFUL_APPLICATION"
    ]

    def __init__(self):
        load_dotenv(find_dotenv())
        
        self.safebrowsing_key = os.getenv("SAFEBROWSING_API_KEY")
        if not self.safebrowsing_key:
            raise ValueError("SAFEBROWSING_API_KEY is missing in environment variables.")
            
        self.base_url = "https://safebrowsing.googleapis.com/v4"
        self.client_id = "minerva"
        self.client_version = "0.1.0"

    def expand_url(self, url: str) -> str:
        """Expand shortened URL.
        """
        try:
            response = requests.head(url, allow_redirects=True)
            return response.url
        except requests.exceptions.RequestException:
            return url # Return original URL if expansion fails

    def is_url_safe(self, target_url: str) -> Tuple[str, List[Dict[str, str]]]:
        """Check if URL is safe using Google Safe Browsing API.
        """
        safe_endpoint = f"{self.base_url}/threatMatches:find?key={self.safebrowsing_key}"
        expanded_url = self.expand_url(target_url)

        request_body = {
            "client": {
                "clientId": self.client_id,
                "clientVersion": self.client_version
            },
            "threatInfo": {
                "threatTypes": self.THREAT_TYPES,
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": target_url}]
            }
        }

        if expanded_url != target_url:
            request_body["threatInfo"]["threatEntries"].append({"url": expanded_url})
        
        try:
            response = requests.post(safe_endpoint, json=request_body)
            response.raise_for_status()
            
            result = response.json()
            
            if not result:
                return "Not Flagged", []
            
            threats = []
            if "matches" in result:
                for match in result["matches"]:
                    threats.append({
                        "threat_type": match.get("threatType"),
                        "threat_url": match.get("threat", {}).get("url"),
                    })
            
            return "Flagged", threats
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error checking URL safety: {str(e)}")