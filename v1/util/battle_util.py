import random
import time

from fastapi_sqlalchemy import db
from sqlalchemy import func

from models.soldier import SoldierModel
from models.user import UserModel
from util.soldier_util import get_soldier_info


def match_making(chat_id: str, db_user: UserModel):
    with db():
        get_match_list = db.session.query(UserModel).filter(
            (UserModel.chat_id != chat_id) & (UserModel.main_soldier.is_not(None)) & (
                    func.abs(UserModel.pvp_rating - db_user.pvp_rating) <= 200)).order_by(
            func.abs(UserModel.pvp_rating - db_user.pvp_rating)).limit(50).all()
    if get_match_list:
        db_opponent = random.choice(get_match_list)

        user_nft_info = get_soldier_info(db_user.main_soldier)
        opponent_nft_info = get_soldier_info(db_opponent.main_soldier)
        return {'user': user_nft_info, 'opponent': opponent_nft_info, "user_info": db_user,
                "opponent_info": db_opponent, 'rs': True}
    return {'rs': False}


def battle(my_soldier: SoldierModel, enemy_soldier: SoldierModel):
    winner = None
    # 선공 정하기
    if my_soldier.stat_def + my_soldier.stat_atk <= enemy_soldier.stat_def + \
            enemy_soldier.stat_atk:
        attack_turn = 'user'
        init_attack = 'user'
    else:
        attack_turn = 'opponent'
        init_attack = 'opponent'

    # 병과별 상성 세팅
    synergy = SynergyData(my_soldier.class_,
                          enemy_soldier.class_).class_interaction()
    log = "전투를 시작합니다.\n"

    # 스텟 세팅
    user_hp = my_soldier.stat_def
    opponent_hp = enemy_soldier.stat_def
    user_damage = my_soldier.stat_atk
    opponent_damage = enemy_soldier.stat_atk
    if synergy['res']:
        penalty = '유저' if synergy['penalty'] == 'user' else '상대편'
        merit = '유저' if synergy['penalty'] == 'enemy' else '상대편'
        log += f"병과 상성으로 {penalty} 약화! {merit} 강화!"
        if penalty == '유저':
            user_hp = round(user_hp * 0.85, 2)
            user_damage = round(user_damage * 0.85, 2)
            opponent_hp = round(opponent_hp * 1.15, 2)
            opponent_damage = round(opponent_damage * 1.15, 2)
        else:
            opponent_hp = round(opponent_hp * 0.85, 2)
            opponent_damage = round(opponent_damage * 0.85, 2)
            user_hp = round(user_hp * 1.15, 2)
            user_damage = round(user_damage * 1.15, 2)
    battle_log = [{
        "log": log,
        "user_hp": user_hp,
        "opponent_hp": opponent_hp,
        "turn": attack_turn,
        "crit": False
    }]

    while (float(user_hp) > 0) and (float(opponent_hp) > 0):
        if attack_turn == 'user':
            # 데미지 계산
            damage = user_damage
            # 크리티컬 계산
            crit_flag = False
            crit = random.randint(1, 100)
            if crit >= 95:
                damage *= 2
                crit_flag = True

            opponent_hp = round(opponent_hp - damage, 1)
            if opponent_hp <= 0:
                opponent_hp = 0
                winner = 'user'
            battle_log.append({
                "log": f"{my_soldier.name}이(가) {enemy_soldier.name}에게 {damage} 의 피해를 입혔습니다",
                "user_hp": user_hp,
                "opponent_hp": opponent_hp,
                "turn": attack_turn,
                "crit": crit_flag
            })
            attack_turn = 'opponent'

        elif attack_turn == 'opponent':
            damage = opponent_damage
            # 크리티컬 계산
            crit_flag = False
            crit = random.randint(1, 100)
            if crit >= 95:
                damage *= 2
                crit_flag = True

            user_hp = round(user_hp - damage, 1)
            if user_hp <= 0:
                user_hp = 0
                winner = 'opponent'
            battle_log.append({
                "log": f"{enemy_soldier.name}이(가) {my_soldier.name}에게 {damage} 의 피해를 입혔습니다",
                "user_hp": user_hp,
                "opponent_hp": opponent_hp,
                "turn": attack_turn,
                "crit": crit_flag})
            attack_turn = 'user'
    return {'battle_log': battle_log, 'winner': winner, 'init_attack': init_attack,
            'my_soldier': my_soldier, 'enemy_soldier': enemy_soldier}


def battle_msg(update, context, battle_, mode: str, user_info: UserModel, opponent_info: UserModel):
    battle_log = battle_['battle_log']
    init_attack = user_info.get_fullname() if battle_[
                                                  'init_attack'] == 'user' else opponent_info.get_fullname()
    win_flag = True if battle_['winner'] == 'user' else False
    my_soldier = battle_['my_soldier']
    enemy_soldier = battle_['enemy_soldier']
    # 선공 통보
    # text = f'능력치를 감안하여 {init_attack} 부터 공격을 시작합니다.'
    # init_message = context.bot.send_message(text=text,
    #                                         chat_id=update.message.chat_id)
    # time.sleep(3)

    # 전투 개시
    # for log in battle_log:
    #     turn = f"<strong>{user_info.get_fullname()}</strong> \t {opponent_info.get_fullname()}" \
    #         if log[
    #                'turn'] == 'user' else f"{user_info.get_fullname()} \t<strong>{opponent_info.get_fullname()}</strong>"
    #     text = f"{turn}\n" \
    #            f"<b>{log['user_hp']}</b> \t\t\t\t\t <b>{log['opponent_hp']}</b> \n" \
    #            f"{'크리티컬!' if log['crit'] else ''}\n" \
    #            f"{log['log']}"
    #     context.bot.edit_message_text(text=text, parse_mode='HTML',
    #                                   chat_id=init_message.chat.id,
    #                                   message_id=init_message.message_id)
    #     time.sleep(3)
    # 전투 끝
    if mode == 'pvp':
        callback_data = 'pvp_main'
        with db():
            db_user = db.session.query(UserModel).filter(
                UserModel.chat_id == update.message.from_user.id).one_or_none()
            rating_before = db_user.pvp_rating
            tier_before = db_user.get_pvp_tier()
            if win_flag:
                rating_amount = elo_calculate(user_info, opponent_info)
                db_user.pvp_win_count += 1
                db_user.pvp_rating += rating_amount
                db_user.win_straight += 1
                db_user.cash_point += 100
            else:
                rating_amount = elo_calculate(opponent_info, user_info)
                db_user.pvp_lose_count += 1
                db_user.pvp_rating -= rating_amount
                db_user.win_straight = 0
                db_user.cash_point += 30
            db_user.pvp_win_rate = round(
                ((db_user.pvp_win_count / (db_user.pvp_win_count + db_user.pvp_lose_count)) * 100),
                2)
            tier_after = db_user.get_pvp_tier()
            text = f"✌<b>승리 하셨습니다!\n</b>포인트 + 100, 레이팅 +{rating_amount}\n나의 레이팅 : {rating_before} -> {db_user.pvp_rating}" \
                if win_flag else f"😢<b>패배 하였습니다!\n</b>포인트 +30 레이팅 -{rating_amount}\n나의 레이팅 : {rating_before} -> {db_user.pvp_rating}"
            text += f"\n상대 레이팅 : {opponent_info.pvp_rating}"
            if tier_before != tier_after:
                text += f"\n\n<strong>PVP 티어가 변경되었습니다. \n {tier_before} -> {tier_after}</strong>"
            if db_user.win_straight >= 2:
                text += f'\n 🔥 {db_user.win_straight} 연승 중🔥 '
            db.session.commit()
            db.session.refresh(db_user)

    elif mode == 'practice':
        text = '✌<b>승리 하셨습니다!</b>' if win_flag else '😢<b>패배 하였습니다!</b>'
        callback_data = 'pvp_practice_main'

    if init_attack == user_info.get_fullname():
        text += f"\n\n <b>PVP 결과 </b>\n" \
                f"(선공)<strong>{user_info.get_fullname()}</strong>: \n1. 병사 : ATK : {my_soldier.stat_atk} / DEF : {my_soldier.stat_def} / {my_soldier.class_to_kr()}\n" \
                f"(후공){opponent_info.get_fullname()}: \n1. 병사 : ATK : {enemy_soldier.stat_atk} / DEF : {enemy_soldier.stat_def} / {enemy_soldier.class_to_kr()}\n" \
                f"✴ 일기토 : {len(battle_log) - 1} 합"
    else:
        text += f"\n\n <b>PVP 결과 </b>\n" \
                f"(후공)<strong>{user_info.get_fullname()}</strong>: \n1. 병사 : ATK : {my_soldier.stat_atk} / DEF : {my_soldier.stat_def} / {my_soldier.class_to_kr()}\n" \
                f"(선공){opponent_info.get_fullname()}:  \n1. 병사 : ATK : {enemy_soldier.stat_atk} / DEF : {enemy_soldier.stat_def} / {enemy_soldier.class_to_kr()}\n" \
                f"✴ 일기토 : {len(battle_log) - 1} 합"
    text +=  f"\n 남은 pvp 횟수 : {20 - db_user.rank_battle_count}"
    context.bot.send_message(text=text, parse_mode='HTML',
                             chat_id=update.message.chat.id)
    return


class SynergyData:
    def __init__(self, user_class: str, enemy_class: str):
        self.class_data = {'user': user_class, 'enemy': enemy_class}

    def class_interaction(self):
        return_dict = {'res': False, 'penalty': None}
        data = list(set(self.class_data.values()))
        if len(data) > 1:
            return_dict['res'] = True
            reverse_data = {v: k for k, v in self.class_data.items()}
            if 'infantry' in data and 'cavalry' in data:
                return_dict['penalty'] = reverse_data.get('cavalry')
            elif 'cavalry' in data and 'archer' in data:
                return_dict['penalty'] = reverse_data.get('archer')
            elif 'infantry' in data and 'archer' in data:
                return_dict['penalty'] = reverse_data.get('infantry')
        return return_dict


def elo_calculate(winner_info: UserModel, loser_info: UserModel):
    elo_constant = 30
    if 30 < winner_info.get_game_count() <= 50:
        elo_constant = 40
    elif winner_info.get_game_count() <= 30:
        elo_constant = 60
    elo_result = int(
        elo_constant * (1 / pow(10, (winner_info.pvp_rating - loser_info.pvp_rating) / 400)))
    return elo_result if elo_result > 0 else 1
