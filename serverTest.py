# from typing import Union
# from fastapi import FastAPI
# from pydantic import BaseModel
#
# app = FastAPI()
#
# '''
# uvicorn server:app --reload를 사용하여 기동
# * --reload옵션을 주면 py파일 수정시 자동으로 서버가 소스 변경을 인식하여 리로딩함.
# '''
#
#
# # Pydantic을 이용해 파이썬 표준 타입으로 본문을 선언.
# class Item(BaseModel):
#     name: str
#     price: float
#     is_offer: Union[bool, None] = None
#
#
# @app.get("/")
# def read_root():
#     return {"Hello": "World"}
#
#
# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}
#
#
# '''
# Item 객체는 request body에
# {
#   "name": "Name of Item",
#   "price": 0,
#   "is_offer": true
# }
# 형식으로 적어주어야 함.
# '''
#
#
# @app.put("/items/{item_id}")
# def update_item(item_id: int, item: Item):
#     return {"item_name": item.name, "item_id": item_id}
