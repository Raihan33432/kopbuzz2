from telethon.sync import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest, DeleteContactsRequest
from telethon.tl.types import InputPhoneContact
import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = "checker_session"

async def check_numbers(phone_list):
    result = {}
    async with TelegramClient(SESSION, API_ID, API_HASH) as client:
        contacts = [InputPhoneContact(client_id=i, phone=number, first_name="Check", last_name="") for i, number in enumerate(phone_list)]
        try:
            imported = await client(ImportContactsRequest(contacts))
            for user in imported.users:
                result[user.phone] = True
            for number in phone_list:
                if number not in result:
                    result[number] = False
            await client(DeleteContactsRequest(imported.users))
        except Exception:
            for number in phone_list:
                result[number] = False
    return result
