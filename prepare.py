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
from getopt import getopt
from lang import lan, getlan, getdict
from JSONParser import loadset
import sys
from typing import List
from os.path import exists
from os import listdir, remove, system
from requests import Session
from file import mkdir
from platform import system as systemname
from re import search

la = None
se = loadset()
if se == -1 or se == -2:
    se = {}
la = getdict('command', getlan(se, {}))


def ph():
    h = f'''{la['O1']}
    prepare.py [-h/-?/--help]   {la['O2']}
    prepare.py [--lan <LANGUAGECODE>] [-u] [filelist]
    --lan <LANGUAGECODE>    {la['O55']}
    -u      {la['O73']}
    filelist    {la['O74']}'''
    print(h)


def gopt(args: List[str]):
    re = getopt(args, 'h?u', ['help', 'lan='])
    rr = re[0]
    r = {}
    h = False
    for i in rr:
        if i[0] == '-h' or i[0] == '-?' or i[0] == '--help':
            h = True
        if i[0] == '--lan' and not 'lan' in r and (i[1] == 'null' or i[1] in lan):
            r['lan'] = i[1]
        if i[0] == '-u':
            r['u'] = True
    if h:
        global la
        la = getdict('command', getlan(se, r))
        ph()
        exit()
    return r, re[1]


class main:
    _r: Session = None
    _upa: bool = False

    def __init__(self, ip: dict, fl: List[str]):
        if 'u' in ip:
            self._upa = True
        if not exists('webuihtml/js(origin)/'):
            raise FileNotFoundError('webuihtml/js(origin)/')
        if len(fl) == 0:
            fl = listdir('webuihtml/js(origin)/')
        self._r = Session()
        tag = self._get_jquery_tag()
        if not exists('webuihtml/jso/'):
            mkdir('webuihtml/jso/')
        self._check('webuihtml/jso/jquery.js',
                    f"https://code.jquery.com/jquery-{tag}.min.js")
        self._check('webuihtml/jso/qrcode.min.js',
                    "https://github.com/davidshimjs/qrcodejs/raw/master/qrcode.min.js")
        self._check('webuihtml/jso/sha256.min.js',
                    "https://github.com/emn178/js-sha256/raw/master/build/sha256.min.js")
        if not self._check_java():
            raise FileNotFoundError('Can not find java.')
        tag = self._get_compiler_tag()
        self._check(
            'compiler.jar', f"https://repo1.maven.org/maven2/com/google/javascript/closure-compiler/{tag}/closure-compiler-{tag}.jar")
        self._check_with_com('webuihtml/jso/base64.min.js',
                             "https://raw.githubusercontent.com/dankogai/js-base64/master/base64.js")
        for fn in fl:
            fn2 = f'webuihtml/js(origin)/{fn}'
            if not exists(fn2):
                raise FileNotFoundError(fn2)
            self._com_javascript(fn)

    def _check(self, fn: str, uri: str):
        if exists(fn) and self._upa:
            remove(fn)
        if not exists(fn):
            self._get_file(uri, fn)

    def _check_with_com(self, fn: str, uri: str):
        if exists(fn) and self._upa:
            remove(fn)
        if not exists(fn):
            fn2 = f"{fn}.tmp"
            self._get_file(uri, fn2)
            if system(f'java -jar compiler.jar --js "{fn2}" --js_output_file "{fn}"') != 0:
                raise Exception('Error in compiler.')
            remove(fn2)

    def _get_jquery_tag(self) -> str:
        re = self._r.get('https://api.github.com/repos/jquery/jquery/tags')
        re = re.json()
        return re[0]['name']

    def _get_compiler_tag(self) -> str:
        re = self._r.head(
            'https://mvnrepository.com/artifact/com.google.javascript/closure-compiler/latest')
        uri = re.headers['Location']
        rs = search(
            r'^https://mvnrepository\.com/artifact/com\.google\.javascript/closure-compiler/(.+)', uri)
        return rs.groups()[0]

    def _get_file(self, uri: str, fn: str):
        re = self._r.get(uri, stream=True)
        with open(fn, 'ab') as f:
            for c in re.iter_content(1024):
                if c:
                    f.write(c)

    def _check_java(self) -> bool:
        sn = systemname()
        s = " 2>&0 1>&0"
        if sn == "Linux":
            s = " > /dev/null 2>&1"
        if system(f"java -h{s}") == 0:
            return True
        return False

    def _com_javascript(self, fn: str):
        print(fn)
        if system(f'java -jar compiler.jar --js "webuihtml/js(origin)/{fn}" --js_output_file "webuihtml/js/{fn}"') != 0:
            raise Exception('Error in compiler.')


if __name__ == "__main__":
    if len(sys.argv) == 1:
        ph()
    else:
        ip, fl = gopt(sys.argv[1:])
        main(ip, fl)