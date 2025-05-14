import requests
import time
import json
import pickle
from bot import InstagramBot

def login_and_save_session(username, password):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://www.instagram.com/accounts/login/"
    })

    session.get("https://www.instagram.com/")
    csrf = session.cookies.get("csrftoken")

    session.headers.update({"X-CSRFToken": csrf})
    timestamp = int(time.time())

    payload = {
        "username": username,
        "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:{timestamp}:{password}",
        "queryParams": {},
        "optIntoOneTap": "false"
    }

    res = session.post("https://www.instagram.com/accounts/login/ajax/", data=payload)
    result = res.json()

    if "checkpoint_url" in result:
        challenge_url = "https://www.instagram.com" + result["checkpoint_url"]
        print("[!] Challenge required, choosing email verification.")
        session.post(challenge_url, data={"choice": 1})

        code = input("Enter the verification code sent to your email: ")
        res = session.post(challenge_url, data={"security_code": code})
        if res.json().get("status") == "ok":
            print("[+] Logged in successfully after verification.")
        else:
            print("[-] Verification failed.")
            return None
    elif result.get("authenticated"):
        print("[+] Logged in successfully.")
    else:
        print("[-] Login failed.")
        return None

    # Save session cookies to file
    with open("session.pkl", "wb") as f:
        pickle.dump(session.cookies, f)

    return session

def load_session():
    session = requests.Session()
    with open("session.pkl", "rb") as f:
        session.cookies.update(pickle.load(f))
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    })
    return session

if __name__ == "__main__":
    choice = input("1 = Login\n2 = Load Session\nChoose: ")
    if choice == "1":
        u = input("Username: ")
        p = input("Password: ")
        session = login_and_save_session(u, p)
    else:
        session = load_session()

    if session:
        bot = InstagramBot(session)
        bot.monitor_groups()
