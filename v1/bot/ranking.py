from fastapi_sqlalchemy import db

from bot.markup_list import ranking_markup
from models.user import UserModel


def bot_ranking(update, context):
    callback_info = str(update.callback_query.data).split('_')
    page = int(callback_info[1])
    limit = 3
    with db():
        ranking = db.session.query(UserModel).order_by(UserModel.pvp_rating.desc()).offset(
            limit * (page - 1)).limit(limit).all()
        user_count = db.session.query(UserModel).count()
        max_page = (user_count // limit) + 1

        context.bot.edit_message_text(text=f'랭킹 , 페이지:{page}',
                                      chat_id=update.callback_query.message.chat_id,
                                      message_id=update.callback_query.message.message_id,
                                      reply_markup=ranking_markup(page, limit, max_page, ranking,
                                                                  str(update.callback_query.message.chat_id)))
    return
