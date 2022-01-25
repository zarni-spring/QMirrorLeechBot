# Implemented by https://github.com/junedkh

import random

from pyshorteners import Shortener as pyShortener
from requests import get as rget
from base64 import b64encode
from urllib.parse import quote
from urllib3 import disable_warnings

from bot import LOGGER, SHORTENER, SHORTENER_API


def short_url(longurl):
    if not SHORTENER: return longurl
    if ("is.gd" in SHORTENER) or ("v.gd" in SHORTENER):
        # url = quote(b64encode(longurl.encode("utf-8")))
        url = rget(f"https://{SHORTENER}/create.php?format=json&url={longurl}&logstats=1").json()
        LOGGER.info(url)
        if 'shorturl' in url: return url['shorturl']
        else: return longurl
    elif "git.io" in SHORTENER:
        try: link = pyShortener.gitio.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            link = longurl
    elif "da.gd" in SHORTENER:
        try: link = pyShortener.dagd.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            link = longurl
    if not SHORTENER_API: return longurl
    elif "shorte.st" in SHORTENER:
        disable_warnings()
        link = rget(f'http://api.shorte.st/stxt/{SHORTENER_API}/{longurl}', verify=False).text
    elif "bc.vc" in SHORTENER: # sample SHORTENER_API 2dgdg5f1fgag7cg6f0622&uid=45634
        url = quote(b64encode(longurl.encode("utf-8")))
        try:
            link = rget(f"https://bc.vc/api.php?key={SHORTENER_API}&url={url}", verify=False).text
        except Exception as e:
            LOGGER.error(e)
            link = longurl
    elif ("pubiza" in SHORTENER) or ("lnkload" in SHORTENER) or ("link.tl" in SHORTENER):
        # sample SHORTENER_API "hsdfgCgdgrsdfgsfgfgsdgLsfgXef mainstream"
        try:
            url = quote(b64encode(longurl.encode("utf-8")))
            key, tip = SHORTENER_API.split(' ')
            link = rget(f"http://pubiza.com/api.php?token={key}&url={url}&ads_type={tip}", verify=False).text
        except Exception as e:
            LOGGER.error(e)
            link = longurl
    elif "linkvertise" in SHORTENER:
        url = quote(b64encode(longurl.encode("utf-8")))
        linkvertise = [
            f"https://link-to.net/{SHORTENER_API}/{random.random() * 1000}/dynamic?r={url}",
            f"https://up-to-down.net/{SHORTENER_API}/{random.random() * 1000}/dynamic?r={url}",
            f"https://direct-link.net/{SHORTENER_API}/{random.random() * 1000}/dynamic?r={url}",
            f"https://file-link.net/{SHORTENER_API}/{random.random() * 1000}/dynamic?r={url}"]
        link = random.choice(linkvertise)
    elif "bitly.com" in SHORTENER:
        s = pyShortener(api_key=SHORTENER_API)
        link = s.bitly.short(longurl)
    elif "ouo.io" in SHORTENER:
        disable_warnings()
        link = rget(f'http://ouo.io/api/{SHORTENER_API}?s={longurl}', verify=False).text
    else:
        link = rget(f'https://{SHORTENER}/api?api={SHORTENER_API}&url={longurl}&format=text').text
    if len(link) == 0:
        LOGGER.error("Something is Wrong with the url shortener")
        return longurl
    return link
