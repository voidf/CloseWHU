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

from model.post import Post

for p, i in enumerate(Post.objects):
    newl = []
    s = set()
    for x in i.content:
        hashed = str(x.to_mongo())
        if hashed not in s:
            s.add(hashed)
            newl.append(x)
    i.content = newl
    i.save()
    print(p)