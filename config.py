from datetime import datetime

class DevConfig():
    """Development configuration"""
    DEBUG = True
    TESTING = True

class TestConfig():
    """Testing configuration"""
    DEBUG = True
    TESTING = True

class ProductionConfig():
    """Production configuration"""
    DEBUG = False
    TESTING = False

class BotInfo():
    """ Secure Information on Bot """
    BOT_URL = 'https://api.telegram.org/bot{0}/{1}'
    BOT_FILE_URL = 'https://api.telegram.org/file/bot{0}/{1}'
    AUTH_TOKEN = ''
    BCKP_DIR = 'Assets/'

    EVENT_START_TIME = datetime.strptime('2019/03/30 23:00:00', '%Y/%m/%d %H:%M:%S')
    EVENT_END_TIME = datetime.strptime('2019/03/30 22:30:00', '%Y/%m/%d %H:%M:%S')
    EVENT_TITLE = "#IngressFS BLR, India April 2019"

    SHEET_CREDS = 'credentials.json'
    SHEET_ID = ''