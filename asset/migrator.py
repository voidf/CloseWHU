"""本文件为离线代码"""
import pickle
from dataclasses import dataclass
import datetime
from io import BytesIO
import os, sys
import shutil
import traceback
from loguru import logger
from mongoengine import connect, disconnect
cur = sys.path[0]
parent = cur[:cur.rfind('\\')]
os.chdir(parent)
sys.path.append(parent)
print(sys.path)

with open('asset/狮子山数学选课指南.htm', 'r') as f:
    htmldata = f.read()

from bs4 import BeautifulSoup

B = BeautifulSoup(htmldata, 'html.parser')
headers = B('h1')
math1 = headers[1]
math2 = headers[2]
P3 = headers[3]

h3 = math1('h3')
content = []

from pydantic import BaseModel
from typing import *
class BSNode(BaseModel):
    pr: int
    c: str
    son: List['BSNode'] = []


M = {
    'h1': 1,
    'h2': 2,
    'h3': 3,
    'p': 5
}

class QNode(BaseModel):
    t: str
    s: List[str] = []

qnodes = []

stack: List[BSNode] = [BSNode(pr=1, son=[], c=math1.get_text())]
def scan(L, R):
    for i in L.next_siblings:
        if i != R:
            if i != '\n':
                content.append(i)
                cpr = M[i.name]
                while stack[-1].pr >= cpr:
                    stack.pop()
                cnode = BSNode(pr=cpr, c=i.get_text().replace('\xa0', ''), son=[])
                stack[-1].son.append(cnode)
                stack.append(cnode)
        else:
            break

def dfs(x: BSNode):
    if x.pr<3:
        for i in x.son:
            dfs(i)
    elif x.pr==3:
        q = QNode(t=x.c)
        for i in x.son:
            if i.c != '\xa0' and i.c:
                q.s.append(i.c)
        qnodes.append(q)

scan(math1, math2)


dfs(stack[0])

scan(math2, P3)

dfs(stack[0])
print(content)
print(qnodes)


# changed to parent path

from model.post import Contrib

mp = {
    '任课老师': 'teacher',
    '任课教师': 'teacher',
    '你的体验': 'comment',
    '学分数量': 'score',
    '给分情况': 'scoring',
    '推荐教材': 'material',
    '补充说明': 'appendix',
    '考核方式': 'examination',
    '课程内容': 'intro',
    '课程性质': 'type',
}
contribs = []
for i in qnodes:
    if i.t.find('.') == 1:
        i.t = i.t[2:].strip()
    
    if i.t.startswith('课程完整名称：'):
        i.t = i.t[7:]
    parsed = Contrib(course=i.t, content={})
    filled = set()
    for x in i.s:
        try:
            key, txt = x.split('：')
            txt = txt.strip()
            rk = mp[key]
            if rk in filled:
                contribs.append(parsed)
                filled.clear()
                parsed = Contrib(course=i.t, content={})
            filled.add(rk)
            if rk == 'teacher':
                setattr(parsed, 'teacher', txt)
            
            elif rk == 'score':
                setattr(parsed.content, rk, float(txt))
            elif rk == 'material':
                setattr(parsed.content, rk, [txt])
            else:
                setattr(parsed.content, rk, txt)
                
        except:
            continue
    if filled:
        contribs.append(parsed)
print(len(contribs))
for p, i in enumerate(contribs):
    print(p)
    i.save()


