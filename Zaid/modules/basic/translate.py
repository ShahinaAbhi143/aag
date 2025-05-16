from Zaid.modules.help import *
import os
from pyrogram import filters, Client
from pyrogram.types import Message
from googletrans import Translator  # googletrans का सिंक्रोनस वर्शन
from Zaid.helper.utility import get_arg


@Client.on_message(filters.command(["tr", "translate"], ["."]) & filters.me)
async def pytrans_tr(_, message: Message):
    tr_msg = await message.edit("`Processing...`")
    r_msg = message.reply_to_message
    args = get_arg(message)

    # Initialize translator (googletrans is sync, but okay to call here)
    translator = Translator()

    if r_msg:
        if r_msg.text:
            to_tr = r_msg.text
        else:
            return await tr_msg.edit("`Reply to a message that contains text!`")

        if not args:
            return await tr_msg.edit("`Please define a destination language!` \n\n**Ex:** `.tr si`")
        dest_lang = args.split(" ")[0]

    elif args:
        sp_args = args.split(None, 1)
        if len(sp_args) == 2:
            dest_lang = sp_args[0]
            to_tr = sp_args[1]
        else:
            return await tr_msg.edit("`Please provide language and text to translate!` \n\n**Ex:** `.tr en Hello`")
    else:
        return await tr_msg.edit("`Please provide text to translate or reply to a message.`")

    try:
        translation = translator.translate(to_tr, dest=dest_lang)
    except Exception as e:
        return await tr_msg.edit(f"`Translation failed:` {e}")

    tred_txt = f"""
**Translation Engine**: `googletrans`
**Translated to:** `{dest_lang}`
**Translation:**
`{translation.text}`
"""

    if len(tred_txt) > 4096:
        await tr_msg.edit("`Translated text is too long, sending as a file...`")
        with open("translated.txt", "w", encoding="utf-8") as tr_txt_file:
            tr_txt_file.write(tred_txt)
        await tr_msg.reply_document("translated.txt")
        os.remove("translated.txt")
        await tr_msg.delete()
    else:
        await tr_msg.edit(tred_txt)


add_command_help(
    "translate",
    [
        [".tr", "Translate some text by giving a text or replying to that text/caption."],
    ],
)
