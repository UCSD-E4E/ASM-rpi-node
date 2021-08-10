# DESCRIPTION: Send email alert to E4E team when error is detected.

import smtplib, ssl
# import getpass

port = 465 # for SSL
smtp_server = "smtp.gmail.com"
sender_email = ""
receiver_emails = ["", ""]
#password = getpass.getpass(prompt="Type your password and press enter: ")
password = ""
#message = "sample message"


class MailAlert:
    def time_alert(self):
        message = "From: Aye Aye Sensor System \nSubject: Arduino Error: Time Between Sent Packets Exceeded \n\nArduino Error: Time between sent packets has exceeded acceptable limit."

        # Create a secure SSL context
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context = context) as server:
            server.login("", password)
            server.sendmail(sender_email, receiver_emails, message)

    def empty_alert(self):
        message = "From: Aye Aye Sensor System \nSubject: Arduino Error: Empty Packets Detected \n\nArduino Error: Empty packets detected."

        # Create a secure SSL context
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context = context) as server:
            server.login("", password)
            server.sendmail(sender_email, receiver_emails, message)

