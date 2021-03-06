import os
import json
import pathlib
from typing import List, Dict
from vars import cron_dir
import vars as config
import pickle


def loadCookies():
    with open(str(cron_dir / 'cookies.dump'), 'rb') as f:
        cookies = pickle.load(f)  # type: Dict[str,str]
    return cookies


def get_chrome_cookies(url, profile: str = 'Default'):
    import os
    import sqlite3
    import win32crypt

    cookie_file_path = os.path.join(os.environ['LOCALAPPDATA'], r'Google\Chrome\User Data\{}\Cookies'.format(profile))
    print(cookie_file_path)
    conn = sqlite3.connect(cookie_file_path)
    ret_dict = {}
    rows = list(conn.execute("select name, encrypted_value from cookies where host_key = '{}'".format(url)))
    conn.close()
    for row in rows:
        ret = win32crypt.CryptUnprotectData(row[1], None, None, None, 0)
        ret_dict[row[0]] = ret[1].decode()
    return ret_dict


try:
    cookies = loadCookies()
except FileNotFoundError:
    import requests.cookies
    try:
        c = requests.cookies.RequestsCookieJar()
        for host in ['game.granbluefantasy.jp', '.game.granbluefantasy.jp', '.mobage.jp']:
            cookies = get_chrome_cookies(host, profile=config.profile)
            print('获取到 {} 域名下的cookies {} 条'.format(host, len(cookies)))
            for key, value in cookies.items():
                c.set(key, value, domain=host)
                # c.append({'key': key, 'value': value, 'host': host})
        with open(str(cron_dir / 'cookies.dump'), 'wb+') as f:
            pickle.dump(c, f)
        print('获取cookies成功')
        cookies = c
    except ImportError:
        raise Exception('无法获取cookies, 请检查cookies.dump文件是否存在.')
