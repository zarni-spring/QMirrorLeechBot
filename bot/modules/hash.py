# https://github.com/HuzunluArtemis/FileHashBot/

import hashlib, os, time
from telegram.ext import CommandHandler
from bot import LOGGER, VIRUSTOTAL_API, VIRUSTOTAL_FREE, dispatcher, app
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import editMessage, sendMessage


def HumanBytes(size):
    if not size: return ""
    power = 2 ** 10
    n = 0
    Dic_powerN = {0: " ", 1: "K", 2: "M", 3: "G", 4: "T"}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + "iB"


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]


def hash(update, context):
    message = update.effective_message
    VtPath = os.path.join("Hasher", str(message.from_user.id))
    if not os.path.exists("Hasher"): os.makedirs("Hasher")
    if not os.path.exists(VtPath): os.makedirs(VtPath)
    file = None
    sent = sendMessage('Running Hasher. Wait for finish.', context.bot, update)
    if message.reply_to_message and message.reply_to_message.document:
        try:
            editMessage(f"Trying to download. Please wait.", sent)
            filename = os.path.join(VtPath, message.reply_to_message.document.file_name)
            file = app.download_media(message=message.reply_to_message.document, file_name=filename)
        except Exception as e:
            LOGGER.error(e)
            file = None
    if file:
        hashStartTime = time.time()
        try:
            with open(file, "rb") as f:
                md5 = hashlib.md5()
                sha1 = hashlib.sha1()
                sha224 = hashlib.sha224()
                sha256 = hashlib.sha256()
                sha512 = hashlib.sha512()
                sha384 = hashlib.sha384()
                while chunk := f.read(8192):
                    md5.update(chunk)
                    sha1.update(chunk)
                    sha224.update(chunk)
                    sha256.update(chunk)
                    sha512.update(chunk)
                    sha384.update(chunk)
        except Exception as a:
            LOGGER.info(str(a))
            f"Hashing error.\n\n{str(a)}"
            try: os.remove(file)
            except: pass
            return editMessage("Hashing error. Check Logs.", sent)
        # hash text
        hashFinishTime = time.time()
        finishedText = "🍆 File: `{}`\n".format(message.reply_to_message.document.file_name)
        finishedText += "🍇 Size: `{}`\n".format(HumanBytes(message.reply_to_message.document.file_size))
        finishedText += "🍓 MD5: `{}`\n".format(md5.hexdigest())
        finishedText += "🍌 SHA1: `{}`\n".format(sha1.hexdigest())
        finishedText += "🍒 SHA224: `{}`\n".format(sha224.hexdigest())
        finishedText += "🍑 SHA256: `{}`\n".format(sha256.hexdigest())
        finishedText += "🥭 SHA512: `{}`\n".format(sha512.hexdigest())
        finishedText += "🍎 SHA384: `{}`\n".format(sha384.hexdigest())
        timeTaken = f"🥚 Hash Time: `{TimeFormatter((hashFinishTime - hashStartTime) * 1000)}`"
        editMessage(f"Calculated file hashes\n{timeTaken}\n\n{finishedText}", sent)
    else:
        help_msg = "<b>Reply to message including file:</b>"
        help_msg += f"\n<code>/{BotCommands.HashCommand}" + " {message}" + "</code>"
        editMessage(help_msg, sent)
    try: os.remove(file)
    except: pass


hash_handler = CommandHandler(BotCommands.HashCommand, hash,
    filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(hash_handler)
