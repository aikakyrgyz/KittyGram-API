from django.core.mail import send_mail


def send_activation_code(email, activation_code):
    activation_url = f'http://localhost:8000/api/account/activate/{activation_code}'
    message = f"""
    Thank you for registering.
    Please activate your account. Activation Link: {activation_url}"""
    send_mail('Activate your account', message, 'test@test.com', [email, ], fail_silently=False)

def send_activation_email(email, activation_code):
    activation_url = f'http://localhost:8000/api/account/activate/{activation_code}'
    message = f"""
    Reset your password.
    Activation Link: {activation_url}"""
    send_mail('Activate your account', message, 'test@test.com', [email, ], fail_silently=False)