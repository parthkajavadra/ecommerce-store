import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from io import BytesIO


SENDGRID_API_KEY = 'your_sendgrid_api_key'  # Store this in an env variable

def send_invoice_email(user_email: str, pdf_invoice: BytesIO):
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    from_email = Email("your_email@example.com")  # Use your email address here
    to_email = To(user_email)
    subject = "Your Invoice"
    content = Content("text/plain", "Please find your invoice attached.")

    # Create the email message
    message = Mail(from_email, to_email, subject, content)

    # Attach the PDF invoice
    message.add_attachment(
        pdf_invoice.getvalue(),
        "application/pdf",
        "invoice.pdf",
        "attachment"
    )

    # Send the email
    response = sg.send(message)
    return response
