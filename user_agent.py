from selenium import webdriver
from fake_useragent import UserAgent

#avoid getting blocked or detected by the website
ua = UserAgent()
user_agent = ua.random

options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={user_agent}")