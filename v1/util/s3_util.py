import json
from typing import Optional

import boto3
import requests

from env import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


def get_soldier_nft(token_id: int):
    url = f"https://metaversewar-nft.s3.ap-northeast-2.amazonaws.com/Soldier_metadata/{str(token_id)}.json"
    timeout = 5
    res = requests.get(url, timeout=timeout).json()
    token_id = int(res["name"].split('#')[1])
    res["information"]["token_id"] = token_id
    return res["information"]


def get_armor_nft(token_id: int):
    url = f"https://metaversewar-nft.s3.ap-northeast-2.amazonaws.com/EP1_Armors/metadata/{str(token_id)}.json"
    timeout = 5
    res = requests.get(url, timeout=timeout).json()
    return res["information"]


def get_weapon_nft(token_id: int):
    url = f"https://metaversewar-nft.s3.ap-northeast-2.amazonaws.com/EP1_Weapons/metadata/{str(token_id)}.json"
    timeout = 5
    res = requests.get(url, timeout=timeout).json()
    return res["information"]


def change_soldier_equipment(token_id: int, part_type: str, part_id: Optional[str]):
    url = f"https://metaversewar-nft.s3.ap-northeast-2.amazonaws.com/Soldier_metadata/{str(token_id)}.json"
    timeout = 5
    res = requests.get(url, timeout=timeout).json()
    s3 = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    res['information']['equipments'][part_type] = part_id
    s3object = s3.Object('metaversewar-nft', f'Soldier_metadata/{token_id}.json')
    s3object.put(
        Body=(bytes(json.dumps(res).encode('UTF-8')))
    )
    return res


# print(change_soldier_equipment(897, "arm", "3"))
print(get_weapon_nft(1))
