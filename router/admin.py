from fastapi import HTTPException
from typing import List
from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import BaseModel
from config import secret
from model.post import Contrib, Post
from utility.motor import L


# class KeyModel(BaseModel):
#     key: str


async def require_admin_key(k: str):
    if k != secret.admin_key:
        raise HTTPException(401, 'invalid admin key')

admin_router = APIRouter(
    prefix="/admin",
    tags=["Admin | 管理"],
    dependencies=[Depends(require_admin_key)]
)


class CourseModel(BaseModel):
    course: str
    teacher: str


@admin_router.post('/post')
async def add_individual_course(c: CourseModel):
    logger.debug((await Post.achk(c.course, c.teacher)).to_mongo())
    return (await Post.achk(c.course, c.teacher)).to_mongo()


@admin_router.delete('/post')
async def remove_individual_course(c: CourseModel):
    return bool(await Post.aunchk(c.course, c.teacher))


@admin_router.get('/post')
async def get_course_list():
    return [i.to_mongo() for i in (await Post.afind())]


class ContentModel(BaseModel):
    comment: str = None
    score: float = None
    scoring: str = None
    material: List[str] = None
    appendix: str = None
    examination: str = None
    intro: str = None
    type: str = None

from pymongo import ReturnDocument

@admin_router.put('/post')
async def modify_individual_course(c: CourseModel, son: List[ContentModel]):
    logger.debug(son)
    logger.debug(type(son))
    
    return (await Post._aget_collection().find_one_and_update(
        {'course': c.course, 'teacher': c.teacher},
        {
            '$set':{'content': [i.dict(exclude_unset=True) for i in son]},
            # '$setOnInsert': {'content': [i.dict() for i in son]}
        },
        upsert=True,
        return_document=ReturnDocument.AFTER,
    ))


@admin_router.get('/contrib')
async def get_contrib_list():
    return [i.to_mongo() for i in (await Contrib.afind())]

@admin_router.get('/contrib/first')
async def get_first_contrib():
    c = (await Contrib.afind_one())
    if not c:
        raise HTTPException(404)
    return c.to_mongo()

@admin_router.get('/contrib/{cid}')
async def get_specific_contrib(cid: str):
    c = (await Contrib.atrychk(cid))
    if not c:
        raise HTTPException(404)
    return c.to_mongo()

async def _pass_contrib(contrib: Contrib):
    if not contrib:
        raise HTTPException(404)
    p: Post = await Post.achk(contrib.course, contrib.teacher)
    p.content.append(contrib.content)
    await p.asave()
    await contrib.adestroy()
    return p.to_mongo()


@admin_router.put('/contrib/first')
async def pass_first_contrib():
    """通过第一个投稿，如果教师id和课程id不存在则会新建"""
    contrib: Contrib = await Contrib.afind_one()
    return (await _pass_contrib(contrib))

@admin_router.put('/contrib/{cid}')
async def pass_specific_contrib(cid: str):
    """通过指定id的投稿"""
    contrib: Contrib = (await Contrib.atrychk(cid))
    return (await _pass_contrib(contrib))


@admin_router.delete('/contrib/first')
async def reject_first_contrib():
    """拒掉首条投稿"""
    return bool(await Contrib.adelete_one({}))

@admin_router.delete('/contrib/{cid}')
async def reject_specific_contrib(cid: str):
    """拒掉指定id的投稿"""
    return bool(await Contrib.aunchk(cid))

async def _modify_contrib(contrib: Contrib, c: CourseModel, m: ContentModel):
    if not contrib:
        raise HTTPException(404)
    contrib.course = c.course
    contrib.teacher = c.teacher
    for k, v in m.dict(exclude_unset=True).items():
        setattr(contrib.content, k, v)
    return (await contrib.asave()).to_mongo()


@admin_router.post('/contrib/first')
async def modify_first_contrib(c: CourseModel, m: ContentModel):
    contrib: Contrib = await Contrib.afind_one()
    return (await _modify_contrib(contrib, c, m))

@admin_router.post('/contrib/{cid}')
async def modify_specific_contrib(cid: str, c: CourseModel, m: ContentModel):
    contrib: Contrib = (await Contrib.atrychk(cid))
    return (await _modify_contrib(contrib, c, m))

@admin_router.post('/contrib')
async def new_contrib(c: CourseModel, m: ContentModel):
    """新建投稿"""
    return (await Contrib._aget_collection().find_one_and_update(
        {'course': c.course, 'teacher': c.teacher},
        {
            '$set':{'content': m.dict(exclude_unset=True)},
        },
        upsert=True,
        return_document=ReturnDocument.AFTER,
    ))


