import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Mock email sending for development if credentials are not provided
MOCK_MODE = True

class EmailVerifier:
    def __init__(self, sender_email=None, sender_password=None):
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.verification_codes = {} # {email: code}

    def generate_code(self):
        return ''.join(random.choices(string.digits, k=6))

    def send_verification_code(self, receiver_email):
        code = self.generate_code()
        self.verification_codes[receiver_email] = code
        
        subject = "Your Verification Code"
        body = f"Your verification code is: {code}"

        if MOCK_MODE or not self.sender_email or not self.sender_password:
            print(f"--- MOCK EMAIL ---")
            print(f"To: {receiver_email}")
            print(f"Subject: {subject}")
            print(f"Body: {body}")
            print(f"------------------")
            return True

        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = receiver_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            text = msg.as_string()
            server.sendmail(self.sender_email, receiver_email, text)
            server.quit()
            return True
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False

    def verify_code(self, email, code):
        if email in self.verification_codes:
            if self.verification_codes[email] == code:
                del self.verification_codes[email] # One-time use
                return True
        return False
