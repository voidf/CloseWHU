"""本文件为离线代码"""
import pickle
from dataclasses import dataclass
import datetime
from io import BytesIO
import os, sys
import shutil
import traceback
from loguru import logger
cur = sys.path[0]
parent = cur[:cur.rfind('\\')]
os.chdir(parent)
sys.path.append(parent)
print(sys.path)
# changed to parent path

