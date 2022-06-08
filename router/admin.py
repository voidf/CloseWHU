from http.client import HTTPException
from fastapi import APIRouter
from loguru import logger
from pydantic import BaseModel
from config import secret
from model.post import Post
from utility.motor import L


class KeyModel(BaseModel):
    key: str

async def require_admin_key(k: KeyModel):
    if k.key != secret.admin_key:
        raise HTTPException(401, 'invalid admin key')

admin_router = APIRouter(
    prefix="/admin",
    tags=["Admin | 管理"],
    dependencies=[]
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
    return [i.to_mongo() for i in (await L(Post.objects))]
