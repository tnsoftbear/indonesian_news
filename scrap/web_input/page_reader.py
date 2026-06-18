import requests
from web_input.session_manager import SessionManager

class PageReader:
    """
    Page reader that supports both traditional cookie-based requests
    and automated browser-based session management.
    """
    
    @staticmethod
    def get_page_data(url, sid=None):
        """
        Get page data using traditional cookie-based approach.
        Requires pre-obtained sid cookie value.
        """
        cookies = {"_sid": sid} if sid else {}
        headers = {
            "authority": "www.business-standard.com",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.7",
            "cache-control": "max-age=0",
            "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Brave";v="120"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "sec-gpc": "1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        
        response = requests.get(url, cookies=cookies, headers=headers)
        return response
    
    @staticmethod
    def get_page_data_with_session(url, session_manager):
        """
        Get page data using browser session with automated cookie handling.
        This is the fully automated approach that doesn't require manual SID extraction.
        """
        return session_manager.get_page_content(url)