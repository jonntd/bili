# (C) 2019-2020 lifegpc
# This file is part of bili.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from . import apic, new_Session
import web
import hashlib
from requests import Session
import rsa
from base64 import b64encode, b64decode
from .rsa import decrypt
import traceback
from urllib.parse import quote_plus
from JSONParser import savecookie
import time


keyhash = None
pubkey = None


class loginapi(apic):
    _appkey = "bca7e84c2d947ac6"
    _salt = "60698ba2f68e01ce44738920a0ffe768"
    _r: Session = None

    def __init__(self, inp: str):
        apic.__init__(self, inp)
        self._r = new_Session(False)

    def _get_pubkey(self):
        re = self._r.post('https://passport.bilibili.com/api/oauth2/getKey', {
                          'appkey': self._appkey, 'sign': self._cal_sign("appkey=%s" % (self._appkey))})
        re = re.json()
        if re['code'] != 0:
            return {'code': -1, 'result': re}
        global keyhash, pubkey
        keyhash = re['data']['hash']
        pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(
            re['data']['key'].encode())
        return {'code': 0}

    def _captcha(self):
        "获取验证码图片"
        re = self._r.get('https://passport.bilibili.com/captcha')
        img = b64encode(re.content).decode('utf8')
        ct = re.headers['Content-type'] if 'Content-type' in re.headers else None
        cap = None
        try:
            re = self._r.post('https://bili.dev:2233/captcha',
                              json={'image': img})
            if re.status_code == 200:
                re = re.json()
                if re and re["code"] == 0:
                    cap = re['message']
        except:
            pass
        return {'code': 0, 'img': img, 'cap': cap, 'type': ct}

    def _login_with_user_pass(self):
        "使用用户名和密码登录"
        username = web.input().get('username')
        password = web.input().get('password')
        capt = web.input().get('capt')
        if username is None or password is None:
            return {'code': -1}
        try:
            username = decrypt(b64decode(username)).decode('utf8')
            password = decrypt(b64decode(password)).decode('utf8')
        except:
            return {'code': -2, 'e': traceback.format_exc()}
        if capt is None:
            pm = f"appkey={self._appkey}&password={self._encrypt(f'{keyhash}{password}')}&username={quote_plus(username)}"
        else:
            pm = f"appkey={self._appkey}&captcha={capt}&password={self._encrypt(f'{keyhash}{password}')}&username={quote_plus(username)}"
        pm2 = f"{pm}&sign={self._cal_sign(pm)}"
        re = self._r.post("https://passport.bilibili.com/api/v2/oauth2/login",
                          pm2, headers={'Content-type': "application/x-www-form-urlencoded"})
        re = re.json()
        if re['code'] == 0:
            sa = []
            for i in re['data']['cookie_info']['cookies']:
                sa.append({'name': i['name'], 'value': i['value'],
                           'domain': '.bilibili.com', 'path': '/'})
            savecookie(sa)
            return {'code': 0}
        elif re['code'] == -105:
            return {'code': -3}
        elif re['code'] == -449:
            pm = f"access_key=&actionKey=appkey&appkey={self._appkey}&build=6040500&captcha=&challenge=&channel=bili&cookies=&device=phone&mobi_app=android&password={self._encrypt(f'{keyhash}{password}')}&permission=ALL&platform=android&seccode=&subid=1&ts={int(time.time())}&username={quote_plus(username)}&validate="
            pm2 = f"{pm}&sign={self._cal_sign(pm)}"
            re = self._r.post('https://passport.bilibili.com/api/v3/oauth2/login',
                              pm2, headers={'Content-type': "application/x-www-form-urlencoded"})
            re = re.json()
            if re['code'] == 0:
                sa = []
                for i in re['data']['cookie_info']['cookies']:
                    sa.append({'name': i['name'], 'value': i['value'],
                               'domain': '.bilibili.com', 'path': '/'})
                savecookie(sa)
                return {'code': 0}
            return {'code': -4, 'result': re}
        elif re['code'] == -629:  # 用户名或密码错误
            return {'code': -6}
        else:
            return {'code': -5, 'result': re}
        return {'code': -7}

    def _cal_sign(self, p):
        sh = hashlib.md5()
        sh.update(f"{p}{self._salt}".encode())
        return sh.hexdigest()

    def _encrypt(self, s: str):
        return quote_plus(b64encode(rsa.encrypt(s.encode(), pubkey)))


class getpubkey(loginapi):
    _VALID_URI = r'^getpubkey$'

    def _handle(self):
        return self._get_pubkey()


class captcha(loginapi):
    _VALID_URI = r'captcha'

    def _handle(self):
        return self._captcha()


class login(loginapi):
    _VALID_URI = r'login'

    def _handle(self):
        t = web.input().get('type')
        if t is None:
            return {'code': -1}
        if t == "0":
            return self._login_with_user_pass()
        return {'code': -1}
