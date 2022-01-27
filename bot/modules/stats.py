# https://github.com/Appeza/tg-mirror-leech-bot edited by HuzunluArtemis

from psutil import disk_usage, cpu_percent, swap_memory, cpu_count, virtual_memory, net_io_counters
from bot.helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from time import time
from subprocess import run
import requests
import math
from threading import Thread
from bot import LOGGER, dispatcher, botStartTime, HEROKU_API_KEY, HEROKU_APP_NAME
from telegram.ext import CommandHandler
from bot.helper.telegram_helper.message_utils import auto_delete_message, sendMessage
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.modules.wayback import getRandomUserAgent


def getHerokuDetails(h_api_key, h_app_name):
    try: import heroku3
    except ModuleNotFoundError: run("pip install heroku3", capture_output=False, shell=True)
    try: import heroku3
    except Exception as f:
        LOGGER.warning("heroku3 cannot imported. add to your deployer requirements.txt file.")
        LOGGER.warning(f)
        return
    if (not h_api_key) or (not h_app_name): return None
    try:
        heroku_api = "https://api.heroku.com"
        Heroku = heroku3.from_key(h_api_key)
        app = Heroku.app(h_app_name)
        useragent = getRandomUserAgent()
        user_id = Heroku.account().id
        headers = {
            "User-Agent": useragent,
            "Authorization": f"Bearer {h_api_key}",
            "Accept": "application/vnd.heroku+json; version=3.account-quotas",
        }
        path = "/accounts/" + user_id + "/actions/get-quota"
        session = requests.Session()
        result = (session.get(heroku_api + path, headers=headers)).json()
        # Account Quota
        quota = result["account_quota"]
        quota_used = result["quota_used"]
        quota_remain = quota - quota_used
        quota_percent = math.floor(quota_remain / quota * 100)
        minutes_remain = quota_remain / 60
        hours = math.floor(minutes_remain / 60)
        minutes = math.floor(minutes_remain % 60)
        day = math.floor(hours / 24)

        # App Quota
        Apps = result["apps"]
        for apps in Apps:
            if apps.get("app_uuid") == app.id:
                AppQuotaUsed = apps.get("quota_used") / 60
                AppPercent = math.floor(apps.get("quota_used") * 100 / quota)
                break
        else:
            AppQuotaUsed = 0
            AppPercent = 0

        AppHours = math.floor(AppQuotaUsed / 60)
        AppMinutes = math.floor(AppQuotaUsed % 60)
        return f"<b>{app.name} Usage:</b> <code>{AppHours}h{AppMinutes}m</code> {AppPercent}%\n" \
        f"<b>Dyno Remaining:</b> <code>{hours}h{minutes}m</code> {quota_percent}%\n" \
        f"<b>Estimated Expired:</b> <code>{day}d</code>"
    except Exception as g:
        LOGGER.error(g)
        return None

def stats(update, context):
    currentTime = get_readable_time(time() - botStartTime)
    total, used, free, disk= disk_usage('/')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(net_io_counters().bytes_sent)
    recv = get_readable_file_size(net_io_counters().bytes_recv)
    cpuUsage = cpu_percent(interval=0.5)
    p_core = cpu_count(logical=False)
    t_core = cpu_count(logical=True)
    swap = swap_memory()
    swap_p = swap.percent
    swap_t = get_readable_file_size(swap.total)
    swap_u = get_readable_file_size(swap.used)
    memory = virtual_memory()
    mem_p = memory.percent
    mem_t = get_readable_file_size(memory.total)
    mem_a = get_readable_file_size(memory.available)
    mem_u = get_readable_file_size(memory.used)
    stats = f'<b>Bot Uptime:</b> {currentTime} | '\
            f'<b>Total Disk Space:</b> {total} | '\
            f'<b>Used:</b> {used} | <b>Free:</b> {free} | '\
            f'<b>Upload:</b> {sent} | '\
            f'<b>Download:</b> {recv} | '\
            f'<b>CPU:</b> {cpuUsage}% | '\
            f'<b>RAM:</b> {mem_p}% | '\
            f'<b>DISK:</b> {disk}% | '\
            f'<b>Physical Cores:</b> {p_core} | '\
            f'<b>Total Cores:</b> {t_core} | '\
            f'<b>SWAP:</b> {swap_t} | <b>Used:</b> {swap_u}% | '\
            f'<b>Memory Total:</b> {mem_t} | '\
            f'<b>Memory Free:</b> {mem_a} | '\
            f'<b>Memory Used:</b> {mem_u}\n'
    heroku = getHerokuDetails(HEROKU_API_KEY, HEROKU_APP_NAME)
    if heroku: stats += heroku
    reply_message = sendMessage(stats, context.bot, update)
    Thread(target=auto_delete_message, args=(context.bot, update.message, reply_message)).start()

stats_handler = CommandHandler(BotCommands.StatsCommand, stats,
    filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(stats_handler)