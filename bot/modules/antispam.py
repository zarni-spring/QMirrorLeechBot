from bot import LOGGER, dispatcher, app
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import auto_delete_message, sendMessage, deleteMessage, sendPhoto, editMessage
from typing import Tuple, Optional
from telegram.ext import ChatMemberHandler, CallbackContext
from telegram import Update, ChatMember, ParseMode, ChatMemberUpdated

def extract_status_change(
    chat_member_update: ChatMemberUpdated,
) -> Optional[Tuple[bool, bool]]:
    """Takes a ChatMemberUpdated instance and extracts whether the 'old_chat_member' was a member
    of the chat and whether the 'new_chat_member' is a member of the chat. Returns None, if
    the status didn't change.
    """
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))

    if status_change is None: return None

    old_status, new_status = status_change
    was_member = (
        old_status
        in [
            ChatMember.MEMBER,
            ChatMember.CREATOR,
            ChatMember.ADMINISTRATOR,
        ]
        or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    )
    is_member = (
        new_status
        in [
            ChatMember.MEMBER,
            ChatMember.CREATOR,
            ChatMember.ADMINISTRATOR,
        ]
        or (new_status == ChatMember.RESTRICTED and new_is_member is True)
    )

    return was_member, is_member



def antispam(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.PRIVATE: return
    result = extract_status_change(update.chat_member)
    if result is None: return
    was_member, is_member = result
    cause_name = update.chat_member.from_user.mention_html()
    member_name = update.chat_member.new_chat_member.user.mention_html()

    if not was_member and is_member:
        try: app.ban_chat_member(update.effective_chat, update.chat_member.new_chat_member.user.id)
        except Exception as o: LOGGER.error(o)
        LOGGER.info(
            f"{member_name} was added by {cause_name}. Welcome!",
            parse_mode=ParseMode.HTML,
        )
    elif was_member and not is_member:
        LOGGER.info(
            f"{member_name} is no longer with us. Thanks a lot, {cause_name} ...",
            parse_mode=ParseMode.HTML,
        )

antispam_handler = ChatMemberHandler(antispam, ChatMemberHandler.CHAT_MEMBER, run_async=True)
dispatcher.add_handler(antispam_handler)
