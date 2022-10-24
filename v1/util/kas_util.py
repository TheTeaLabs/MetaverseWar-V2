import requests

from env import KAS_KEY

x_chain_id = '8217'
Authorization = KAS_KEY
soldier_nft_address = "0x01e4495739485afa86dff3d1003de7afc424264d"
armor_nft_address = "0x7b40f786b354f18be0de14d60723745068ac9dc7"
weapon_nft_address = "0x3a0724cd8ae373ca5c389e5189dad2fa0cb90f06"


def get_user_soldier_nft(owner_address: str):
    url = f"https://th-api.klaytnapi.com/v2/contract/nft/{soldier_nft_address}/owner/{owner_address}?size=1000&cursor="
    headers = {"x-chain-id": x_chain_id,
               "Authorization": Authorization}
    timeout = 5
    response = requests.get(url, headers=headers, timeout=timeout).json()
    nft_list = []
    for item in response["items"]:
        res = requests.get(item["tokenUri"], timeout=timeout).json()
        token_id = int(item['tokenId'], 16)
        res["information"]["token_id"] = token_id
        nft_list.append(res["information"])
    return nft_list


def check_user_own_soldier_nft(owner_address: str, token_id: int):
    url = f"https://th-api.klaytnapi.com/v2/contract/nft/{soldier_nft_address}/token/{str(hex(token_id))}"
    headers = {"x-chain-id": x_chain_id,
               "Authorization": Authorization}
    timeout = 5
    response = requests.get(url, headers=headers, timeout=timeout).json()
    if response['owner'] != owner_address.lower():
        return False
    return True


def get_armor_nft(owner_address: str):
    url = f"https://th-api.klaytnapi.com/v2/contract/nft/{armor_nft_address}/owner/{owner_address}?size=1000&cursor="
    headers = {"x-chain-id": x_chain_id,
               "Authorization": Authorization}
    timeout = 5
    response = requests.get(url, headers=headers, timeout=timeout).json()
    nft_list = []
    for item in response["items"]:
        res = requests.get(item["tokenUri"], timeout=timeout).json()
        token_id = int(item['tokenId'], 16)
        res["information"]["token_id"] = token_id
        nft_list.append(res["information"])
    return nft_list


def check_user_own_nft_armor(owner_address: str, token_id: int):
    url = f"https://th-api.klaytnapi.com/v2/contract/nft/{armor_nft_address}/token/{str(hex(token_id))}"
    headers = {"x-chain-id": x_chain_id,
               "Authorization": Authorization}
    timeout = 5
    response = requests.get(url, headers=headers, timeout=timeout).json()
    if response['owner'] != owner_address.lower():
        return False
    return True


def get_weapon_nft(owner_address: str):
    url = f"https://th-api.klaytnapi.com/v2/contract/nft/{weapon_nft_address}/owner/{owner_address}?size=1000&cursor="
    headers = {"x-chain-id": x_chain_id,
               "Authorization": Authorization}
    timeout = 5
    response = requests.get(url, headers=headers, timeout=timeout).json()
    nft_list = []
    for item in response["items"]:
        res = requests.get(item["tokenUri"], timeout=timeout).json()
        token_id = int(item['tokenId'], 16)
        res["information"]["token_id"] = token_id
        nft_list.append(res["information"])
    return nft_list


def check_user_own_nft_weapon(owner_address: str, token_id: int):
    url = f"https://th-api.klaytnapi.com/v2/contract/nft/{weapon_nft_address}/token/{str(hex(token_id))}"
    headers = {"x-chain-id": x_chain_id,
               "Authorization": Authorization}
    timeout = 5
    response = requests.get(url, headers=headers, timeout=timeout).json()
    if response['owner'] != owner_address.lower():
        return False
    return True

# print(get_armor_nft('0x3837246623e204de3b61f4871072f1f16142e33c'))
