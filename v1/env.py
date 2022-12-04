"""환경 변수 설정 및 정의"""
import os

from dotenv import load_dotenv

load_dotenv(verbose=True)

BOT_TOKEN = os.getenv('BOT_TOKEN')
DB_URL = os.getenv('DB_URL')
DB_PORT = os.getenv('DB_PORT')
DB_ID = os.getenv('DB_ID')
DB_PW = os.getenv('DB_PW')
DB_DB = os.getenv('DB_DB')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
KAS_KEY = os.getenv('KAS_KEY')
SOLDIER_PRICE = int(os.getenv('SOLDIER_PRICE'))
EQUIPMENT_PRICE = int(os.getenv('EQUIPMENT_PRICE'))
DAILY_PLAYABLE_COUNT = int(os.getenv('DAILY_PLAYABLE_COUNT'))
