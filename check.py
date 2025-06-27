from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.errors.rpcerrorlist import PhoneNumberInvalidError
import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

async def check_numbers(numbers):
    result = {}
    async with client:
        try:
            contacts = await client(functions.contacts.ImportContactsRequest(
                contacts=[types.InputPhoneContact(client_id=i, phone=number, first_name="Test", last_name="User")
                          for i, number in enumerate(numbers)]
            ))
            for user in contacts.users:
                result[user.phone] = True
            for number in numbers:
                if number not in result:
                    result[number] = False
        except Exception as e:
            for number in numbers:
                result[number] = False
    return result
