import os
import sys
from typing import Optional
from DrissionPage import Chromium, ChromiumOptions
import logging
import time
from enum import Enum
import random
from dotenv import load_dotenv

from browser_utils import BrowserManager
from get_email_code import EmailVerificationHandler

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def save_screenshot(tab, stage: str, timestamp: bool = True) -> None:
    """
    Save a screenshot of the page

    Args:
        tab: Browser tab object
        stage: Stage identifier for the screenshot
        timestamp: Whether to add a timestamp
    """
    try:
        # Create screenshots directory
        screenshot_dir = "screenshots"
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)

        # Generate filename
        if timestamp:
            filename = f"turnstile_{stage}_{int(time.time())}.png"
        else:
            filename = f"turnstile_{stage}.png"

        filepath = os.path.join(screenshot_dir, filename)

        # Save screenshot
        tab.get_screenshot(filepath)
        logging.debug(f"Screenshot saved: {filepath}")
    except Exception as e:
        logging.warning(f"Failed to save screenshot: {str(e)}")

class VerificationStatus(Enum):
    """Verification status enum"""

    PASSWORD_PAGE = "@name=password"
    CAPTCHA_PAGE = "@data-index=0"
    ACCOUNT_SETTINGS = "Account Settings"

class TurnstileError(Exception):
    """Turnstile verification related exception"""

    pass

class Register(object):
    def __init__(self, first_name, last_name, email, password,temp_email_address):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.temp_email_address = temp_email_address
        self.tab= BrowserManager().init_browser(get_user_agent()).latest_tab
        self.sign_up_url = 'https://authenticator.cursor.sh/sign-up'
        self.settings_url = 'https://www.cursor.com/settings'
        self.login_url = 'https://authenticator.cursor.sh'
        
    def register(self):
        print(f"Registering {self.first_name} {self.last_name} with email {self.email} and password {self.password}")
        self.sign_up_account(self.tab)
        return True

    def login(self):
        print(f"Logging in {self.first_name} {self.last_name} with email {self.email} and password {self.password}")


    def sign_up_account_by_login(self, tab):
        self.tab.get(self.login_url)
        self.tab.ele("@name=email").input(self.email)
        self.tab.ele("@type=submit").click()
        time.sleep(random.uniform(2, 3))
        self.tab.ele("xpath://button[@name='intent' and @value='magic-code']").click()
        time.sleep(random.uniform(2, 3))
        handle_turnstile(tab)
        email_handler = EmailVerificationHandler(self.email,self.temp_email_address)
        while True:
            try:
                if tab.ele("Account Settings"):
                    logging.info("Registration successful")
                    break
                if tab.ele("@data-index=0"):
                    logging.info("Getting email verification code")
                    code = email_handler.get_verification_code()
                    if not code:
                        logging.error("Verification code could not be obtained")
                        return False

                    logging.info(f"Verification code received: {code}")
                    logging.info("Inputting verification code")
                    i = 0
                    for digit in code:
                        tab.ele(f"@data-index={i}").input(digit)
                        time.sleep(random.uniform(0.1, 0.3))
                        i += 1
                    logging.info("Verification code input complete")
                    break
            except Exception as e:
                logging.error(f"Verification code process error: {str(e)}")
                return False
        return True

    def sign_up_account(self, tab):
        logging.info("Starting account registration")
        logging.info(f"Visiting registration page: {self.sign_up_url}")
        tab.get(self.sign_up_url)
        email_handler = EmailVerificationHandler(self.email,self.temp_email_address)
        time.sleep(5)
        save_screenshot(tab, "registration_page")
        try:
            if tab.ele("@name=first_name"):
                logging.info("Filling personal information")
                tab.actions.click("@name=first_name").input(self.first_name)
                logging.info(f"Input first name: {self.first_name}")
                time.sleep(random.uniform(1, 2))

                tab.actions.click("@name=last_name").input(self.last_name)
                logging.info(f"Input last name: {self.last_name}")
                time.sleep(random.uniform(1, 2))

                tab.actions.click("@name=email").input(self.email)
                logging.info(f"Input email: {self.email}")
                time.sleep(random.uniform(1, 2))

                logging.info("Submitting personal information")
                tab.actions.click("@type=submit")

        except Exception as e:
            logging.error(f"Registration page access failed: {str(e)}")
            return False

        handle_turnstile(tab)

        try:
            if tab.ele("@name=password"):
                logging.info("Setting password")
                tab.ele("@name=password").input(self.password)
                time.sleep(random.uniform(1, 3))

                logging.info("Submitting password")
                tab.ele("@type=submit").click()
                logging.info("Password setup complete")

        except Exception as e:
            logging.error(f"Password setup failed: {str(e)}")
            return False

        if tab.ele("This email is not available."):
            logging.error("Registration failed: email already in use")
            return False

        handle_turnstile(tab)

        while True:
            try:
                if tab.ele("Account Settings"):
                    logging.info("Registration successful")
                    break
                if tab.ele("@data-index=0"):
                    logging.info("Getting email verification code")
                    code = email_handler.get_verification_code()
                    if not code:
                        logging.error("Verification code could not be obtained")
                        return False

                    logging.info(f"Verification code received: {code}")
                    logging.info("Inputting verification code")
                    i = 0
                    for digit in code:
                        tab.ele(f"@data-index={i}").input(digit)
                        time.sleep(random.uniform(0.1, 0.3))
                        i += 1
                    logging.info("Verification code input complete")
                    break
            except Exception as e:
                logging.error(f"Verification code process error: {str(e)}")
                return False

        handle_turnstile(tab)
        wait_time = random.randint(1, 2)
        for i in range(wait_time):
            logging.info(f"Waiting for system processing: {wait_time-i} seconds remaining")
            time.sleep(1)

        logging.info("Getting account information")
        tab.get(self.settings_url)
        try:
            usage_selector = (
                "css:div.col-span-2 > div > div > div > div > "
                "div:nth-child(1) > div.flex.items-center.justify-between.gap-2 > "
                "span.font-mono.text-sm\\/\\[0\\.875rem\\]"
            )
            usage_ele = tab.ele(usage_selector)
            if usage_ele:
                usage_info = usage_ele.text
                total_usage = usage_info.split("/")[-1].strip()
                logging.info(f"Account usage limit: {total_usage}")
                logging.info(
                    "Please visit the open source project for more information: https://github.com/chengazhen/cursor-auto-free"
                )
        except Exception as e:
            logging.error(f"Failed to get account usage info: {str(e)}")

        logging.info("Registration complete")
        account_info = f"Cursor account info - Email: {self.email}, Password: {self.password}"
        logging.info(account_info)
        time.sleep(5)
        return True

def get_user_agent():
    """Get user_agent"""
    try:
        # Use JavaScript to get user agent
        browser_manager = BrowserManager()
        browser = browser_manager.init_browser()
        user_agent = browser.latest_tab.run_js("return navigator.userAgent")
        browser_manager.quit()
        return user_agent.replace("HeadlessChrome", "Chrome")
    except Exception as e:
        logging.error(f"Failed to get user agent: {str(e)}")
        return None

def check_verification_success(tab) -> Optional[VerificationStatus]:
    """
    Check if verification was successful

    Returns:
        VerificationStatus: The corresponding status if successful, None if failed
    """
    for status in VerificationStatus:
        if tab.ele(status.value):
            logging.info(f"Verification successful: {status.name}")
            return status
    return None

def handle_turnstile(tab, max_retries: int = 2, retry_interval: tuple = (1, 2)) -> bool:
    """
    Handle Turnstile verification

    Args:
        tab: Browser tab object
        max_retries: Maximum number of retries
        retry_interval: Retry interval range (min, max)

    Returns:
        bool: Whether verification was successful

    Raises:
        TurnstileError: Exception during verification process
    """
    logging.info("Detecting Turnstile")

    retry_count = 0

    try:
        while retry_count < max_retries:
            retry_count += 1
            logging.debug(f"Retry verification count: {retry_count}")

            try:
                # Locate verification frame element
                challenge_check = (
                    tab.ele("@id=cf-turnstile", timeout=2)
                    .child()
                    .shadow_root.ele("tag:iframe")
                    .ele("tag:body")
                    .sr("tag:input")
                )

                if challenge_check:
                    logging.info("Detected Turnstile")
                    # Random delay before clicking verification
                    time.sleep(random.uniform(1, 3))
                    challenge_check.click()
                    time.sleep(2)

                    # Check verification result
                    if check_verification_success(tab):
                        logging.info("Turnstile verification passed")
                        return True

            except Exception as e:
                logging.debug(f"Current attempt unsuccessful: {str(e)}")

            # Check if already verified
            if check_verification_success(tab):
                return True

            # Random delay before next attempt
            time.sleep(random.uniform(*retry_interval))

        # Exceeded maximum retries
        logging.error(f"Verification failed after {max_retries} attempts")
        logging.error(
            "Please visit the open source project for more information: https://github.com/chengazhen/cursor-auto-free"
        )
        return False

    except Exception as e:
        error_msg = f"Error during Turnstile verification: {str(e)}"
        logging.error(error_msg)
        raise TurnstileError(error_msg)


class EmailGenerator:
    def __init__(
        self,
        domain: str = None
    ):
        self.domain = domain or os.getenv('EMAIL_DOMAIN', 'zoowayss.eu.org')
        self.names = self.load_names()
        self.default_first_name = self.generate_random_name()
        self.default_last_name = self.generate_random_name()

    def load_names(self):
        try:
            with open("names-dataset.txt", "r") as file:
                return file.read().split()
        except FileNotFoundError:
            logging.warning("names_file_not_found")
            # Fallback to a small set of default names if the file is not found
            return ["John", "Jane", "Alex", "Emma", "Michael", "Olivia", "William", "Sophia", 
                    "James", "Isabella", "Robert", "Mia", "David", "Charlotte", "Joseph", "Amelia"]

    def generate_random_name(self):
        """Generate a random username"""
        return random.choice(self.names)

    def generate_email(self, length=4):
        """Generate a random email address"""
        length = random.randint(0, length)  # Generate a random int between 0 and length
        timestamp = str(int(time.time()))[-length:]  # Use the last length digits of timestamp
        return f"{self.default_first_name}{timestamp}@{self.domain}"
        
    def generate_random_password(self, length=12):
        """Generate a random password"""
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        return "".join(random.choices(chars, k=length))

    def get_account_info(self):
        """Get complete account information"""
        return {
            "email": self.generate_email(),
            "password": self.generate_random_password(),
            "first_name": self.default_first_name,
            "last_name": self.default_last_name,
        }


if __name__ == "__main__":
    
    email_generator = EmailGenerator()
    account_info = email_generator.get_account_info()
    print(account_info)
    register = Register(account_info["first_name"], account_info["last_name"], account_info["email"], account_info["password"])
    register.register()
    register.login()
