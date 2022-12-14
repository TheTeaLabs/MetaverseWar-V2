# cmd_handler_bot.py
import datetime
import threading
from typing import List

import telegram
from fastapi_sqlalchemy import db
from sqlalchemy.exc import IntegrityError
from telegram.ext import CommandHandler
from telegram.ext import Updater, CallbackQueryHandler

# from bot.game_pvp import bot_pvp
# from bot.game_scenario import bot_scenario
from bot.markup_list import init_markup, register_markup
# from bot.ranking import bot_ranking
from bot.ranking import bot_ranking
from bot.shop import bot_shop
from bot.status import bot_status, soldier_status_text
from env import BOT_TOKEN, DAILY_PLAYABLE_COUNT
from models.user import UserModel, DailyCheckModel
from util.battle_util import match_making, battle, battle_msg
from util.soldier_util import init_create_soldier, init_equipment, get_soldier_info

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
        db_user = db.session.query(UserModel).filter(
            UserModel.chat_id == update.message.from_user.id).one_or_none()

        if not db_user:
            context.bot.send_message(
                text=f"회원 가입을 먼저 진행해주세요. \n@NFT_gamebot",
                chat_id=update.message.chat_id)
            return

        if not db_user.main_soldier:
            context.bot.send_message(
                text=f"{db_user.first_name} {db_user.last_name} , 전투 병사를 지정해야 합니다.",
                chat_id=update.message.chat_id)
            return
        if db_user.last_rank_battle:
            if db_user.last_rank_battle.date() < datetime.date.today():
                db_user.last_rank_battle = datetime.datetime.now()
                db_user.rank_battle_count = 1
            elif db_user.last_rank_battle.date() >= datetime.date.today():
                if db_user.rank_battle_count >= DAILY_PLAYABLE_COUNT:
                    context.bot.send_message(
                        text=f"{db_user.first_name} {db_user.last_name} , 하루 게임 횟수 초과 하였습니다.",
                        chat_id=update.message.chat_id)
                    return
                else:
                    db_user.last_rank_battle = datetime.datetime.now()
                    db_user.rank_battle_count += 1
        else:
            db_user.last_rank_battle = datetime.datetime.now()
            db_user.rank_battle_count += 1
        match = match_making(update.message.from_user.id, db_user)
        if not match['rs']:
            db.session.rollback()
            context.bot.send_message(
                text=f"{db_user.first_name} {db_user.last_name} , 레이팅 차이로 매칭에 실패 하였습니다.",
                chat_id=update.message.chat_id)
            return
        db.session.commit()
        db.session.refresh(db_user)
        battle_ = battle(match['user'], match['opponent'])
        battle_msg(update, context, battle_, 'pvp', match['user_info'], match['opponent_info'])
        return


def my_info_state(update, context):
    with db():
        db_user = db.session.query(UserModel).filter(
            UserModel.chat_id == update.message.from_user.id).one_or_none()
        if not db_user:
            context.bot.send_message(
                text=f"회원 가입을 먼저 진행해주세요. \n@NFT_gamebot",
                chat_id=update.message.chat_id)
            return

        context.bot.send_message(
            chat_id=update.message.chat_id, parse_mode='HTML'
            , text=soldier_status_text(db_user))
    return


def show_ranking_state(update, context):
    with db():
        ranking_list: List[UserModel] = db.session.query(UserModel).order_by(
            UserModel.pvp_rating.desc()).limit(
            10).all()
        text = "<strong>랭킹</strong>\n"
        rank = 1
        for user in ranking_list:
            if rank <= 3:
                if rank == 1:
                    text += '🥇'
                elif rank == 2:
                    text += '🥈'
                else:
                    text += '🥉'
                text += f"<strong>{str(rank)} 위 : {user.get_fullname()} 레이팅: {user.pvp_rating}</strong>\n"
            else:
                text += '🏅'
                text += f"{str(rank)} 위 : {user.get_fullname()} 레이팅: {user.pvp_rating}\n"
            rank += 1
        context.bot.send_message(
            chat_id=update.message.chat_id, parse_mode='HTML'
            , text=text)
    return


def daily_check_state(update, context):
    with db():
        db_user = db.session.query(UserModel).filter(
            UserModel.chat_id == update.message.from_user.id).one_or_none()
        text = f"<strong>{db_user.get_fullname()} 님,\n{datetime.date.today()} 출석을 환영합니다!</strong> " \
               f"\n출석 보상 : 300 포인트"
        if db_user:
            if db_user.joined_at:
                if db_user.joined_at.date() >= datetime.date.today():
                    text = f"<strong>{db_user.get_fullname()} 님, 내일 다시 오세요!</strong> "
                    context.bot.send_message(
                        chat_id=update.message.chat_id, parse_mode='HTML'
                        , text=text)

                    return
            db_user.joined_at = datetime.datetime.now()
            db_user.cash_point += 300
            db.session.add(
                    DailyCheckModel(chat_id=db_user.chat_id, checked_at=datetime.date.today()))
            db.session.commit()
            context.bot.send_message(
                    chat_id=update.message.chat_id, parse_mode='HTML'
                    , text=text)


# def test_state(update, context):
#     with db():
#         db_user = db.session.query(UserModel).filter(
#             UserModel.chat_id == update.message.from_user.id).one_or_none()
#         init_equipment(update, get_soldier_info(db_user.main_soldier))
#     return


start_handler = CommandHandler('start', init_state)
battle_handler = CommandHandler(['battle', 'pvp'], battle_state)
info_handler = CommandHandler(['info'], my_info_state)
ranking_handler = CommandHandler(['ranking', 'rank'], show_ranking_state)
check_handler = CommandHandler('check', daily_check_state)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(battle_handler)
dispatcher.add_handler(info_handler)
dispatcher.add_handler(ranking_handler)
dispatcher.add_handler(check_handler)


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
                             last_name=update.callback_query.message.chat.last_name,
                             cash_point=5000)
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError as error:
                raise error
            db.session.refresh(user)
            init_solder = init_create_soldier(update)
            init_equipment(update, init_solder)

            BOT.sendMessage(chat_id=update.callback_query.message.chat_id,
                            text="계정이 생성되었습니다. /start 로 게임을 시작해주세요!")

    elif str(update.callback_query.data).startswith("status"):
        bot_status(update, context)
    elif str(update.callback_query.data).startswith("shop"):
        bot_shop(update, context)
    # elif str(update.callback_query.data).startswith("scenario"):
    #     bot_scenario(update, context)
    elif str(update.callback_query.data).startswith("ranking"):
        bot_ranking(update, context)


dispatcher.add_handler(CallbackQueryHandler(callback_get))

t = threading.Thread(target=updater.start_polling)
t.start()
