from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy

from sqlalchemy.future import select

from typing import List

from database import Base, session

import logging
logging.basicConfig(level=logging.INFO)



class Recipe(Base):
    __tablename__ = 'recipes'
    id = mapped_column(Integer, primary_key=True, index=True)
    name = mapped_column(String, index=True)
    time_spent = mapped_column(String) # время будет в объяснении сколько
    description = mapped_column(String)
    watched_count = mapped_column(Integer)
    
    p_r_assotiation: Mapped[List["ProductRecipe"]]  = relationship(lazy="selectin")
    
    products: AssociationProxy[List["Product"]] = association_proxy(
        "p_r_assotiation",
        "products",
        creator=lambda productsobj: ProductRecipe(products=productsobj))
    
    
    def __init__(self, name, time_spent, description, watched_count=0, products=None):
        self.name = name
        self.time_spent = time_spent
        self.description = description
        self.watched_count = watched_count
        if not products:
            return        
        self.products.extend([Product(**p) for p in products])
        
    
    async def re_create(self):
        """
        Функция пред-обработчик массива продуктов на запись в б.д.
        Во избежание конфликта уникальности названия продукта.
         
        Если в таблице продуктов уже есть какие-то претенденты - удалить тёзок из добавляемых,
        добавив, однако, объекты с такими же значениями в названии из уже имеющихся.
        """        
        if not self.products:
            return
        # Получение списка объектов уже имеющихся продуктов.
        set_name = set(p.name.strip() for p in self.products)
        res = await session.execute((select(Product).filter(Product.name.in_(set_name))))
        existing = res.scalars().all()
        
        # добавление уже имеющихся продуктов в таблице в список на добавление, для увязки с данным рецептом в таблице пар.
        self.products.clear()
        self.products.extend(existing)
        
        # Добавление новых продуктов в список.
        existing_name = set(p.name for p in existing)
        set_name = set_name - existing_name
        self.products.extend([Product(name=name) for name in set_name])
        
    

class Product(Base):
    __tablename__ = 'products'
    id = mapped_column(Integer, primary_key=True, index=True)
    name = mapped_column(String, index=True, unique=True)
    
    def __init__(self, name):
        self.name = name
    

class ProductRecipe(Base):
    __tablename__ = 'products_recipes'
    recipe_id = mapped_column(Integer, ForeignKey("recipes.id"), primary_key=True)
    product_id = mapped_column(Integer, ForeignKey("products.id"), primary_key=True)    
    
    recipes: Mapped["Recipe"] = relationship(back_populates="p_r_assotiation", lazy="selectin")
    products: Mapped["Product"] = relationship(lazy="selectin")
