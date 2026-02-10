import os
from flask import Flask
from flask_mail import Mail, Message
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Email Configuration from .env
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

mail = Mail(app)

def test_email():
    print("--- Testing Email Configuration ---")
    print(f"Server: {app.config['MAIL_SERVER']}")
    print(f"Port: {app.config['MAIL_PORT']}")
    print(f"User: {app.config['MAIL_USERNAME']}")
    
    if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
        print("\n[ERROR] Email credentials missing in .env file!")
        return

    recipient = input("\nEnter recipient email address for test: ")
    
    with app.app_context():
        msg = Message("NK Automobiles - Test Email", recipients=[recipient])
        msg.body = "This is a test email from the NK Automobiles system to verify your SMTP configuration."
        
        try:
            print(f"Attempting to send email to {recipient}...")
            mail.send(msg)
            print("\n[SUCCESS] Email sent successfully!")
        except Exception as e:
            print(f"\n[FAILED] Error sending email: {e}")
            print("\nTroubleshooting Tips:")
            print("1. If using Gmail, use an 'App Password', NOT your regular password.")
            print("2. Ensure 'Less secure app access' is handled (Google now requires App Passwords).")
            print("3. Check if your ISP blocks port 587.")

if __name__ == "__main__":
    test_email()
