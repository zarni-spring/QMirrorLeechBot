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
    elif "v.gd" in SHORTENER:
        try:
            url = quote(longurl)
            response = rget(f"https://v.gd/create.php?format=json&url={url}&logstats=1")
            if response.ok:
                if 'shorturl' in response.json(): return response.json()['shorturl']
            else:
                LOGGER.error("response was not ok")
                return longurl
        except Exception as e:
            LOGGER.error(e)
            return longurl
    elif "da.gd" in SHORTENER:
        try: return pyShortener().dagd.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            return longurl
    elif "is.gd" in SHORTENER:
        try: return pyShortener().isgd.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            return longurl
    elif "ttm.sh" in SHORTENER:
        try: return pyShortener(domain='ttm.sh').nullpointer.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            return longurl
    elif "clck.ru" in SHORTENER:
        try: return pyShortener().clckru.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            return longurl
    elif "chilp.it" in SHORTENER:
        try: return pyShortener().chilpit.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            return longurl
    elif "osdb" in SHORTENER:
        try: return pyShortener().osdb.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            return longurl
    elif "owly" in SHORTENER:
        try: return pyShortener().owly.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            return longurl
    
    # requires shortener api

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
    elif "pubiza" in SHORTENER:
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
    elif "bit.ly" in SHORTENER:
        try:
            s = pyShortener(api_key=SHORTENER_API)
            link = s.bitly.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            link = longurl
    elif "post" in SHORTENER:
        try:
            s = pyShortener(api_key=SHORTENER_API)
            link = s.post.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            link = longurl
    elif "cutt.ly" in SHORTENER:
        try:
            s = pyShortener(api_key=SHORTENER_API)
            link = s.cuttly.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            link = longurl
    elif "adf.ly" in SHORTENER:
        try:
            key, uid = SHORTENER_API.split(' ')
            s = pyShortener(api_key=key,user_id=uid)
            link = s.adfly.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            link = longurl
    elif "shortcm" in SHORTENER:
        try:
            api_key, domain = SHORTENER_API.split(' ')
            s = pyShortener(api_key=api_key, domain=domain)
            link = s.shortcm.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            link = longurl
    elif "tinycc" in SHORTENER:
        try:
            api_key, login = SHORTENER_API.split(' ')
            s = pyShortener(api_key=api_key, login=login)
            link = s.tinycc.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            link = longurl
    elif "tinyurl" in SHORTENER:
        try:
            link = pyShortener().tinyurl.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            link = longurl
    elif "ouo.io" in SHORTENER:
        disable_warnings()
        try: link = rget(f'http://ouo.io/api/{SHORTENER_API}?s={longurl}', verify=False).text
        except Exception as e:
            LOGGER.error(e)
            link = longurl
    else:
        try: link = rget(f'https://{SHORTENER}/api?api={SHORTENER_API}&url={longurl}&format=text').text
        except Exception as e:
            LOGGER.error(e)
            link = longurl
    if len(link) == 0:
        LOGGER.error("Something is Wrong with the url shortener")
        return longurl
    return link
