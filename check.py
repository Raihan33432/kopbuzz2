from telethon.sync import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest, DeleteContactsRequest
from telethon.tl.types import InputPhoneContact
from dotenv import load_dotenv
import os

load_dotenv()
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
phone = os.getenv("PHONE_NUMBER")

session_name = "checker_session"

async def check_numbers(phone_list):
    result = {}
    async with TelegramClient(session_name, api_id, api_hash) as client:
        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            code = input("🔐 Enter the OTP code from Telegram: ")
            await client.sign_in(phone, code)

        contacts = [InputPhoneContact(client_id=i, phone=number, first_name="Check", last_name="") for i, number in enumerate(phone_list)]
        imported = await client(ImportContactsRequest(contacts))
        for user in imported.users:
            result[user.phone] = True
        for number in phone_list:
            if number not in result:
                result[number] = False
        await client(DeleteContactsRequest(imported.users))
    return result
