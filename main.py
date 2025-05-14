import requests
import time
from collections import defaultdict

class InstagramBot:
    def __init__(self, username, password, owner_ids=[]):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.user_id = None
        self.logged_in = False
        self.owner_ids = set(owner_ids)
        self.last_seen_msg_ids = {}
        self.user_message_count = defaultdict(int)  # user_id -> count

    def login(self):
        print("[*] Getting CSRF token...")
        headers = {
            'User-Agent': 'Mozilla/5.0',
        }
        r = self.session.get("https://www.instagram.com/accounts/login/", headers=headers)
        csrf = self.session.cookies.get("csrftoken")

        headers.update({
            "X-CSRFToken": csrf,
            "Referer": "https://www.instagram.com/accounts/login/",
            "X-Requested-With": "XMLHttpRequest",
        })

        enc_password = f"#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{self.password}"
        payload = {
            'username': self.username,
            'enc_password': enc_password,
            'queryParams': {},
            'optIntoOneTap': 'false'
        }

        print("[*] Attempting login...")
        res = self.session.post(
            "https://www.instagram.com/accounts/login/ajax/",
            headers=headers,
            data=payload
        )

        data = res.json()
        if data.get("authenticated"):
            self.logged_in = True
            self.user_id = self.get_own_user_id()
            print(f"[+] Logged in as {self.username} (user_id: {self.user_id})")
        else:
            print(f"[-] Login failed: {data}")

    def get_own_user_id(self):
        res = self.session.get(f"https://www.instagram.com/{self.username}/?__a=1&__d=dis")
        if res.status_code == 200:
            return str(res.json()["graphql"]["user"]["id"])
        return None

    def get_threads(self):
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://www.instagram.com/direct/inbox/',
        }
        inbox = self.session.get("https://i.instagram.com/api/v1/direct_v2/inbox/", headers=headers)
        if inbox.status_code == 200:
            return inbox.json().get("inbox", {}).get("threads", [])
        return []

    def send_message(self, thread_id, text):
        url = "https://i.instagram.com/api/v1/direct_v2/threads/broadcast/text/"
        headers = {
            'User-Agent': 'Instagram 123.0.0.21.114 Android',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = {
            'thread_ids': f'["{thread_id}"]',
            'text': text,
        }
        r = self.session.post(url, headers=headers, data=data)
        return r.status_code == 200

    def monitor_groups(self):
        if not self.logged_in:
            print("[-] Not logged in")
            return

        print("[*] Monitoring group chats...")

        while True:
            threads = self.get_threads()
            for thread in threads:
                thread_id = thread.get("thread_id")
                users = thread.get("users", [])
                if len(users) <= 1:
                    continue  # Skip non-group chats

                items = thread.get("items", [])
                if not items:
                    continue

                last_msg = items[0]
                last_msg_id = last_msg.get("item_id")

                # Avoid duplicate replies
                if self.last_seen_msg_ids.get(thread_id) == last_msg_id:
                    continue
                self.last_seen_msg_ids[thread_id] = last_msg_id

                sender_id = str(last_msg.get("user_id"))
                if not sender_id or sender_id == self.user_id or sender_id in self.owner_ids:
                    continue  # Skip own or owner messages

                # Track how many messages a user has sent
                self.user_message_count[sender_id] += 1
                reply_count = self.user_message_count[sender_id]

                # Fetch sender username
                user_info = self.session.get(f"https://i.instagram.com/api/v1/users/{sender_id}/info/")
                if user_info.status_code != 200:
                    continue
                sender_username = user_info.json()["user"]["username"]

                # Send replies equal to the count of messages sent
                for _ in range(reply_count):
                    msg = f"@{sender_username} OYY MSG MAT KAR"
                    success = self.send_message(thread_id, msg)
                    if success:
                        print(f"[+] Replied to @{sender_username}: {msg}")
                    else:
                        print(f"[-] Failed to reply to @{sender_username}")
                    time.sleep(2)  # Delay between each reply

            time.sleep(5)  # Main loop delay


if __name__ == "__main__":
    username = input("Enter your Instagram username: ")
    password = input("Enter your Instagram password: ")

    # Replace with actual owner user IDs (you can print them from debug)
    owner_ids = ["1234567890"]

    bot = InstagramBot(username, password, owner_ids=owner_ids)
    bot.login()

    if bot.logged_in:
        bot.monitor_groups()
