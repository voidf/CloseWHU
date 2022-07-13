"""这份代码是离线代码，用于处理初版问卷星导出，用前需要用excel将其另存为csv

说一下问卷设计存在的问题：
    1. 单表单多数据，不好做映射，增大数据处理编码难度，降低编码人员心情
    2. 考核方式、学分数量没收集
    3. 给分情况预期是随意填写的字符串内容，而不是1~5分这样的枚举
    4. 总体评分是什么时候多加的字段(0x0)
    5. 教学情况不明确，应该写到【你的体验】还是【课程内容】？总之这两个中的一个没收集（目前打算写到你的体验中去）
    6. 最好明确标记一下哪些数据是供展示的，尽量减少收集不必要的字段

"""

import asyncio
import csv
from model.post import Content, Post

headers = ['4、课程名称', '5、任课教师', '6、课程类型', '8、总体评价', '9、给分情况', '10、教学情况（如：讲课质量、任务数量）', '11、其他想补充的', '12、是否还要继续填写']

startoffset = 9

colctr = [9, 10, 11, 13, 14, 15, 16, 17]


new_mapping = []

empty_token = '(空)'
skip_token = '(跳过)'
no_continue='否（跳转后可直接提交）'


li = []

def rating_mapping(x: str):
    return {
        '五': 5,
        '四': 4,
        '三': 3,
        '二': 2,
        '一': 1,
    }[x[0]]

injection = {
    0: 'course',
    1: 'teacher',
    2: 'type',
        # 跨院
    4: 'rating',
    5: 'scoring',
    6: 'comment',
    7: 'appendix',
}


emptyP = Post()
emptyP.content = Content()
first = True

with open('B.CSV', 'r', newline='\n', encoding='utf-8') as f:
    rd = csv.reader(f)
    p = Post()
    p.content = Content()

    assert p.to_mongo() == emptyP.to_mongo()
    
    for i in rd:
        if first:
            first = False
            continue

        for idx, cont in enumerate(i):
            if cont in (empty_token, skip_token):
                i[idx] = ''
        if i[9]: p.course = i[9]
        if i[10]: p.teacher = i[10]

        if i[11]: p.content.type = i[11]
        if i[13]: p.content.rating = rating_mapping(i[13])
        if i[14]: p.content.scoring = i[14]
        if i[15]: p.content.comment = i[15]
        if i[16]: p.content.appendix = i[16]
        li.append(p)

        p = Post()
        p.content = Content()
        
        if i[17] != no_continue:
            offset = 18
            while offset+7 < len(i):
                if i[offset+0]: p.course = i[offset+0]
                if i[offset+1]: p.teacher = i[offset+1]

                if i[offset+2]: p.content.type = i[offset+2]
                if i[offset+4]: p.content.rating = rating_mapping(i[offset+4])
                if i[offset+5]: p.content.scoring = i[offset+5]
                if i[offset+6]: p.content.comment = i[offset+6]
                if i[offset+7]: p.content.appendix = i[offset+7]
                if p.to_mongo() != emptyP.to_mongo():
                    li.append(p)
                    p = Post()
                    p.content = Content()
                offset += 8
print(li)

        # print(*[i[x] for x in colctr])
async def upload(p: Post):
    real: Post = await Post.achk(p.course, p.teacher)
    real.content.append(p.content)
    print(await real.asave())


async def main():
    await asyncio.gather(*[upload(x) for x in li])

asyncio.run(main())