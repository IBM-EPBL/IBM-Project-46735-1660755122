import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail,To, Email

def sendgridmail(user):
    message = Mail(
        from_email=Email("personalexpensetracker99@gmail.com"),
        to_emails=To(user),
        subject='Your Monthly expense is exceeded',
        html_content='<strong>Avoid spending money, your monthly expense is exceeded...</strong>')
    try:
        sg = SendGridAPIClient('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')
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)