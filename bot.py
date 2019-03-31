import requests
from bottle import (
    Bottle, response, request as bottle_request
)
from PIL import Image
from io import BytesIO
import cv2
import os
import json
import time
import config
import numpy as np

class BotHandlerMixin:
    BOT_URL = config.BotInfo.BOT_URL
    BOT_FILE_URL = config.BotInfo.BOT_FILE_URL
    AUTH_TOKEN = config.BotInfo.AUTH_TOKEN
    BCKP_DIR = config.BotInfo.BCKP_DIR

    def get_chat_id(self, data):
        """ Method to extract chat id from Telegram request. """

        chat_id = data['message']['chat']['id']

        return chat_id

    def get_text(self, text):
        """ Method to extract message from Telegram request. """

        message_text = data['message'].get('text', None)

        return message_text

    def get_file(self, file):
        """ Method to extract File details from TG request """
        photo_details = file['document']
        # file_details = max(photo_details, key=lambda x:x['file_size'])
        # print(file_details)
        
        message_url = self.BOT_URL.format(self.AUTH_TOKEN, 'getFile')
        res = requests.get(message_url, json=photo_details)
        json_data = json.loads(res.content)
        if json_data.get('ok', None) == True:
            file_path = json_data['result']['file_path']
            file_url = self.BOT_FILE_URL.format(self.AUTH_TOKEN,file_path)
            res = requests.get(file_url)
            img = Image.open(BytesIO(res.content))
            save_path = os.path.join(self.BCKP_DIR,file['chat'].get('username', 'unknown'),str(time.time())+'.'+file_path.split('.')[-1])
            print("SAVE PATH:",save_path)
            opencv_image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            cv2.imwrite(save_path, opencv_image)

        return
        

    def send_message(self, prepared_data):
        """ Method to send the Prepared Data(JSON which includes 'chat_id' and 'text') to the Bot. """

        message_url = self.BOT_URL.format(self.AUTH_TOKEN, 'sendMessage')
        requests.post(message_url, json=prepared_data)

class TelegramBot(BotHandlerMixin, Bottle):

    def __init__(self, *args, **kwargs):
        super(TelegramBot, self).__init__()
        self.route('/', callback=self.post_handler, method='POST')

    def change_text_message(self, text):
        """ Method to extract message id from Telegram request. """

        return text[::-1]

    def process_image(self, photo):
        """ Method to retrieve Image from TG Servers """
        
        return

    def prepare_data_for_answer(self, data):
        """ Method to Alter the data and process the Reply Message. """

        message = data['message']

        if 'document' in message:
            image = self.process_image(self.get_file(message))
        elif 'text' in message:
            answer = self.change_text_message(self.get_text(message))
        
        json_data = {
            'chat_id': self.get_chat_id(data),
            'text': 'answer',
        }
        
        return json_data

    def post_handler(self):
        """ Method to serve Webhook requests from Telegram. """

        data = bottle_request.json
        print(data)
        answer_data = self.prepare_data_for_answer(data)
        # self.send_message(answer_data)
        
        return response

if __name__ == '__main__':
    app = TelegramBot()
    app.run(host='localhost', port=8080, debug=True)