# written by huzunluartemis

from threading import Thread
from bot import COMBOT_CAS, LOGGER, SPAMWATCH_API, USERGE_ANTISPAM_API, dispatcher, app
from bot.helper.telegram_helper.message_utils import auto_delete_message, sendMessage
from typing import Tuple, Optional
from telegram.ext import ChatMemberHandler, CallbackContext
from telegram import Update, ChatMember, ChatMemberUpdated
import requests

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


def checkSpamWatch(userid):
    userid = str(userid)
    if not SPAMWATCH_API: return None
    api = 'https://api.spamwat.ch'
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {SPAMWATCH_API}"})
    req = session.request('get', f'{api}/banlist/{userid}')
    if not req.status_code == 200: return None
    info = "#Spamwatch Ban Info:"
    try:
        admin = req.json()['admin']
        id = req.json()['id']
        reason = req.json()['reason']
        message = req.json()['message']
        date = req.json()['date']
        if admin: info += f"\nAdmin: {admin}"
        if id: info += f"\nID: {id}"
        if reason: info += f"\nReason: {reason}"
        if message: info += f"\nMessage: {message}"
        if date: info += f"\nDate: {date}"
    except: pass
    return info


def CombotAntiSpamCheck(userid):
    if not COMBOT_CAS: return None
    api = f"https://api.cas.chat/check?user_id={userid}"
    session = requests.Session()
    req = session.request('get', api)
    if not int(req.status_code) == 200: return None
    if not bool(req.json()['ok']): return None
    info = "#Combot Ban Info:"
    result = req.json()['result']
    if not result: return info
    try:
        offenses = result['offenses']
        time_added = result['time_added']
        info += f"\nOffenses: {offenses}"
        info += f"\nTime: {time_added}"
    except: pass
    return info


def UsergeAntiSpamCheck(userid):
    if not USERGE_ANTISPAM_API: return None
    api = f"https://api.userge.tk/ban?api_key={USERGE_ANTISPAM_API}&user_id={userid}"
    session = requests.Session()
    req = session.request('get', api)
    if not bool(req.json()['success']): return None
    info = "#Userge Ban Info:"
    try:
        reason = req.json()['reason']
        date = req.json()['date']
        bb_user_id = req.json()['banned_by']['user_id']
        bb_user_name = req.json()['banned_by']['name']
        if reason: info += f"\nReason: {reason}"
        if date: info += f"\nDate: {date}"
        if bb_user_name: info += f"\nBanned by: {bb_user_name}"
        if bb_user_id: info += f" ({bb_user_id})"
    except: pass
    return info


def antispam(update: Update, context: CallbackContext) -> None:
    if (not SPAMWATCH_API) and (not COMBOT_CAS) and (not USERGE_ANTISPAM_API): return
    result = extract_status_change(update.chat_member)
    if result is None: return
    was_member, is_member = result
    cause_name = update.chat_member.from_user.mention_html()
    member_name = update.chat_member.new_chat_member.user.mention_html()
    if was_member and (not is_member): return
    banned = None
    if SPAMWATCH_API: banned = checkSpamWatch(update.chat_member.new_chat_member.user.id)
    elif not banned:
        if COMBOT_CAS: banned = CombotAntiSpamCheck(update.chat_member.new_chat_member.user.id)
    elif not banned:
        if USERGE_ANTISPAM_API: banned = UsergeAntiSpamCheck(update.chat_member.new_chat_member.user.id)
    if banned:
        try:
            app.ban_chat_member(update.effective_chat.id, update.chat_member.new_chat_member.user.id)
            success = "Success"
        except Exception as o:
            success = "Unsuccess"
            LOGGER.error(o)
        success = "Unsuccess"
        swtc = f"\nUser: {member_name}"
        swtc += f"\nAdded by {cause_name}"
        swtc += f"\nID: <code>{update.chat_member.new_chat_member.user.id}<\code>"
        swtc += f"\nBan: {success}"
        swtc += f"\n\n{banned}"
        reply_message = sendMessage(swtc, context.bot, update)
        Thread(target=auto_delete_message, args=(context.bot, update.message, reply_message)).start()

if SPAMWATCH_API or COMBOT_CAS or USERGE_ANTISPAM_API:
    antispam_handler = ChatMemberHandler(antispam, ChatMemberHandler.CHAT_MEMBER, run_async=True)
    dispatcher.add_handler(antispam_handler)
else: LOGGER.info('No using any Spam Protection.')
