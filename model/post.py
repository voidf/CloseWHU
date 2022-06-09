from model.mixin.asyncable import Asyncable
from mongoengine import *
from mongoengine.document import Document
from mongoengine.fields import *
from utility.password import encrypt
from mongoengine.queryset import *
from mongoengine.document import *
from pymongo import ReturnDocument
from model.mixin.asyncable import result2bool

class Content(EmbeddedDocument):
    """具体的评价内容"""
    comment = StringField(verbose_name='你的体验')
    score = FloatField(verbose_name='学分数量')
    scoring = StringField(verbose_name='给分情况')
    material = ListField(StringField(), verbose_name='推荐教材')
    appendix = StringField(verbose_name='补充说明')
    examination = StringField(verbose_name='考核方式')
    intro = StringField(verbose_name='课程内容')
    type = StringField(verbose_name='课程性质')

class Topic(Asyncable):
    @classmethod
    async def atrychk(cls, course, teacher, *args, **kwargs):
        """尝试找一个课"""
        return cls._nullable(await cls._aget_collection().find_one({'course': course, 'teacher': teacher}, *args, **kwargs), created=False)

    @classmethod
    async def achk(cls, course, teacher, *args, **kwargs):
        """尝试找一个课，不存在则塞入一个课"""
        default_document = cls().to_mongo()
        res = await cls._aget_collection().find_one_and_update(
            {'course': course, 'teacher': teacher},
            {'$setOnInsert': default_document},
            *args,
            upsert=True,
            return_document=ReturnDocument.AFTER,
            **kwargs
        )

        return cls._to_mongoengine(res, created=False)

    @classmethod
    async def aunchk(cls, course, teacher, *args, **kwargs):
        """根据主键删一个文档"""
        return result2bool(await cls._aget_collection().delete_one({'course': course, 'teacher': teacher}, *args, **kwargs))

class Contrib(Document, Asyncable):
    """用户投稿，只是collection不同"""
    course = StringField(required=True, verbose_name='课程完整名称')
    teacher = StringField(required=True, unique_with='course', verbose_name='任课教师')
    content = EmbeddedDocumentField(Content) # 注意不是list


class Post(Document, Topic):
    """管理员批准展示的一条教师-课程容器"""
    course = StringField(required=True, verbose_name='课程完整名称')
    teacher = StringField(required=True, unique_with='course', verbose_name='任课教师')
    content = EmbeddedDocumentListField(Content)
    