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
from os.path import exists
from JSONParser import loadcookie


def logincheck() -> bool:
    if not exists('cookies.json'):
        return False
    r = new_Session(False)
    read = loadcookie(r)
    if read != 0:
        return False
    re = r.get('https://api.bilibili.com/x/web-interface/nav')
    re.encoding = 'utf8'
    obj = re.json()
    if obj['code'] == 0 and 'data' in obj and obj['data']['isLogin']:
        return True
    return False


class checklogin(apic):
    _VALID_URI = r"^checklogin$"

    def _handle(self):
        return {'code': 0, 'islogin': logincheck()}
