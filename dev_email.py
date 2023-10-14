import requests

from utils import email_api

def send_email(compute_type, time=0):
	return requests.post(
		"https://api.mailgun.net/v3/sandbox4574654266a44ce996b1a806a3ff1f06.mailgun.org/messages",
		auth=("api", email_api),
		data={"from": "Mailgun Sandbox <postmaster@sandbox4574654266a44ce996b1a806a3ff1f06.mailgun.org>",
			"to": "Development <dev@jcrayb.com>",
			"subject": f"Computation finished",
			"text": compute_type})