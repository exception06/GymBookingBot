from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os

load_dotenv()
# Create Chrome Profile and create account manually. Put YOUR email and password here:
ACCOUNT_EMAIL = os.getenv("ACCOUNT_EMAIL")
ACCOUNT_PASSWORD = os.getenv("ACCOUNT_PASSWORD")
GYM_URL = "https://appbrewery.github.io/gym/"

# Configure Selenium to stay open using the Chrome option
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

# Create profile directory
user_data_dir = os.path.join(os.getcwd(), "chrome_profile")

# Set up Chrome options
chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

# Launch Chrome with persistent profile
driver = webdriver.Chrome(options=chrome_options)
driver.get(GYM_URL)

# ---------------- Automated Login ----------------

wait = WebDriverWait(driver=driver, timeout=2)

# Click the login button
try:
    login_button = wait.until(EC.element_to_be_clickable((By.ID, "login-button")))
    login_button.click()
except NoSuchElementException:
    print("The Login is not successful.")
    
# Enter the email and the password
email_ip = wait.until(EC.element_to_be_clickable((By.ID, "email-input")))
email_ip.clear()
email_ip.send_keys(ACCOUNT_EMAIL)

password_ip = driver.find_element(By.ID, "password-input")
password_ip.clear()
password_ip.send_keys(ACCOUNT_PASSWORD)

submit_btn = driver.find_element(By.ID, value="submit-button")
submit_btn.click()

wait.until(EC.presence_of_all_elements_located((By.ID, "schedule-page")))# Look wether next page is loaded
class_cards = driver.find_elements(By.CSS_SELECTOR, "div[id^='class-card-']")

# Counts for the bookings
booked_count = 0
waitlist_count = 0
already_booked_count = 0
total_processed = 0

processed_classes = []
TARGET_DAYS = ["Tue", "Thu"]
TARGET_TIME = "6:00 PM"
for card in class_cards:
    day_group = card.find_element(By.XPATH, "./ancestor::div[contains(@id, 'day-group-')]")
    day_title = day_group.find_element(By.TAG_NAME, "h2").text

    # Check if this is a Tuesday OR Thursday
    if TARGET_DAYS[0] in day_title or TARGET_DAYS[1] in day_title:
        time_text = card.find_element(By.CSS_SELECTOR, "p[id^='class-time-']").text
        if TARGET_TIME in time_text:
            class_name = card.find_element(By.CSS_SELECTOR, "h3[id^='class-name-']").text
            button = card.find_element(By.CSS_SELECTOR, "button[id^='book-button-']")

            # Track the class details
            class_info = f"{class_name} on {day_title}"

            if button.text == "Booked":
                print(f"✓ Already booked_count: {class_info}")
                already_booked_count += 1
                # Add detailed class info
                processed_classes.append(f"[Booked] {class_info}")
            elif button.text == "Waitlisted":
                print(f"✓ Already on waitlist: {class_info}")
                already_booked_count += 1
                # Add detailed class info
                processed_classes.append(f"[Waitlisted] {class_info}")
            elif button.text == "Book Class":
                button.click()
                print(f"✓ Successfully booked_count: {class_info}")
                booked_count += 1
                # Add detailed class info
                processed_classes.append(f"[New Booking] {class_info}")
                sleep(0.5)
            elif button.text == "Join Waitlist":
                button.click()
                print(f"✓ Joined waitlist for: {class_info}")
                waitlist_count += 1
                # Add detailed class info
                processed_classes.append(f"[New Waitlist] {class_info}")
                sleep(0.5)
total_count = booked_count+waitlist_count+already_booked_count
print(f"""
--- BOOKING SUMMARY ---
Classes booked: {booked_count}
Waitlists joined: {waitlist_count}
Already booked/waitlisted: {already_booked_count}
Total Tuesday 6pm classes processed: {total_count}
""")

# Going onto the next page
try:
    my_bookings = driver.find_element(By.ID, "my-bookings-link")
    my_bookings.click()
except NoSuchElementException:
    print("❌ Could not find 'My Bookings' link.")
    driver.quit()


# Locate the confirmed bookings section
section_bookings = driver.find_elements(By.CSS_SELECTOR, value='.MyBookings_bookingCard__VRdrR')
section_name = []

for section in section_bookings:
    if len(section_bookings) == booked_count+waitlist_count+already_booked_count:
        section_name_element = section.find_element(By.TAG_NAME, value="h3")
        section_name.append(section_name_element)

# Verification of the classes
print("--- VERIFYING ON MY BOOKINGS PAGE ---")
for name in section_name:
    print(f"""
  ✓ Verified: {name.text}""")

print(f"""
--- VERIFICATION RESULT ---
Expected: {total_count}
Found: {len(section_bookings)}""")

if total_count == len(section_bookings):
    print("✅ SUCCESS: All bookings verified!")
else:
    print("❌ MISMATCH: Missing -1 bookings")

#driver.close()
