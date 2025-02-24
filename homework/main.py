from typing import List

from fastapi import FastAPI
from sqlalchemy.future import select
from sqlalchemy import desc

import models
import schemas
from database import engine, session

from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("---===< DB and its ORM try to init...>===---")
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield
    logging.info("---===< DB and its ORM try to tear down...>===---")
    await session.close()
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.post("/recipes/", response_model=schemas.RecipeOut)
async def recipes(recipe_schema: schemas.RecipeIn) -> models.Recipe:
    """
    <h1>Внесение нового рецепта в БД.</h1>
    """
    r_d = recipe_schema.model_dump(exclude_unset=True)
    new_recipe = models.Recipe(**r_d)

    async with session.begin():
        await new_recipe.re_create()
        session.add(new_recipe)

    return new_recipe


@app.get("/recipes/", response_model=List[schemas.RecipeOutSimple])
async def recipes() -> List[models.Recipe]:
    """
    <h1>Получение списка всех рецептов.</h1>
    """
    res = await session.execute(
        select(models.Recipe).order_by(
            desc(models.Recipe.watched_count), models.Recipe.name
        )
    )
    objs = res.scalars().all()
    return objs


@app.get("/recipes{recipe_id}/", response_model=schemas.RecipeOut)
async def recipes(recipe_id: int = 1) -> models.Recipe:
    """
    <h1>Получение детальной информации приготовления по id.</h1>
    """
    res = await session.execute(
        select(models.Recipe)
        .join(models.ProductRecipe)
        .join(models.Product)
        .where(models.Recipe.id == recipe_id)
    )
    recipe = res.scalar()
    recipe.watched_count += 1
    await session.commit()
    return recipe
