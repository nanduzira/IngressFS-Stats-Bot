import requests
from flask import Flask, request
from datetime import datetime
import config
import locale


BOT_URL = config.BotInfo.BOT_URL
BOT_FILE_URL = config.BotInfo.BOT_FILE_URL
AUTH_TOKEN = config.BotInfo.AUTH_TOKEN
BCKP_DIR = config.BotInfo.BCKP_DIR

EVENT_TITLE = config.BotInfo.EVENT_TITLE
EVENT_START_TIME = config.BotInfo.EVENT_START_TIME
EVENT_END_TIME = config.BotInfo.EVENT_END_TIME

AGENT_STATS_DATA = {
    'username': {
        'chat-id': '',
        'faction': '',
        'start': {
            'level':15,
            'ap': 24000000,
            'trekker': 893,
            'stats_img': False,
            'updated': False
        },
        'end': {
            'level':15,
            'ap': 24000000,
            'trekker': 893,
            'stats_img': False,
            'updated': False
        }
    }
}

locale.setlocale(locale.LC_ALL, 'en_US.utf8')

app = Flask(__name__)
app.config.from_object(config.DevConfig)

def get_url(bot_url, method):
  return bot_url.format(AUTH_TOKEN,method)

def set_faction(username, faction):
    if 'res' in faction or 'resistance' in faction:
        AGENT_STATS_DATA[username]['faction'] = 'RES'
        response_text = "*AGENT @{0},*\n\nYour Faction alignment is set to *Resistance*.".format(username)
    elif 'enl' in faction or 'enlightened' in faction:
        AGENT_STATS_DATA[username]['faction'] = 'ENL'
        response_text = "*AGENT @{0},*\n\nYour Faction alignment is set to *Enlightened*.".format(username)
    else:
        response_text = "*AGENT @{0},*\n\nYour Faction alignment wasn't able to be recognized. Please try to set your Faction using:\n\t\t\t`/faction Resistance`\n\t\t\t`/faction Enlightened`".format(username)
    print('AGENT STATS :{}'.format(AGENT_STATS_DATA))

    return response_text

def set_stat(username, stat_name, stat_val):
    val = stat_val[len(stat_name)+2:]
    if  not AGENT_STATS_DATA[username]['start']['updated']:
        if val.isdigit():
            AGENT_STATS_DATA[username]['start'][stat_name] = int(val)
            response_text = "*AGENT @{0},*\n\nYour Starting {1} is set to {2}".format(username, stat_name, locale.format('%d', AGENT_STATS_DATA[username]['start'][stat_name], grouping=True))
        else:
            response_text = "*AGENT @{0},*\n\nYour Starting {1} wasn't able to be recognized. Please try to set your {1} using:\n\t\t\t`/{1} ##`".format(username, stat_name)
    elif datetime.now() >= EVENT_END_TIME and not AGENT_STATS_DATA[username]['end']['updated']:
        if val.isdigit():
            AGENT_STATS_DATA[username]['end'][stat_name] = int(val)
            response_text = "*AGENT @{0},*\n\nYour Ending {1} is set to {2}".format(username, stat_name, locale.format('%d', AGENT_STATS_DATA[username]['end'][stat_name], grouping=True))
        else:
            response_text = "*AGENT @{0},*\n\nYour Ending {1} wasn't able to be recognized. Please try to set your {1} using:\n\t\t\t`/{1} ##`".format(username, stat_name)
    else:
        response_text = "Event have not been ended yet. *#IngressFS Stats Bot* will accept Ending Stats at {0}".format(EVENT_END_TIME.strftime('%Y/%m/%d %H:%M:%S'))
    
    return response_text


def process_text(username, chat_id, text):
    if username not in AGENT_STATS_DATA:
        AGENT_STATS_DATA[username] = {
            'chat-id': chat_id,
            'start': {
                'stats_img': False,
                'updated': False
            },
            'end': {
                'stats_img': False,
                'updated': False
            }
        }
    if text.startswith('/start'):
        response_text = "*Welcome Agent @{0},*\n\n#IngressFS Stats Bot will help you guide through your registration process for *{1}*. Now has a first step, Set your Faction using:\n\t\t\t`/faction Resistance`\n\t\t\t`/faction Enlightened`".format(username, EVENT_TITLE)
    elif text.startswith('/faction'):
        set_faction(username, text.lower())
        response_text = set_faction(username, text.lower())
    elif '/level' in text:
        response_text = set_stat(username, 'level', text.lower())
    elif '/ap' in text:
        response_text = set_stat(username, 'ap', text.lower())
    elif '/trekker' in text:
        response_text = set_stat(username, 'trekker', text.lower())
    elif '/save' in text:
        response_text = "Save Received"
    elif '/reset' in text:
        response_text = "Reset Received"
    elif '/help' in text:
        response_text = "Help Received"
    else:
        response_text = "*#IngressFS Stats Bot* ain't currently supporting communication with a Human Being..... ^_^"
    
    return response_text

def process_message(message):
    data = dict()
    data["chat_id"] = message["from"]["id"]
    data['parse_mode'] = "Markdown"

    if datetime.now() >= EVENT_START_TIME:
        if 'text' in message:
            data['text'] = process_text(message['chat']['username'], message["from"]["id"], message['text'])
        elif 'photo' in message:
            data['text'] = "Bot currently is not able to recognize Compressed Images properly.\nPlease send the same has a file without any sort of Compression...!!!"
        else:
            data['text'] = "Unrecognized Content....!!!. Please follow the basic steps suggested by the Bot.\n\nFor more info try out the /help command"
    else:
        data['text'] = "Event have not been started yet. *#IngressFS Stats Bot* will be accepting Stats at {0}".format(EVENT_START_TIME.strftime('%Y/%m/%d %H:%M:%S'))
    print("DATA :{}".format(data))
    r = requests.post(get_url(BOT_URL, "sendMessage"), data=data)

@app.route("/", methods=["POST"])
def post_handler():
    if request.method == "POST":
        update = request.get_json()
        print("UPDATE :{}".format(update))

        if 'message' in update:
            process_message(update['message'])
        return "ok!", 200


if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000)