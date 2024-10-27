from twilio.rest import Client
import smtplib
import os
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

class Checker:
    def __init__(self):
        if os.getenv("GITHUB_ACTIONS") == "true":
            chrome_options = Options()
            self.driver = webdriver.Chrome(options=chrome_options)
        else:
            self.driver = webdriver.Chrome(service=Service("/Users/leon/projects/selenium/chromedriver"))


    def process(self):
        try:
            self.driver.get("https://pio-przybysz.duw.pl/login")
            sleep(5)
            self.driver.find_element(By.ID, "mat-input-0").send_keys(os.getenv('EMAIL_TO'))
            self.driver.find_element(By.ID,"mat-input-1").send_keys(os.getenv('KP_PASSWORD'))
            self.driver.find_element(By.XPATH, "//button[text()='Zaloguj']").click()
            sleep(5)
            self.driver.get("https://pio-przybysz.duw.pl/szczegoly-wniosku/81463")
            sleep(5)
        except Exception as e:
            self.send_email(f"Error in process: {e}")
            return

        if "Pismo w sprawie – braki formalne" in self.driver.page_source:
            self.send_all("KP status still not changed!")
        else:
            self.send_all("KP status has been changed!")
        self.driver.quit()

    def send_sms(self, message):
        client = Client(os.getenv('SID'), os.getenv('TOKEN'))
        message = client.messages.create(to=os.getenv('MY_NUMBER'), from_=os.getenv('VIRTUAL_NUMBER'), body=message)

    def send_email(self, message):
        subject = "KP Status auto email"
        msg_body = message
        msg = f"Subject: {subject}\n\n{msg_body}"

        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=os.getenv('EMAIL_USER'), password=os.getenv('EMAIL_PASSWORD'))
            connection.sendmail(from_addr=os.getenv('EMAIL_USER'), to_addrs=os.getenv('EMAIL_TO'), msg=msg)

    def send_all(self, message):
        try:
            self.send_sms(f"{message}")
        except Exception as e:
            self.send_email(f"Error in sending SMS: {e}")
        finally:
            self.send_email(f"{message}")


Checker().process()