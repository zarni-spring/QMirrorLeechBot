from bot.helper.ext_utils.shortenurl import short_url
from telegram.ext import CommandHandler
import re
from bot.helper.telegram_helper.filters import CustomFilters
from bot import dispatcher
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import auto_delete_message, sendMessage, deleteMessage, sendPhoto, editMessage

def shortener(update, context):
    message = update.effective_message
    sent = sendMessage("Shortening", context.bot, update)
    link = None
    if message.reply_to_message: link = message.reply_to_message.text
    else:
        link = message.text.split(' ', 1)
        if len(link) != 2:
            help_msg = "<b>Send link after command:</b>"
            help_msg += f"\n<code>/{BotCommands.ShortenerCommand}" + " {link}" + "</code>"
            help_msg += "\n<b>By replying to message (including link):</b>"
            help_msg += f"\n<code>/{BotCommands.ShortenerCommand}" + " {message}" + "</code>"
            return editMessage(help_msg, sent)
        link = link[1]
    try: link = re.match(r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*", link)[0]
    except TypeError: return editMessage('Not a valid link.', sent)
    return editMessage(short_url(link), sent)


shortener_handler = CommandHandler(BotCommands.ShortenerCommand, shortener,
    CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)

dispatcher.add_handler(shortener_handler)
