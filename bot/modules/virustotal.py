import subprocess
from telegram import Message
import re, hashlib, requests, os
from telegram.ext import CommandHandler
from bot import LOGGER, VIRUSTOTAL_API, VIRUSTOTAL_FREE, dispatcher, app
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import editMessage, sendMessage

base_url = 'https://www.virustotal.com/vtapi/v2/file/'
apiKey = VIRUSTOTAL_API

def get_report(file_hash):
    '''
    :param file_hash: md5/sha1/sha256
    :return: json response / None
    '''
    try:
        LOGGER.info("VirusTotal: Check for existing report")
        url = base_url + 'report'
        params = {
            'apikey': apiKey,
            'resource': file_hash
        }
        headers = {"Accept-Encoding": "gzip, deflate"}
        try:
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 403:
                LOGGER.error("VirusTotal Permission denied, wrong api key?")
                return None
        except:
            LOGGER.error("VirusTotal ConnectionError, check internet connectivity")
            return None
        try:
            return response.json()
        except ValueError:
            return None
    except Exception as e:
        LOGGER.error(e)
        return None

def upload_file(file_path):
    '''
    :param file_path: file path to upload
    :return: json response / None
    '''
    try:
        url = base_url + "scan"
        if os.path.getsize(file_path) > 32*1024*1024:
            url = 'https://www.virustotal.com/vtapi/v2/file/scan/upload_url'
            params = {'apikey':apiKey}
            response = requests.get(url, params=params)
            upload_url_json = response.json()
            url = upload_url_json['upload_url']
        files = {'file': open(file_path, 'rb')}
        headers = {"apikey": apiKey}
        try:
            response = requests.post(url, files=files, data=headers)
            if response.status_code == 403:
                LOGGER.error("VirusTotal Permission denied, wrong api key?")
                return None
        except:
            LOGGER.error("VirusTotal ConnectionError, check internet connectivity")
            return None
        json_response = response.json()
        return json_response

    except:
        LOGGER.error("VirusTotal upload_file")
        return None

def get_result(file_path):
    '''
    Uoloading a file and getting the approval msg from VT or fetching existing report
    :param file_path: file's path
    :param file_hash: file's hash - md5/sha1/sha256
    :return: VirusTotal result json / None upon error
    '''
    hash = None
    if os.path.isfile(file_path): hash = getMD5(path=file_path)
    try: hash = re.match(r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*", file_path)[0]
    except Exception: hash = None
    if not hash: hash = file_path
    try:
        report = get_report(hash)
        LOGGER.info(report)
        if report:
            LOGGER.info("[INFO] Report found.")
            if int(report['response_code']) == 1:
                return report
            elif file_path:
                LOGGER.info("[INFO] VirusTotal: file upload")
                upload_response = upload_file(file_path)
                return upload_response
    except Exception as e: LOGGER.info(e)


def getMD5(path):
    with open(path, "rb") as f:
        file_hash = hashlib.md5()
        chunk = f.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(8192)
    return file_hash.hexdigest()


def getResultAsReadable(result):
    if result and 'scans' in result:
        stro = []
        scans = result['scans']
        for i in scans:
            if not bool((scans[i]['detected'])): continue
            stro.append(i)
        details = "\nTotal: " + str(result['total'])  + \
            " | Positives: " + str(result['positives']) + \
            " | Negatives: " + str(len(scans) - int(result['positives']))
        if result['verbose_msg']: details += f"Message: <code>{result['verbose_msg']}</code>"
        if result['scan_id']: details += f"\nScan ID: <code>{result['scan_id']}</code>"
        if result['md5']: details += f"\nMD5: <code>{result['md5']}</code>"
        if result['sha1']: details += f"\nSHA1: <code>{result['sha1']}</code>"
        if result['sha256']: details += f"\nSHA256: <code>{result['sha256']}</code>"
        if result['permalink']: details += f"\nLink: {result['permalink']}"
        if len(stro) == 0: return "File is clean like a baby" + details
        else: return "Detections: " + ", ".join(stro) + details
    elif result and 'scan_id' in result:
        stro = ""
        if result['verbose_msg']: stro += f"Message: <code>{result['verbose_msg']}</code>"
        if result['scan_id']: stro += f"\nScan ID: <code>{result['scan_id']}</code>"
        if result['md5']: stro += f"\nMD5: <code>{result['md5']}</code>"
        if result['sha1']: stro += f"\nSHA1: <code>{result['sha1']}</code>"
        if result['sha256']: stro += f"\nSHA256: <code>{result['sha256']}</code>"
        if result['permalink']: stro += f"\nLink: {result['permalink']}"
        return stro
    else:
        LOGGER.error(result)
        return "Something went wrong. Check Logs."

def humanbytes(size, byte=True):
    """Hi human, you can't read bytes?"""
    if not byte: size = size / 8 # byte or bit ?
    power = 2 ** 10
    zero = 0
    units = {0: "", 1: "KiB", 2: "MiB", 3: "GiB", 4: "TiB"}
    while size > power:
        size /= power
        zero += 1
    return f"{round(size, 2)} {units[zero]}"


def virustotal(update, context):
    if not VIRUSTOTAL_API: return LOGGER.error("VIRUSTOTAL_API not provided.")
    message = update.effective_message
    VtPath = os.path.join("Virustotal", str(message.from_user.id))
    if not os.path.exists("Virustotal"): os.makedirs("Virustotal")
    if not os.path.exists(VtPath): os.makedirs(VtPath)
    help_msg = "<b>Reply to message including file:</b>"
    help_msg += f"\n<code>/{BotCommands.VirusTotalCommand}" + " {message}" + "</code>"
    help_msg += "\n<b>By replying to message (including hash):</b>"
    help_msg += f"\n<code>/{BotCommands.VirusTotalCommand}" + " {message}" + "</code>"
    sent = sendMessage('Running VirusTotal Scan. Wait for finish.', context.bot, update)
    link = None
    if message.reply_to_message:
        if message.reply_to_message.document: # file
            maxsize = 210*1024*1024
            if VIRUSTOTAL_FREE: maxsize = 32*1024*1024
            if message.reply_to_message.document.file_size > maxsize:
                return editMessage(f"File limit is {humanbytes(maxsize)}", sent)
            try:
                editMessage(f"Trying to download. Please wait.", sent)
                filename = os.path.join(VtPath, message.reply_to_message.document.file_name)
                link = app.download_media(message=message.reply_to_message.document, file_name=filename)
            except Exception as e: LOGGER.error(e)
        else: link = message.reply_to_message.text
    else:
        link = message.text.split(' ', 1)
        if len(link) != 2: link = None
        else: link = link[1]
    if not link:
        editMessage("Some error exceed. Please try again later.", sent)
        try: os.remove(link)
        except: pass
    ret = getResultAsReadable(get_result(link))
    return editMessage(ret, sent)


virustotal_handler = CommandHandler(BotCommands.VirusTotalCommand, virustotal,
    filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(virustotal_handler)
