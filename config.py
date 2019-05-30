from datetime import datetime, timedelta

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

    EVENT_START_TIME = datetime.strptime('2019/06/01 15:50:00', '%Y/%m/%d %H:%M:%S') - timedelta(hours=5, minutes=30)
    EVENT_END_TIME = datetime.strptime('2019/06/01 18:00:00', '%Y/%m/%d %H:%M:%S') - timedelta(hours=5, minutes=30)
    EVENT_TITLE = "#IngressFS BLR, India June 2019"

    SHEET_CREDS = 'credentials.json'
    SHEET_ID = '1Uqubcmdzq9mK7y4D0lj9N7diWSXd4FTxY0D61V89YN4'
    SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/'
