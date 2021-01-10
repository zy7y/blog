#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
@project: blog(FastAPI)
@file: category.py
@author: zy7y
@time: 2021/1/10
@site: https://cnblogs.com/zy7y
@github: https://github.com/zy7y
@gitee: https://gitee.com/zy7y
@desc:
分类表
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session

import schemas.category
from core import deps
import db as models

router = APIRouter()


@router.post("/category", summary="新增分类", response_model=schemas.category.Category)
def category_add(
        category: schemas.category.CategoryCreate,
        db: Session = Depends(deps.get_db),
        user_token: models.User = Depends(deps.get_current_user)
):
    # 获取当前用户登录的id
    user_id = user_token.id
    result = db.query(models.Category).filter(
        and_(models.Category.name == category.name, models.Category.user_id == user_id)
    ).first()

    if result:
        raise HTTPException(status_code=404, detail="分类名称已存在")
    category_obj = models.Category(
        name=category.name,
        user_id=user_id
    )
    db.add(category_obj)
    db.commit()
    db.refresh(category_obj)
    return category_obj


@router.get("/category", summary="获取分类列表", response_model=List[schemas.category.Category])
def category_list(
        db: Session = Depends(deps.get_db),
        user_token: models.User = Depends(deps.get_current_user)
):
    return db.query(models.Category).filter(models.Category.user_id == user_token.id).all()


@router.get("/plant/category", summary="平台分类列表", response_model=List[schemas.category.PlantCategory])
def plant_category(
        db: Session = Depends(deps.get_db),
        super_token: models.User = Depends(deps.get_current_superuser)
):
    return db.query(models.Category).all()


@router.put("/category/{category_id}", summary="修改分类", response_model=schemas.category.Category)
def update_category(
        category_id: int,
        category: schemas.category.CategoryCreate,
        db: Session = Depends(deps.get_db),
        user_token: models.User = Depends(deps.get_current_user)
):
    if not db.query(models.Category).get(category_id):
        raise HTTPException(status_code=404, detail="分类不存在")
    category_up = db.query(models.Category).filter(
        and_(models.Category.id == category_id, models.Category.user_id == user_token.id)
    )
    if category_up.update({"name": category.name}):
        db.commit()
        category = category_up.first()
        return category
    raise HTTPException(status_code=404, detail="不能修改其他用户的分类数据.")


@router.delete("/category/{category_id}", summary="删除分类")
def delete_category(
        category_id: int,
        db: Session = Depends(deps.get_db),
        user_token: models.User = Depends(deps.get_current_user)
):
    result = db.query(models.Category).get(category_id)
    if result:
        db.delete(result)
        db.commit()
        return {"detail": "删除成功!"}
    raise HTTPException(status_code=404, detail="分类不存在.")