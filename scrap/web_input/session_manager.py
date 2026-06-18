from playwright.sync_api import sync_playwright
import time
import logging
import subprocess
import sys

class SessionManager:
    """
    Manages browser session to automatically handle cookie consent
    and extract the _sid cookie from business-standard.com

    Uses the installed Chrome browser (channel="chrome") when available
    to bypass bot detection from Akamai CDN. Falls back to bundled Chromium
    if Chrome is not installed.
    """

    def __init__(self, headless=True):
        self.headless = headless
        self._sid = None
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def _chrome_available(self):
        """Check if Google Chrome is installed on the system."""
        chrome_paths = [
            "/usr/bin/google-chrome-stable",
            "/usr/bin/google-chrome",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        ]
        import os
        for path in chrome_paths:
            if os.path.exists(path):
                return True
        # Also try which/where command
        try:
            cmd = "where" if sys.platform == "win32" else "which"
            result = subprocess.run([cmd, "google-chrome"], capture_output=True, text=True)
            if result.returncode == 0:
                return True
        except Exception:
            pass
        return False

    def initialize(self):
        """
        Initialize browser session and accept cookie consent to get _sid cookie
        """
        # Start Playwright and keep reference alive
        self._playwright = sync_playwright().start()

        # Try to use installed Chrome to bypass bot detection
        use_chrome = self._chrome_available()
        launch_args = [
            "--no-sandbox",
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
            "--no-default-browser-check",
        ]

        if use_chrome:
            self.logger.info("Using installed Chrome browser to bypass bot detection")
            print("Using installed Chrome browser to bypass bot detection")
            self._browser = self._playwright.chromium.launch(
                headless=self.headless,
                channel="chrome",
                args=launch_args,
            )
        else:
            self.logger.info("Chrome not found, using bundled Chromium")
            print("Chrome not found, using bundled Chromium")
            self._browser = self._playwright.chromium.launch(
                headless=self.headless,
                args=launch_args,
            )

        self._context = self._browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="Asia/Kolkata",
        )
        self._page = self._context.new_page()

        # Navigate to the site
        self.logger.info("Navigating to business-standard.com to accept cookies...")
        print("Navigating to business-standard.com to accept cookies...")

        try:
            self._page.goto("https://www.business-standard.com", wait_until="networkidle", timeout=60000)
        except Exception as e:
            self.logger.warning(f"Initial navigation timed out, continuing anyway: {e}")

        # Wait a bit for cookie banner to appear
        time.sleep(3)

        # Try to accept cookie consent
        self._accept_cookie_consent()

        # Extract the _sid cookie
        self._sid = self._extract_sid()

        if self._sid:
            msg = f"Successfully extracted _sid: {self._sid[:20]}..."
            self.logger.info(msg)
            print(msg)
        else:
            msg = "Failed to extract _sid cookie - scraping may still work"
            self.logger.warning(msg)
            print(msg)

        return self._sid

    def _accept_cookie_consent(self):
        """
        Try multiple strategies to accept cookie consent
        """
        # Strategy 1: Look for accept button
        accept_selectors = [
            "button:has-text('Accept')",
            "button:has-text('Accept All')",
            "button:has-text('I Accept')",
            "[data-testid='accept-button']",
            ".cookie-accept",
            "button.accept",
            "input[value*='Accept']",
        ]

        for selector in accept_selectors:
            try:
                button = self._page.locator(selector).first
                if button.is_visible(timeout=3000):
                    button.click()
                    self.logger.info(f"Accepted cookies using selector: {selector}")
                    time.sleep(2)
                    return True
            except Exception:
                continue

        # Strategy 2: Try clicking on cookie banner
        banner_selectors = [
            "[role='dialog']",
            ".cookie-banner",
            ".cookie-consent",
            ".onetrust-pc-dark-filter",
        ]

        for selector in banner_selectors:
            try:
                banner = self._page.locator(selector).first
                if banner.is_visible(timeout=1000):
                    # Try to find and click any button in the banner
                    buttons = banner.locator("button")
                    count = buttons.count()
                    for i in range(count):
                        btn = buttons.nth(i)
                        if "accept" in btn.text_content().lower():
                            btn.click()
                            self.logger.info("Accepted cookies by clicking button in banner")
                            time.sleep(2)
                            return True
            except Exception:
                continue

        # Strategy 3: Execute JavaScript to accept cookies (OneTrust is common)
        try:
            self._page.evaluate("""
                () => {
                    // Try OneTrust (common cookie consent library)
                    if (typeof OneTrustAcceptAll === 'function') {
                        OneTrustAcceptAll();
                    }
                    // Try to dismiss any overlay
                    var overlays = document.querySelectorAll('[role="dialog"], .modal, .overlay');
                    overlays.forEach(el => {
                        var closeBtn = el.querySelector('button');
                        if (closeBtn) closeBtn.click();
                    });
                }
            """)
            time.sleep(2)
            self.logger.info("Attempted to accept cookies via JavaScript")
        except Exception as e:
            self.logger.warning(f"JavaScript cookie acceptance failed: {e}")

        return False

    def _extract_sid(self):
        """
        Extract _sid cookie from the current page
        """
        try:
            cookies = self._context.cookies()
            for cookie in cookies:
                if cookie.get("name") == "_sid":
                    return cookie.get("value")
        except Exception as e:
            self.logger.error(f"Error extracting _sid: {e}")

        # Fallback: Try to get from document.cookie via JavaScript
        try:
            sid = self._page.evaluate("() => document.cookie.match(/_sid=([^;]*)/)?.[1]")
            return sid
        except Exception as e:
            self.logger.error(f"Error extracting _sid via JavaScript: {e}")

        return None

    def get_page_content(self, url):
        """
        Fetch page content using the browser session with cookies already set
        """
        if not self._page:
            self.logger.error("Page not initialized. Call initialize() first.")
            return None

        try:
            self._page.goto(url, wait_until="networkidle", timeout=60000)
            return self._page.content()
        except Exception as e:
            self.logger.error(f"Error fetching page {url}: {e}")
            return None

    def get_sid(self):
        """
        Get the current _sid value
        """
        return self._sid

    def close(self):
        """
        Close the browser session
        """
        try:
            if self._page:
                self._page.close()
        except Exception:
            pass
        try:
            if self._context:
                self._context.close()
        except Exception:
            pass
        try:
            if self._browser:
                self._browser.close()
        except Exception:
            pass
        try:
            if self._playwright:
                self._playwright.stop()
        except Exception:
            pass

    def __enter__(self):
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
