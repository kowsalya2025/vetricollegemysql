import sendgrid
import os
from sendgrid.helpers.mail import Mail

sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))

message = Mail(
    from_email='kowsalyacse1992@gmail.com',
    to_emails='kowsalyacse1992@gmail.com',
    subject='SendGrid Test Email',
    html_content='<h1>It works!</h1><p>SendGrid is configured correctly.</p>'
)

response = sg.send(message)
print(f"Status: {response.status_code}")  # Should print 202