import requests
import time
import threading
import json

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
BASE_URL = "https://i.instagram.com/api/v1/"
OWNER_IDS = ["123456789", "987654321"]  # Replace with real owner IDs

class InstagramBot:
    def __init__(self, session):
        self.session = session
        self.username = self.get_current_user()
        self.stop_flag = False
        self.last_seen_timestamps = {}

    def get_current_user(self):
        res = self.session.get(BASE_URL + "accounts/current_user/")
        if res.status_code == 200:
            return res.json()["user"]["username"]
        return None

    def get_group_chats(self):
        res = self.session.get(BASE_URL + "direct_v2/inbox/")
        if res.status_code == 200:
            threads = res.json().get('inbox', {}).get('threads', [])
            return threads
        return []

    def send_message(self, thread_id, text):
        payload = {
            "thread_ids": f"[\"{thread_id}\"]",
            "text": text
        }
        url = BASE_URL + "direct_v2/threads/broadcast/text/"
        return self.session.post(url, data=payload)

    def monitor_groups(self):
        print(f"Logged in as @{self.username}")
        while not self.stop_flag:
            threads = self.get_group_chats()
            for thread in threads:
                thread_id = thread["thread_id"]
                items = thread.get("items", [])
                unseen_messages = []

                for message in reversed(items):
                    user_id = message.get("user_id")
                    if not user_id or user_id in OWNER_IDS:
                        continue
                    if message.get("item_type") != "text":
                        continue
                    if message.get("user_id") == self.get_user_id():
                        continue

                    timestamp = message["timestamp"]
                    if thread_id in self.last_seen_timestamps and timestamp <= self.last_seen_timestamps[thread_id]:
                        continue

                    unseen_messages.append(message)

                if unseen_messages:
                    count = len(unseen_messages)
                    sender = unseen_messages[-1]["user_id"]
                    username = unseen_messages[-1]["user"]["username"]
                    reply = f"@{username} OYY MSG MAT KAR"

                    for _ in range(count):
                        self.send_message(thread_id, reply)
                        print(f"Replied to @{username} in thread {thread_id}")
                        time.sleep(2)  # Delay between replies

                    self.last_seen_timestamps[thread_id] = unseen_messages[-1]["timestamp"]

            time.sleep(5)

    def get_user_id(self):
        res = self.session.get(BASE_URL + "accounts/current_user/")
        return res.json().get("user", {}).get("pk", "")

    def stop(self):
        self.stop_flag = True
