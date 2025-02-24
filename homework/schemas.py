from pydantic import BaseModel, ConfigDict, Field

from typing import List


class BaseProduct(BaseModel):
    
    name: str

class ProductIn(BaseProduct):
    ...
    
class ProductOut(BaseProduct):
    id: int
    model_config = ConfigDict(from_attributes=True)



class BaseRecipe(BaseModel):    
    name: str
    time_spent: str
    description: str
    products: List[ProductIn]
    
class RecipeIn(BaseRecipe):
    ...
    
class RecipeOut(BaseRecipe):
    id: int
    watched_count: int
    products: List[ProductOut]
    model_config = ConfigDict(from_attributes=True)
    
class RecipeOutSimple(BaseModel):
    id: int
    name: str
    watched_count: int
    time_spent: str
    model_config = ConfigDict(from_attributes=True)
    
