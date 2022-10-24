# cmd_handler_bot.py
import datetime
import threading

import telegram
from fastapi_sqlalchemy import db
from sqlalchemy.exc import IntegrityError
from telegram.ext import CommandHandler
from telegram.ext import Updater, CallbackQueryHandler

# from bot.game_pvp import bot_pvp
# from bot.game_scenario import bot_scenario
from bot.markup_list import init_markup, register_markup
# from bot.ranking import bot_ranking
from bot.shop import bot_shop
from bot.status import bot_status
from env import BOT_TOKEN
from models.user import UserModel
from util.battle_util import match_making, battle, battle_msg

updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher
BOT = telegram.Bot(BOT_TOKEN)


# start 를 눌렀을때 화면 init 과 동일시 해야함
def init_state(update, context):
    text = """
    <b>&lt;최초 &gt;</b> 텔레그램 봇 기반의 NFT 게임 메타버스워!

공지방 : https://t.me/Metaversewarofficial

소통방 : https://t.me/metaverse_warGroupchat

Contact : @gryptogolo

(c) 2022. DalgonaDAO | Thetealabs Ltd. All rights reserved
    """
    context.bot.send_message(chat_id=update.message.chat_id, parse_mode='HTML'
                             , text=text)
    # context.bot.send_photo(chat_id=update.message.chat_id,
    #                        photo='https://metaversewar-data.s3.ap-northeast-2.amazonaws.com/logo/logo.png')
    if update.message.chat.type == "private":
        # 계정 확인
        with db():
            db_user = db.session.query(UserModel).filter(
                UserModel.chat_id == update.message.chat.id).one_or_none()
            if not db_user:
                context.bot.send_message(
                    chat_id=update.message.chat_id, parse_mode='HTML'
                    , text='Welcome to MetaverseWar'
                    , reply_markup=register_markup
                )
            else:
                # 최근 접속 시간 갱신
                db_user.joined_at = datetime.datetime.now()
                db.session.commit()
                db.session.refresh(db_user)
                text = 'Welcome to MetaverseWar'
                if not db_user.main_soldier:
                    text += '\n\n<b>메인 전투 병사를 지정 하셔야 합니다.</b>'

                context.bot.send_message(
                    chat_id=update.message.chat_id, parse_mode='HTML'
                    , text=text
                    , reply_markup=init_markup(db_user)
                )


def battle_state(update, context):
    with db():
        db_user = db.session.query(UserModel).filter(UserModel.chat_id == update.message.from_user.id).one_or_none()
    if not db_user.main_soldier:
        context.bot.send_message(text=f"{db_user.first_name} {db_user.last_name} should set main soldier first",
                                 chat_id=update.message.chat_id)
        return
    match = match_making(update.message.from_user.id, db_user)
    battle_ = battle(match['user'], match['opponent'])
    battle_msg(update, context, battle_, 'pvp', match['user_info'], match['opponent_info'])
    return


start_handler = CommandHandler('start', init_state)
battle_handler = CommandHandler('battle', battle_state)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(battle_handler)


def callback_get(update, context):
    print(update.callback_query.data)
    # 초기 화면
    if update.callback_query.data == "init":
        with db():
            db_user = db.session.query(UserModel).filter(
                UserModel.chat_id == update.callback_query.message.chat_id).one_or_none()
            text = "Welcome to MetaverseWar"
            if not db_user.main_soldier:
                text += '\n\n<b>메인 전투 병사를 지정 하셔야 합니다.</b>'
            context.bot.edit_message_text(text=text, parse_mode='HTML',
                                          chat_id=update.callback_query.message.chat_id,
                                          message_id=update.callback_query.message.message_id,
                                          reply_markup=init_markup(db_user))
    elif update.callback_query.data == "init_register":
        with db():
            user = UserModel(chat_id=update.callback_query.message.chat_id,
                             first_name=update.callback_query.message.chat.first_name,
                             last_name=update.callback_query.message.chat.last_name)
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError as error:
                raise error
            db.session.refresh(user)
            BOT.sendMessage(chat_id=update.callback_query.message.chat_id,
                            text="계정이 생성되었습니다. /start 로 게임을 시작해주세요!")

    elif str(update.callback_query.data).startswith("status"):
        bot_status(update, context)
    elif str(update.callback_query.data).startswith("shop"):
        bot_shop(update, context)
    # elif str(update.callback_query.data).startswith("scenario"):
    #     bot_scenario(update, context)
    # elif str(update.callback_query.data).startswith("ranking"):
    #     bot_ranking(update, context)


dispatcher.add_handler(CallbackQueryHandler(callback_get))

t = threading.Thread(target=updater.start_polling)
t.start()
