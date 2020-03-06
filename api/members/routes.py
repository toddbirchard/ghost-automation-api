from flask import current_app as api
from flask import make_response, request, jsonify
from mixpanel import Mixpanel
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Email, Mail


@api.route('/members/mixpanel', methods=['POST'])
def subscriber_mixpanel():
    """Create Mixpanel profile for new subscriber."""
    mp = Mixpanel(api.config['mixpanel_api_token'])
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    if email:
        body = {'$name': name, '$email': email}
        mp.people_set(email, body)
        return make_response(jsonify({'CREATED': body}))
    return make_response(jsonify({'DENIED': data}))


@api.route('/members/welcome', methods=['POST'])
def subscriber_welcome_email():
    """Send welcome email to newsletter subscribers."""
    sg = SendGridAPIClient(api_key=api.config['SENDGRID_API_KEY'])
    sender = Email(api.config['SENDGRID_FROM_EMAIL'])
    data = request.get_json()
    subscribers = data['subscribers']
    for subscriber in subscribers:
        recipient = Email(subscriber['email'])
        subject = "Welcome to Hackers & Slackers"
        mail = Mail(sender, subject, recipient)
        mail.template_id = api.config['SENDGRID_TEMPLATE_ID']
        sg.client.mail.send.post(request_body=mail.get())
    return make_response(jsonify({'SUCCESS': data}))
