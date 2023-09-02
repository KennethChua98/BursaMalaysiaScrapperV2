from selenium import webdriver
from fake_useragent import UserAgent

# avoid getting blocked or detected by the website
ua = UserAgent()
options = webdriver.ChromeOptions()
# known issus usb_service_win.cc:415 but it is not affecting the program
# therefore suppress the error message
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.headless = True
options.add_argument("--disable-gpu")  # Disable GPU acceleration (optional)
options.add_argument("--blink-settings=imagesEnabled=false")  # Disable image loading
options.add_argument(f"user-agent={ua.random}")
