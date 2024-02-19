import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


from os.path import join, dirname
from dotenv import load_dotenv
import os

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


MAIL_PASS = os.environ.get('MAIL_PASS')

def send_email(receiver_email, subject, message_content, 
               sender_email="axisbank.hrteam123@gmail.com", 
               sender_password=MAIL_PASS):
    
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject

    body = MIMEText(message_content, 'plain')
    message.attach(body)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Change the server and port accordingly
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())

        print("Email sent successfully!")

    except Exception as e:
        print("Error sending email:", str(e))

    finally:
        server.quit()

