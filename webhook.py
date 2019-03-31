from pprint import pprint
import requests

import config

BOT_URL = config.BotInfo.BOT_URL
AUTH_TOKEN = config.BotInfo.AUTH_TOKEN

test_url = 'https://ingressfs-stat.serveo.net'

def get_url(method):
    return BOT_URL.format(AUTH_TOKEN,method)

# r = requests.get(get_url("setWebhook"), data={"url": test_url})
r = requests.get(get_url("getWebhookInfo"))
pprint(r.status_code)
pprint(r.json())