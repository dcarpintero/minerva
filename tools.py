import os
from typing import Dict, List, Tuple

from PIL import Image
import pytesseract
import requests
from dotenv import load_dotenv, find_dotenv


class Tools:
    def __init__(self):
        load_dotenv(find_dotenv())

        self.safebrowsing_key = os.getenv("SAFEBROWSING_API_KEY")
        self.api_base_url = "https://safebrowsing.googleapis.com/v4"
        self.client_id = "minerva"
        self.client_version = "0.1.0"
        self.threat_types = [
            "MALWARE",
            "SOCIAL_ENGINEERING",
            "UNWANTED_SOFTWARE",
            "POTENTIALLY_HARMFUL_APPLICATION"
        ]

    def ocr(self, image_path: str) -> str:
        """Extract text from image using OCR
        """
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            return f"Error in text extraction: {str(e)}"

    def expand_url(self, url: str) -> str:
        """Expand shortened URL
        """
        try:
            response = requests.head(url, allow_redirects=True)
            return response.url
        except requests.exceptions.RequestException as e:
            return url  # Return original URL if expansion fails
    
    def is_url_safe(self, url: str) -> Tuple[bool, List[Dict[str, str]]]:
        """Check if URL is safe using Google Safe Browsing API
        """
        if not self.safebrowsing_key:
            raise ValueError("SAFEBROWSING_API_KEY is missing.")
        
        api_endpoint = f"{self.api_base_url}/threatMatches:find?key={self.safebrowsing_key}"
        expanded_url = self.expand_url(url)
        
        request_body = {
            "client": {
                "clientId": self.client_id,
                "clientVersion": self.client_version
            },
            "threatInfo": {
                "threatTypes": self.threat_types,
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [
                    {"url": url},
                    {"url": expanded_url} if expanded_url != url else {}
                ]
            }
        }
        
        try:
            response = requests.post(api_endpoint, json=request_body)
            response.raise_for_status()

            result = response.json()
            
            if not result:
                return True, []
            
            threats = []
            if "matches" in result:
                for match in result["matches"]:
                    threats.append({
                        "threat_type": match.get("threatType"),
                        "platform_type": match.get("platformType"),
                        "threat_entry_type": match.get("threatEntryType")
                    })
            
            return False, threats
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error checking URL safety: {str(e)}")