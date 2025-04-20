import os, smtplib
from dotenv import load_dotenv

load_dotenv()
user = 'it@awhbharat.org'
pwd = 'kn10PijpNTQ4'
print("Attempting SSL connect to smtp.zoho.com:465 …")
msg = "random test message"
msg = MIMEMultipart('related')
msg['Subject'] = "Your AWH Digital Visiting Card"
msg['From']    = ZOHO_USER
msg['To']      = to_addr
msg.attach(MIMEText(html, 'html'))
try:
    with smtplib.SMTP_SSL('smtp.zoho.in', 465) as smtp:
        smtp.login(user, pwd)
        
    print("✅ SSL login successful!")
except Exception as e:
    print("❌ SSL login failed:", e)

print("\nAttempting STARTTLS connect to smtp.zoho.com:587 …")

with smtplib.SMTP('smtp.zoho.in', 587) as smtp:
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login(user, pwd)
    smtp.send_message(msg)
   
