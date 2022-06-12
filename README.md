# 如何跑通

## 0.依赖

python3.9+

你可以去白嫖500M Mongodb提供的云数据库，当然也可以本地装一个

[白嫖传送门](https://account.mongodb.com/)

[自启传送门](https://www.mongodb.com/try/download/community)

## 1.写配置

修改`secret.template.yml`为`secret.yml`，参见注释配置好

## 2.装依赖包

```pip3 install -U -r requirements.txt```

## 3.开冲

懒人版：

```python3 api.py```

或者高级一点：

```uvicorn api:app --port=11451 --workers=4 --host=0.0.0.0```