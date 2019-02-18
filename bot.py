import requests
from bottle import (
    run, post, response, request as bottle_request
)

BOT_URL = 'https://api.telegram.org/bot{0}/'
AUTH_TOKEN = ''

def get_chat_id(data):
    """ Method to extract chat id from Telegram request. """

    chat_id = data['message']['chat']['id']

    return chat_id

def get_message(data):
    """ Method to extract message id from Telegram request. """

    message_text = data['message']['text']

    return message_text

def send_message(prepared_data):
    """ Method to send the Prepared Data(JSON which includes 'chat_id' and 'text') to the Bot. """

    message_url = BOT_URL.format(AUTH_TOKEN) + 'sendMessage'
    requests.post(message_url, json=prepared_data)

def change_text_message(text):
    """ Method to extract message id from Telegram request. """

    return text[::-1]

def prepare_data_for_answer(data):
    """ Method to Alter the data and process the Reply Message. """

    answer = change_text_message(get_message(data))
    
    json_data = {
        'chat_id': get_chat_id(data),
        'text': answer,
    }
    
    return json_data

@post('/')
def main():
    """ Method to serve Webhook requests from Telegram. """

    data = bottle_request.json
    print(data)
    answer_data = prepare_data_for_answer(data)
    send_message(answer_data)
    
    return response

if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True)