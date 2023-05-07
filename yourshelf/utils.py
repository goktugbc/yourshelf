import traceback
def send_mail(title, body, sender, receiver):
    from django.core.mail import EmailMessage
    try:
        mail = EmailMessage(title, body, sender, receiver)
        mail.content_subtype = "html"
        mail.send(fail_silently=False)
        return "Success"
    except Exception as e:
        return traceback.format_exc()