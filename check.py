from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest, DeleteContactsRequest
from telethon.tl.types import InputPhoneContact
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
phone = os.getenv("PHONE_NUMBER")
session_name = "checker_session"

async def check_numbers(phone_list):
    """
    Given a list of phone numbers (strings), returns a dict mapping each number to
    True if a Telegram account exists, False otherwise.
    Requires an existing authorized Telethon session named checker_session.session.
    """
    result = {}
    # Use existing session (assumes session file already created and authorized)
    async with TelegramClient(session_name, api_id, api_hash) as client:
        # Import contacts for the given phone numbers
        contacts = [InputPhoneContact(client_id=i, phone=number, first_name="User", last_name="")
                    for i, number in enumerate(phone_list)]
        imported = await client(ImportContactsRequest(contacts))
        # Mark found users
        for user in imported.users:
            if user.phone:
                result[user.phone] = True
        # Any numbers not found in imported.users are False
        for number in phone_list:
            result.setdefault(number, False)
        # Clean up imported contacts
        await client(DeleteContactsRequest(imported.users))
    return result
