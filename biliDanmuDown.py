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
def downloadn(cid,r) :
    "下载当前弹幕"
    try :
        re=r.get('https://comment.bilibili.com/'+str(cid)+".xml")
    except :
        return -1
    re.encoding='utf8'
    return re.text
def downloadh(cid,r,date) :
    "下载历史弹幕"
    try :
        re=r.get('https://api.bilibili.com/x/v2/dm/history?type=1&date=%s&oid=%s' % (date,cid))
    except :
        return -1
    re.encoding='utf8'
    return re.text