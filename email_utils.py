import random
import string

class EmailVerifier:
    def __init__(self):
        """
        Initialize EmailVerifier for console-based verification.
        No credentials required.
        """
        self.verification_codes = {} # {email: code}

    def generate_code(self):
        return ''.join(random.choices(string.digits, k=6))

    def send_verification_code(self, receiver_email):
        code = self.generate_code()
        self.verification_codes[receiver_email] = code
        
        print("\n" + "="*60)
        print("🔐 NEXUS VERIFICATION CODE")
        print("="*60)
        print(f"To: {receiver_email}")
        print(f"Code: {code}")
        print("="*60 + "\n")
        
        return True

    def verify_code(self, email, code):
        if email in self.verification_codes:
            if self.verification_codes[email] == code:
                del self.verification_codes[email] # One-time use
                return True
        return False
