import asyncio

from bot import bot, HU_APP
from pyromod import listen
from asyncio.exceptions import TimeoutError

from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    SessionPasswordNeeded, FloodWait,
    PhoneNumberInvalid, ApiIdInvalid,
    PhoneCodeInvalid, PhoneCodeExpired
)

API_TEXT = """Hola, {}.
Este es el bot generador de sesiones de cadena de Pyrogram. Generaré String Session de tu cuenta de Telegram.

Por @InFoJosTel

Ahora envíe su `API_ID` igual que` APP_ID` para comenzar a generar sesión.

Obtenga `APP_ID` de https://my.telegram.org o @UseTGzKBot."""

HASH_TEXT = "Ahora envía tu `API_HASH`.\n\nObtener `API_HASH` desde https://my.telegram.org O @UseTGzKBot.\n\nPreciona /cancel cancelar tarea."
PHONE_NUMBER_TEXT = (
    "Ahora envíe el número de teléfono de su cuenta de Telegram en formato internacional. \n"
    "Incluido el código de país. Ejemplo: **+14154566376**\n\n"
    "Preciona /cancel cancelar tarea."
)

@bot.on_message(filters.private & filters.command("start"))
async def genStr(_, msg: Message):
    chat = msg.chat
    api = await bot.ask(
        chat.id, API_TEXT.format(msg.from_user.mention)
    )
    if await is_cancel(msg, api.text):
        return
    try:
        check_api = int(api.text)
    except Exception:
        await msg.reply("`API_ID` is Invalid.\nPreciona /start to Start again.")
        return
    api_id = api.text
    hash = await bot.ask(chat.id, HASH_TEXT)
    if await is_cancel(msg, hash.text):
        return
    if not len(hash.text) >= 30:
        await msg.reply("`API_HASH` is Invalid.\nPreciona /start to Start again.")
        return
    api_hash = hash.text
    while True:
        number = await bot.ask(chat.id, PHONE_NUMBER_TEXT)
        if not number.text:
            continue
        if await is_cancel(msg, number.text):
            return
        phone = number.text
        confirm = await bot.ask(chat.id, f'`Is "{phone}" correct? (y/n):` \n\nSend: `y` (If Yes)\nSend: `n` (If No)')
        if await is_cancel(msg, confirm.text):
            return
        if "y" in confirm.text:
            break
    try:
        client = Client("my_account", api_id=api_id, api_hash=api_hash)
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`\nPreciona /start to Start again.")
        return
    try:
        await client.connect()
    except ConnectionError:
        await client.disconnect()
        await client.connect()
    try:
        code = await client.send_code(phone)
        await asyncio.sleep(1)
    except FloodWait as e:
        await msg.reply(f"You have Floodwait of {e.x} Seconds")
        return
    except ApiIdInvalid:
        await msg.reply("API ID and API Hash are Invalid.\n\nPreciona /start to Start again.")
        return
    except PhoneNumberInvalid:
        await msg.reply("Your Phone Number is Invalid.\n\nPreciona /start to Start again.")
        return
    try:
        otp = await bot.ask(
            chat.id, ("An OTP is sent to your phone number, "
                      "Please enter OTP in `1 2 3 4 5` .format__(Space between each numbers!)__ \n\n"
                      "If Bot not sending OTP then try /restart and Start Task again with /start command to Bot.\n"
                      "Press /cancel to Cancel."), timeout=300)

    except TimeoutError:
        await msg.reply("Time limit reached of 5 min.\nPress /start to Start again.")
        return
    if await is_cancel(msg, otp.text):
        return
    otp_code = otp.text
    try:
        await client.sign_in(phone, code.phone_code_hash, phone_code=' '.join(str(otp_code)))
    except PhoneCodeInvalid:
        await msg.reply("Invalid Code.\n\nPress /start to Start again.")
        return
    except PhoneCodeExpired:
        await msg.reply("Code is Expired.\n\nPress /start to Start again.")
        return
    except SessionPasswordNeeded:
        try:
            two_step_code = await bot.ask(
                chat.id, 
                "Your account have Two-Step Verification.\nPlease enter your Password.\n\nPreciona /cancel to Cancel.",
                timeout=300
            )
        except TimeoutError:
            await msg.reply("`Time limit reached of 5 min.\n\nPreciona /start to Start again.`")
            return
        if await is_cancel(msg, two_step_code.text):
            return
        new_code = two_step_code.text
        try:
            await client.check_password(new_code)
        except Exception as e:
            await msg.reply(f"**ERROR:** `{str(e)}`")
            return
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`")
        return
    try:
        session_string = await client.export_session_string()
        await client.send_message("me", f"***Your Pyrogram Session***\n\n```{session_string}``` \n\nBy [@UsePyrogramBot](tg://openmessage?user_id=1860890017) \n⬆️ This String Session is generated using https://replit.com/@ZauteKm/GenerateStringSession \nPlease subscribe ❤️ [@ZauTeKm](https://telegra.ph/ZauTe-Telegram-Official-Channel--Group-04-18)")
        await client.disconnect()
        text = "String Session is Successfully Generated.\nClick on Below Button."
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Show String Session", url=f"tg://openmessage?user_id={chat.id}")]]
        )
        await bot.send_message(chat.id, text, reply_markup=reply_markup)
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`")
        return


@bot.on_message(filters.private & filters.command("restart"))
async def restart(_, msg: Message):
    await msg.reply("Restarted Bot!")
    HU_APP.restart()


@bot.on_message(filters.private & filters.command("help"))
async def restart(_, msg: Message):
    out = f"""
Hi, {msg.from_user.mention}. This is Pyrogram Session String Generator Bot. \
I will give you `STRING_SESSION` for your UserBot.

It needs `API_ID`, `API_HASH`, Phone Number and One Time Verification Code. \
Which will be sent to your Phone Number.
You have to put **OTP** in `1 2 3 4 5` this .format__(Space between each numbers!)__

**NOTE:** If bot not Sending OTP to your Phone Number than send /restart Command and again send /start to Start your Process. 

Must Join Channel for Bot Updates !!
"""
    reply_markup = InlineKeyboardMarkup(
        [[
              InlineKeyboardButton('🗣️ Feedback', url='https://telegram.me/InFoJosTelGroup'),
              InlineKeyboardButton(' Channel 📢', url='https://telegram.me/InFoJosTel')
              ],[
              InlineKeyboardButton('🙄 Source', url='https://githup.com/InFoJosTel/String-Session-Generator'),
              InlineKeyboardButton('Bot Lists 🤖', url='https://t.me/TG_BotList/37'),
              InlineKeyboardButton('Music 👨‍🎤', url='https://t.me/joinchat/7gSUxv6vgQE3M2Fl')
              ],[
              InlineKeyboardButton('🔻 Subscribe Now YouTube 🔻', url='https://youtube.com/playlist?list=PLzkiTywVmsSfmhaDdWNZ5PRmmMKGTIxPJ')
       ]]
    )
    await msg.reply(out, reply_markup=reply_markup)


async def is_cancel(msg: Message, text: str):
    if text.startswith("/cancel"):
        await msg.reply("Process Cancelled.")
        return True
    return False

if __name__ == "__main__":
    bot.run()
