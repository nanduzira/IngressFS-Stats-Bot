import requests
import threading
from flask import Flask, request
from datetime import datetime, timedelta
import locale
import json

import config
from spreadsheet import Spreadsheet

BOT_URL = config.BotInfo.BOT_URL
BOT_FILE_URL = config.BotInfo.BOT_FILE_URL
AUTH_TOKEN = config.BotInfo.AUTH_TOKEN
BCKP_DIR = config.BotInfo.BCKP_DIR

EVENT_TITLE = config.BotInfo.EVENT_TITLE
EVENT_START_TIME = config.BotInfo.EVENT_START_TIME
EVENT_END_TIME = config.BotInfo.EVENT_END_TIME

LOCAL_START_TIME = EVENT_START_TIME + timedelta(hours=5, minutes=30)
LOCAL_END_TIME = EVENT_END_TIME + timedelta(hours=5, minutes=30)

SHEET_CREDS =config.BotInfo.SHEET_CREDS
SHEET_ID = config.BotInfo.SHEET_ID
SHEET_URL = config.BotInfo.SHEET_URL

AGENT_STATS_DATA = dict()

locale.setlocale(locale.LC_ALL, 'en_US.utf8')

stat_sheet = Spreadsheet(SHEET_CREDS)
sheet_fields = {
    'ENL': {
        'name': 'L{0}',
        'start': 'L{0}:O{1}',
        'end': 'P{0}:R{1}',
        'res': 'H{0}:J{1}'
    },
    'RES': {
        'name': 'A{0}',
        'start': 'A{0}:D{1}',
        'end': 'E{0}:G{1}',
        'res': 'S{0}:U{1}'
    }
}
app = Flask(__name__)
app.config.from_object(config.DevConfig)

def synchronized(func):

    func.__lock__ = threading.Lock()

    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func

def get_url(bot_url, method):
  return bot_url.format(AUTH_TOKEN,method)

def set_faction(username, faction):
    if 'res' in faction or 'resistance' in faction:
        AGENT_STATS_DATA[username]['faction'] = 'RES'
        response_text = f"Your Faction alignment is set to *{AGENT_STATS_DATA[username]['faction']}*."
    elif 'enl' in faction or 'enlightened' in faction:
        AGENT_STATS_DATA[username]['faction'] = 'ENL'
        response_text = f"Your Faction alignment is set to *{AGENT_STATS_DATA[username]['faction']}*."
    else:
        response_text = "Your Faction alignment wasn't able to be recognized. Please try to set your Faction using:\n\t\t\t`/faction Resistance`\n\t\t\t`/faction Enlightened`"

    return response_text

def set_stat(username, stat_name, stat_val):
    val = stat_val[len(stat_name)+2:]
    if  not AGENT_STATS_DATA[username]['start']['saved']:
        if val.isdigit():
            AGENT_STATS_DATA[username]['start'][stat_name] = int(val)
            response_text = "Your Starting {0} is set to {1}".format(stat_name, locale.format('%d', AGENT_STATS_DATA[username]['start'][stat_name], grouping=True))
        else:
            response_text = "Your Starting {0} wasn't able to be recognized. Please try to set your {0} using:\n\t\t\t`/{0} ##`".format(stat_name)
    elif not AGENT_STATS_DATA[username]['end']['saved']:
        if datetime.now() <= EVENT_END_TIME:
            return "Event have not been ended yet...!!!\n\n*#IngressFS Stats Bot* will accept Ending Stats at {0}".format(LOCAL_END_TIME.strftime('%d %b, %Y %I:%M%p'))

        if val.isdigit():
            AGENT_STATS_DATA[username]['end'][stat_name] = int(val)
            response_text = "Your Ending {0} is set to {1}".format(stat_name, locale.format('%d', AGENT_STATS_DATA[username]['end'][stat_name], grouping=True))
        else:
            response_text = "Your Ending {0} wasn't able to be recognized. Please try to set your {0} using:\n\t\t\t`/{0} ##`".format(stat_name)
    else:
        response_text = "Both Start & End Stats are saved. Good work Agent....!!!. Contact @NaNDuzIRa for any queries:"

    return response_text

def get_info(username):
    info = '*AGENT STATS INFO*\n\n\t\t_Agent Name :_ *@{0}*\n\t\t'.format(username)
    for state, dic in AGENT_STATS_DATA[username].items():
        if  not isinstance(dic, dict):
            if 'faction' in state:
                info += '_Faction :_ *{0}*\n\t\t'.format(AGENT_STATS_DATA[username]['faction'])
            continue

        info += '\n\t\t'
        for key, val in dic.items():
            if key in ['stats-img','saved']:
                if val:
                    info += '_{0} {1} :_ *{2}*\n\t\t'.format(state, key, 'Received Agent Stats' if 'stats-img' in key else 'Saved to Google Sheets')
                else:
                    info += '_{0} {1} :_ *{2}*\n\t\t'.format(state, key, 'No Agent Stats' if 'stats-img' in key else 'Not Saved')
            else:
                info += '_{0} {1} :_ *{2} {3}*\n\t\t'.format(state, key, locale.format('%d',val,grouping=True),
                    'Km' if 'trekker' in key else 'AP' if 'ap' in key else 'lvl')

    return info

@synchronized
def update_sheet(username,faction, state, data):
    fields = sheet_fields[faction]
    if not data['saved']:
        if 'start' is state:
            result = stat_sheet.get_values(SHEET_ID,fields['name'].format(21)+':'+fields['name'].format(70))
            row = 20 + len(result.get('values', '')) + 1
            values = [[
                username,
                AGENT_STATS_DATA[username]['start']['level'],
                AGENT_STATS_DATA[username]['start']['ap'],
                AGENT_STATS_DATA[username]['start']['trekker']
            ]]
            result = stat_sheet.update_values(SHEET_ID,fields['start'].format(row,row),'USER_ENTERED',values)
            response_text = "Successfully Saved {0} state...!!!".format(state) if result['updatedCells'] == len(values[0]) else "{0} state Saving was unsuccessful...!!!".format(state)
            AGENT_STATS_DATA[username]['start']['saved'] = row
        elif 'end' is state:
            values = [[
                AGENT_STATS_DATA[username]['end']['level'],
                AGENT_STATS_DATA[username]['end']['ap'],
                AGENT_STATS_DATA[username]['end']['trekker']
            ]]
            row = AGENT_STATS_DATA[username]['start']['saved']
            result = stat_sheet.update_values(SHEET_ID,fields['end'].format(row,row),'USER_ENTERED',values)
            response_text = "Successfully Saved {0} state...!!!".format(state) if result['updatedCells'] == len(values[0]) else "{0} state Saving was unsuccessful...!!!".format(state)
            AGENT_STATS_DATA[username]['end']['saved'] = row
        else:
            response_text = "Some Error Occurred...!!!  Contact *@NaNDuzIRa* for any queries:"
    else:
        response_text = "Seems like data is already saved for {0} Stats".format(state)

    return response_text

def save_stat(username):
    if 'faction' not in AGENT_STATS_DATA[username]:
        return "Your Faction alignment wasn't able to be recognized. Please try to set your Faction using:\n\t\t\t`/faction Resistance`\n\t\t\t`/faction Enlightened`"

    if not AGENT_STATS_DATA[username]['start']['saved']:
        if all(k in AGENT_STATS_DATA[username]['start'] for k in ('ap','level','trekker')):
            if not AGENT_STATS_DATA[username]['start']['stats-img']:
                return "A _Screenshot_ of your *Agent-Stats* from *Scanner [REDACTED]* App is needed by the Bot for verification purpose.\n\nPlease send the same using the *Share button* in Agent Tab of Scanner [REDACTED] App."
            response_text = update_sheet(username, AGENT_STATS_DATA[username]['faction'], 'start', AGENT_STATS_DATA[username]['start'])
        else:
            response_text = "Please provide all Start Stats(AP, LEVEL, TREKKER)"
    elif not AGENT_STATS_DATA[username]['end']['saved']:
        if datetime.now() <= EVENT_END_TIME:
            return "Event have not been ended yet....!!!\n\n*#IngressFS Stats Bot* will accept Ending Stats at {0}".format(LOCAL_END_TIME.strftime('%d %b, %Y %I:%M%p'))

        if all(k in AGENT_STATS_DATA[username]['end'] for k in ('ap','level','trekker')):
            if not AGENT_STATS_DATA[username]['end']['stats-img']:
                return "A _Screenshot_ of your *Agent-Stats* from *Scanner [REDACTED]* App is needed by the Bot for verification purpose.\n\nPlease send the same using the *Share button* in Agent Tab of Scanner [REDACTED] App."
            response_text = update_sheet(username, AGENT_STATS_DATA[username]['faction'], 'end', AGENT_STATS_DATA[username]['end'])
        else:
            response_text = "Please provide all End Stats(AP, LEVEL, TREKKER)"
    else:
        response_text = "Both Start & End Stats are saved. Good work Agent....!!!. Contact @NaNDuzIRa for any queries:"

    return response_text

def reset_stats(username):
    if not AGENT_STATS_DATA[username]['start']['saved']:
        AGENT_STATS_DATA[username]['start'].pop('level',None)
        AGENT_STATS_DATA[username]['start'].pop('ap',None)
        AGENT_STATS_DATA[username]['start'].pop('trekker',None)
        AGENT_STATS_DATA[username]['start']['stats-img'] = False
        response_text = "Your Starting Stats have been reset...!!!"
    elif not AGENT_STATS_DATA[username]['end']['saved']:
        AGENT_STATS_DATA[username]['end'].pop('level',None)
        AGENT_STATS_DATA[username]['end'].pop('ap',None)
        AGENT_STATS_DATA[username]['end'].pop('trekker',None)
        AGENT_STATS_DATA[username]['end']['stats-img'] = False
        response_text = "Your Ending Stats have been reset...!!!"
    else:
        response_text = "Both Start & End Stats are saved. Good work Agent....!!!. Contact @NaNDuzIRa for any queries:"

    return response_text

def get_file(username, photo=None, document=None):
    if photo:
        file_detail = max(photo, key=lambda x:x['file_size'])
        file_name = f"{BCKP_DIR}photo_{username}_{datetime.now().strftime('%Y_%m_%d-%H_%M_%S')}"
    elif document:
        file_detail = document
        file_name = f"{BCKP_DIR}file_{username}_{datetime.now().strftime('%Y_%m_%d-%H_%M_%S')}"

    msg_url = BOT_URL.format(AUTH_TOKEN, 'getFile')
    res = requests.get(msg_url, json=file_detail)
    json_data = json.loads(res.content)
    if json_data.get('ok', None) == True:
        file_name += f".{json_data['result']['file_path'].rsplit('.',1)[-1]}"
        file_url = BOT_FILE_URL.format(AUTH_TOKEN, json_data['result']['file_path'])
        res = requests.get(file_url, allow_redirects=True)
        open(file_name, 'wb').write(res.content)

        if photo:
            response_text = "Bot currently is not able to recognize Compressed Images properly.\nPlease send the same has a file without any sort of Compression...!!!"
        elif document:
            response_text = "Received Agent-Stats Image Successfully. Make sure you enter the stats manually for cross-checking & save it."
            if not AGENT_STATS_DATA[username]['start']['stats-img']:
                AGENT_STATS_DATA[username]['start']['stats-img'] = True
            elif not AGENT_STATS_DATA[username]['end']['stats-img']:
                if datetime.now() <= EVENT_END_TIME:
                    return "Event have not been ended yet....!!!\n\n*#IngressFS Stats Bot* will accept Ending Stats at {0}".format(LOCAL_END_TIME.strftime('%d %b, %Y %I:%M%p'))
                AGENT_STATS_DATA[username]['end']['stats-img'] = True
            else:
                response_text = "Agent-Stats is set for Start & End already."

    else:
        response_text = "Error fetching File Details from Server....!!!"

    return response_text



def process_text(username, text):
    if text.startswith('/start'):
        response_text = "*Welcome Agent @{0},*\n\n#IngressFS Stats Bot will help you guide through your registration process for *{1}*. Now has a first step, Set your Faction using:\n\t\t\t`/faction Resistance`\n\t\t\t`/faction Enlightened`".format(username, EVENT_TITLE)
    elif text.startswith('/faction'):
        response_text = set_faction(username, text.lower())
    elif text.startswith('/level'):
        response_text = set_stat(username, 'level', text.lower())
    elif text.startswith('/ap'):
        response_text = set_stat(username, 'ap', text.lower())
    elif text.startswith('/trekker'):
        response_text = set_stat(username, 'trekker', text.lower())
    elif text.startswith('/info'):
        response_text = get_info(username)
    elif text.startswith('/save'):
        response_text = save_stat(username)
    elif text.startswith('/reset'):
        response_text = reset_stats(username)
    elif text.startswith('/results'):
        response_text = f"Visit the [#IngressFS Bengaluru, Scoring Spreadsheet - 4th May 2019]({SHEET_URL}) to view your Results"
    elif text.startswith('/help'):
        response_text = "Contact @NaNDuzIRa for more help"
    else:
        response_text = "*#IngressFS Stats Bot* ain't currently supporting natural language communication with a Human Being...!!!"

    return response_text

def process_message(message):
    data = {
        'chat_id': message['chat']['id'],
        'parse_mode': 'Markdown'
    }
    if 'username' in message['chat']:
        if message['chat']['username'] not in AGENT_STATS_DATA:
            AGENT_STATS_DATA[message['chat']['username']] = {
                'chat-id': data['chat_id'],
                'start': {
                    'stats-img': False,
                    'saved': False
                },
                'end': {
                    'stats-img': False,
                    'saved': False
                }
            }

        if datetime.now() >= EVENT_START_TIME:
            if 'text' in message:
                data['text'] = process_text(message['chat']['username'], message['text'])
            elif 'photo' in message:
                data['text'] = get_file(message['chat']['username'], photo=message['photo'])
            elif 'document' in message:
                data['text'] = get_file(message['chat']['username'], document=message['document'])
            else:
                data['text'] = "Unrecognized Content....!!!. Please follow the basic steps suggested by the Bot.\n\nFor more info try out the /help command"
        else:
            data['text'] = "Event have not been started yet....!!!\n\n*#IngressFS Stats Bot* will be accepting Stats at {0}".format(LOCAL_START_TIME.strftime('%d %b, %Y %I:%M%p'))
    else:
        data['text'] = "Please set your Username in Telegram Settings has Agent Name to continue...!!!"
    # print('AGENT STATS :{}'.format(json.dumps(AGENT_STATS_DATA,separators="':",indent="\t")))
    # print("DATA :{}".format(json.dumps(data,separators="':",indent="\t")))
    r = requests.post(get_url(BOT_URL, "sendMessage"), data=data)

@app.route('/IngressFS_Stats_bOt', methods=['POST'])
def post_handler():
    if request.method == "POST":
        update = request.get_json()
        # print("UPDATE :{}".format(json.dumps(update,separators="':",indent="\t")))

        if isinstance(update, dict) and 'message' in update:
            process_message(update['message'])
        else:
            return "WRONG PLACE...!!! Move out of here."
        return "ok!", 200

@app.route('/', methods=['POST','GET'])
def get_lost():
    return "GET LOST"

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000)
