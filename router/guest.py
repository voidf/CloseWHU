from fastapi import HTTPException
from typing import List
from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import BaseModel
from config import secret
from model.post import Contrib, Post
from utility.motor import L
from pymongo import ReturnDocument

guest_router = APIRouter(
    tags=["Guest | 公开接口"]
)

from .admin import CourseModel, ContentModel



@guest_router.get('/post')
async def find_course(course: str=None, teacher: str=None):
    if course and teacher:
        p = (await Post.atrychk(course, teacher))
        if not p: raise HTTPException(404)
        return p.to_mongo()
    elif course:
        return [i.to_mongo() for i in
            (await Post.afind({'course': course}))
        ]
    elif teacher:
        return [i.to_mongo() for i in
            (await Post.afind({'teacher': teacher}))
        ]
    else:
        res = await Post.aaggregate_list([{
            '$project':{
                'teacher':1, 'course':1, '_id': 0, 'cnt': {'$size': '$content'}
            }
        }])
        # logger.debug(res)
        return res
        # logger.debug(await Post.afind(projection={'teacher':1, 'course':1}))
        # logger.debug([i.to_mongo() for i in
        #     (await Post.afind(projection={'teacher':1, 'course':1}))
        # ])
        # return [i.to_mongo() for i in
        #     (await Post.afind(projection={'teacher':1, 'course':1}))
        # ]

@guest_router.get('/post/{idx}')
async def find_course(course: str, teacher: str, idx: int):
    p = (await Post.atrychk(course, teacher))
    if not p: raise HTTPException(404)
    return p.content[idx].to_mongo()

@guest_router.post('/contrib')
async def new_contrib(c: CourseModel, m: ContentModel):
    return (await Contrib._aget_collection().find_one_and_update(
        {'course': c.course, 'teacher': c.teacher},
        {
            '$set':{'content': m.dict(exclude_unset=True)},
        },
        upsert=True,
        return_document=ReturnDocument.AFTER,
    ))


