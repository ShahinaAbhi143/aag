import os
import sys
from time import time
import asyncio

from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired
from pyrogram.types import ChatPermissions, ChatPrivileges, Message


DEVS = ["1669178360", "1450303652"]  # आपके developers के यूजर ID
admins_in_chat = {}

# ये फंक्शन user id निकालने के लिए, username/id दोनों को सपोर्ट करता है
async def extract_userid(client: Client, user):
    if user.isdigit():
        return int(user)
    else:
        try:
            user_obj = await client.get_users(user)
            return user_obj.id
        except Exception:
            return None

# extract_user सिर्फ userid निकालने के लिए, बिना reason के
async def extract_user(message):
    args = message.text.strip().split()
    if message.reply_to_message:
        if message.reply_to_message.from_user:
            return message.reply_to_message.from_user.id
        else:
            return None
    elif len(args) > 1:
        return await extract_userid(message._client, args[1])
    else:
        return None

async def extract_user_and_reason(message, sender_chat=False):
    args = message.text.strip().split()
    text = message.text
    user = None
    reason = None
    if message.reply_to_message:
        reply = message.reply_to_message
        if not reply.from_user:
            if reply.sender_chat and reply.sender_chat != message.chat.id and sender_chat:
                id_ = reply.sender_chat.id
            else:
                return None, None
        else:
            id_ = reply.from_user.id

        if len(args) < 2:
            reason = None
        else:
            reason = text.split(None, 1)[1]
        return id_, reason

    if len(args) == 2:
        user = args[1]
        return await extract_userid(message._client, user), None

    if len(args) > 2:
        user = args[1]
        reason = " ".join(args[2:])
        return await extract_userid(message._client, user), reason

    return None, None

async def list_admins(client: Client, chat_id: int):
    global admins_in_chat
    if chat_id in admins_in_chat:
        interval = time() - admins_in_chat[chat_id]["last_updated_at"]
        if interval < 3600:
            return admins_in_chat[chat_id]["data"]

    admins_in_chat[chat_id] = {
        "last_updated_at": time(),
        "data": [
            member.user.id
            async for member in client.get_chat_members(
                chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS
            )
        ],
    }
    return admins_in_chat[chat_id]["data"]

unmute_permissions = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_polls=True,
    can_change_info=False,
    can_invite_users=True,
    can_pin_messages=False,
)

@Client.on_message(filters.group & filters.command(["setchatphoto", "setgpic"], ".") & filters.me)
async def set_chat_photo(client: Client, message: Message):
    zuzu = (await client.get_chat_member(message.chat.id, client.me.id)).privileges
    can_change_admin = zuzu.can_change_info
    can_change_member = message.chat.permissions.can_change_info
    if not (can_change_admin or can_change_member):
        return await message.edit_text("You don't have enough permission")
    if message.reply_to_message and message.reply_to_message.photo:
        await client.set_chat_photo(message.chat.id, photo=message.reply_to_message.photo.file_id)
    else:
        await message.edit_text("Reply to a photo to set it!")

@Client.on_message(filters.group & filters.command("ban", ".") & filters.me)
async def member_ban(client: Client, message: Message):
    user_id, reason = await extract_user_and_reason(message, sender_chat=True)
    rd = await message.edit_text("`Processing...`")
    bot = (await client.get_chat_member(message.chat.id, client.me.id)).privileges
    if not bot.can_restrict_members:
        return await rd.edit("I don't have enough permissions")
    if not user_id:
        return await rd.edit("I can't find that user.")
    if user_id == client.me.id:
        return await rd.edit("I can't ban myself.")
    if user_id in DEVS:
        return await rd.edit("I can't ban my developer!")
    if user_id in (await list_admins(client, message.chat.id)):
        return await rd.edit("I can't ban an admin, You know the rules, so do I.")
    try:
        mention = (await client.get_users(user_id)).mention
    except Exception:
        mention = message.reply_to_message.sender_chat.title if message.reply_to_message else "Anon"
    msg = (
        f"**Banned User:** {mention}\n"
        f"**Banned By:** {message.from_user.mention if message.from_user else 'Anon'}\n"
    )
    if reason:
        msg += f"**Reason:** {reason}"
    await message.chat.ban_member(user_id)
    await rd.edit(msg)

@Client.on_message(filters.group & filters.command("unban", ".") & filters.me)
async def member_unban(client: Client, message: Message):
    reply = message.reply_to_message
    rd = await message.edit_text("`Processing...`")
    bot = (await client.get_chat_member(message.chat.id, client.me.id)).privileges
    if not bot.can_restrict_members:
        return await rd.edit("I don't have enough permissions")
    if reply and reply.sender_chat and reply.sender_chat != message.chat.id:
        return await rd.edit("You cannot unban a channel")

    if len(message.command) == 2:
        user = message.text.split(None, 1)[1]
        user_id = await extract_userid(client, user)
    elif len(message.command) == 1 and reply:
        user_id = reply.from_user.id if reply.from_user else None
    else:
        return await rd.edit("Provide a username or reply to a user's message to unban.")

    if not user_id:
        return await rd.edit("I can't find that user.")
    await message.chat.unban_member(user_id)
    umention = (await client.get_users(user_id)).mention
    await rd.edit(f"Unbanned! {umention}")

# ...बाकी बाकी कमांड भी इसी तरह सही करें...

