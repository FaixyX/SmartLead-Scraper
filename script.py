from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time


# Credentials from config.py
CSV_FILE_PATH = "accounta.csv"
DRIVER_PATH = "C:\\drivers\\chromedriver.exe"
SMARTLEAD_EMAIL = "abc@xyz.com"
SMARTLEAD_PASSWORD = "password"


# GmailAccount class to store Gmail credentials
class GmailAccount:
    def __init__(self, email, password):
        self.email = email
        self.password = password


class BrowserAutomation:
    def __init__(self, driver_path):
        self.driver_path = driver_path
        self.driver = None


    def start_browser(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--start-maximized")


        service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)


    def quit_browser(self):
        if self.driver:
            self.driver.quit()


    def wait_and_find_element(self, by, locator, timeout=15, condition="presence"):
        try:
            if condition == "clickable":
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((by, locator))
                )
            elif condition == "visible":
                element = WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located((by, locator))
                )
            else:  # presence
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, locator))
                )
            return element
        except TimeoutException:
            print(f"Timeout waiting for element: {locator}")
            raise


    def enter_text(self, by, locator, text):
        try:
            element = self.wait_and_find_element(by, locator, condition="visible")
            element.clear()
            element.send_keys(text)
        except TimeoutException:
            print(f"Failed to find element to enter text: {locator}")
            raise


    def click_element(self, by, locator):
        try:
            element = self.wait_and_find_element(by, locator, condition="clickable")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].click();", element)
        except TimeoutException:
            print(f"Failed to click element: {locator}")
            raise


    def aggressive_scroll_to_bottom(self):
        """Scroll aggressively to the bottom of the page using multiple methods."""
        try:
            print("Aggressively scrolling to the bottom of the page...")


            # Focus on the page
            self.driver.find_element(By.TAG_NAME, 'body').click()


            # Aggressive scroll using JavaScript
            for _ in range(10):
                self.driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(0.1)


            # Scroll using ActionChains (simulate real mouse scroll)
            actions = ActionChains(self.driver)
            for _ in range(20):
                actions.send_keys(Keys.PAGE_DOWN).perform()
                time.sleep(0.1)


            # Final scroll to ensure we reach the very bottom
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(1)


            print("Reached the bottom of the page.")
        except Exception as e:
            print(f"Error while scrolling to the bottom: {e}")


    def process_gmail_account(self, gmail_account):
        try:
            # Step 1: Go to Google sign-in page
            print(f"Navigating to Google sign-in for account: {gmail_account.email}")
            self.driver.get("https://gmail.com")
            time.sleep(2)


            # Step 2: Enter the email and click 'Next'
            print("Entering email...")
            self.enter_text(By.ID, "identifierId", gmail_account.email)
            self.click_element(By.ID, "identifierNext")
            time.sleep(2)


            # Step 3: Enter the password
            print("Entering password...")
            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
            )
            password_field.send_keys(gmail_account.password)
            password_field.send_keys(Keys.RETURN)
            time.sleep(1)


            # Step 4: Handle Confirmation Page (if present)
            try:
                print("Checking for confirmation page...")
                # Aggressively scroll to the bottom
                self.aggressive_scroll_to_bottom()


                # Click 'Entendido' or 'I understand' button if present
                entendido_button = self.wait_and_find_element(
                    By.XPATH, "//input[@id='confirm' and (@value='Entendido' or @value='I understand')]", timeout=10, condition="clickable"
                )
                if entendido_button:
                    print("Clicking confirmation button...")
                    self.driver.execute_script("arguments[0].click();", entendido_button)
                    time.sleep(1)
            except TimeoutException:
                print("Confirmation page not found. Proceeding...")


            print("Gmail account successfully processed.")
            return True


        except TimeoutException as te:
            print(f"Timeout occurred: {te}")
            return False
        except NoSuchElementException as nse:
            print(f"Element not found: {nse}")
            return False
        except ElementNotInteractableException as eni:
            print(f"Element not interactable: {eni}")
            return False
        except Exception as e:
            print(f"Error during Gmail account processing: {e}")
            return False


    def process_smartlead_account(self, smartlead_email, smartlead_password):
        try:
            # Step 1: Navigate to Smartlead
            print("Navigating to Smartlead login page...")
            self.driver.get("https://app.smartlead.ai")
            time.sleep(1)  # Increased time for page load


            # Step 2: Log in to Smartlead
            print("Logging into Smartlead...")
            self.enter_text(By.NAME, "email", smartlead_email)
            self.enter_text(By.NAME, "password", smartlead_password)
            self.click_element(By.XPATH, "//button[@type='submit']")
            time.sleep(2)  # Give time for login and redirect


            # Step 3: Navigate to email accounts page
            print("Navigating to email accounts page...")
            self.driver.get("https://app.smartlead.ai/app/email-accounts/emails")
            time.sleep(3)
           
            print("Page source before clicking 'Add Account' button:")
            print(self.driver.page_source)


            # Step 4: Click "Add Account" button with enhanced troubleshooting
            print("Clicking 'Add Account' button...")


            try:
                # Ensure the page is fully loaded
                time.sleep(2)  # Add more delay if necessary


                # Hide any overlays that might block interaction
                self.driver.execute_script(
                    "document.querySelectorAll('.bb-feedback-button, .gleap-notification-container').forEach(el => el.style.display = 'none');"
                )


                # Wait for the button to be present, then scroll into view and click
                add_account_button = self.wait_and_find_element(
                    By.XPATH, "//span[text()='Add Account(s)']/..",
                    timeout=20,
                    condition="clickable"
                )


                # Scroll the button into view to make sure it's visible
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_account_button)
                time.sleep(0.5)  # Pause to allow any rendering adjustments


                # Attempt to click the button using JavaScript
                self.driver.execute_script("arguments[0].click();", add_account_button)
                print("'Add Account' button clicked.")


                # Wait briefly to ensure any loading or transition occurs
                time.sleep(3)


            except TimeoutException:
                print("Timeout: 'Add Account' button was not found.")
            except Exception as e:
                print(f"Failed to click 'Add Account' button: {e}")




            # Step 5: Click the "Select" button
            print("Clicking 'Select' button...")
            select_button = self.wait_and_find_element(By.XPATH, "//button[contains(@class, 'select-btn')]//span[text()='Select']", timeout=15, condition="clickable")
            self.click_element(By.XPATH, "//button[contains(@class, 'select-btn')]//span[text()='Select']")
            time.sleep(1)


            # Step 6: Click OAuth button (Gmail icon)
            print("Clicking OAuth button...")


            try:
                # Ensure the page is fully loaded
                time.sleep(2)


                # Hide any overlays that might block interaction
                self.driver.execute_script(
                    "document.querySelectorAll('.bb-feedback-button, .gleap-notification-container').forEach(el => el.style.display = 'none');"
                )


                # Locate the OAuth button with a precise XPath targeting the Gmail icon
                oauth_button = self.wait_and_find_element(
                    By.XPATH,
                    "//div[@class='add-account-card-big']//div[contains(@class, 'email-provider-icon')]",
                    timeout=15,
                    condition="clickable"
                )


                # Scroll the button into view to ensure visibility
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", oauth_button)
                time.sleep(0.5)  # Short delay to account for scrolling adjustments


                # Attempt the first click using JavaScript
                self.driver.execute_script("arguments[0].click();", oauth_button)
                print("First click on OAuth button.")


                # Short delay before a second click
                time.sleep(1)


                # Second click using JavaScript to ensure action registers
                self.driver.execute_script("arguments[0].click();", oauth_button)
                print("Second click on OAuth button.")


                # Additional delay to allow any subsequent loading or transitions
                time.sleep(3)


            except TimeoutException:
                print("Timeout: OAuth button was not found.")
            except Exception as e:
                print(f"Failed to click OAuth button: {e}")




            # Step 7: Click Connect Account
            print("Clicking 'Connect Account' button...")
            connect_account_button = self.wait_and_find_element(By.XPATH, "//button[contains(@class, 'bg-primary') and .//span[text()='Connect Account']]", timeout=15, condition="clickable")
            self.driver.execute_script("arguments[0].click();", connect_account_button)
            time.sleep(2)


            # Step 8: Select Google Account
            print("Selecting Google account...")
            google_account_element = self.wait_and_find_element(By.XPATH, "//div[@role='link' and contains(@class, 'VV3oRb')]", timeout=15, condition="clickable")
            self.driver.execute_script("arguments[0].click();", google_account_element)
            time.sleep(1)


            # Step 9: Click Continue
            print("Clicking 'Continue' button...")
            continue_button = self.wait_and_find_element(By.XPATH, "//button[.//span[text()='Continuar']]", timeout=15, condition="clickable")
            self.driver.execute_script("arguments[0].click();", continue_button)
            time.sleep(1)


            # Step 10: Click Allow Permission
            print("Clicking 'Allow' button...")
            allow_button = self.wait_and_find_element(By.XPATH, "//span[@jsname='V67aGc' and text()='Permitir']", timeout=15, condition="clickable")
            self.driver.execute_script("arguments[0].click();", allow_button)
            time.sleep(2)


            print("Smartlead account successfully linked.")
            return True


        except TimeoutException as te:
            print(f"Timeout occurred: {te}")
            return False
        except NoSuchElementException as nse:
            print(f"Element not found: {nse}")
            return False
        except ElementNotInteractableException as eni:
            print(f"Element not interactable: {eni}")
            return False
        except Exception as e:
            print(f"Error during Smartlead account processing: {e}")
            return False
        finally:
            print("Smartlead processing completed.")


# Instantiate the automation class and run processes
if __name__ == "__main__":
    automation = BrowserAutomation(DRIVER_PATH)
    automation.start_browser()
    try:
        gmail_account = GmailAccount(email="spitzke@managementforthevision.com", password="your_password_here")
        success = automation.process_gmail_account(gmail_account)


        if success:
            print("Gmail processing completed successfully. Proceeding to Smartlead...")
            automation.process_smartlead_account(SMARTLEAD_EMAIL, SMARTLEAD_PASSWORD)
        else:
            print("Gmail processing failed. Skipping Smartlead setup.")


    finally:
        automation.quit_browser()



