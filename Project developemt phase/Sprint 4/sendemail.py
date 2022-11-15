import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail,To

def sendgridmail(user):
    message = Mail(
        from_email=os.environ.get('SENDER_EMAIL'),
        to_emails=To(user),
        subject='Your Monthly expense is exceeded',
        html_content='<strong>Avoid spending money, your monthly expense is exceeded...</strong>')
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)