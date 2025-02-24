import sqlite3

txt = """-- Рецепты
CREATE TABLE IF NOT EXISTS recipes (
id integer PRIMARY KEY,
name text NOT NULL,
time_spent text,
description text,
watched_count integer
);

-- Продукты
CREATE TABLE IF NOT EXISTS products (
id integer PRIMARY KEY,
name text UNIQUE NOT NULL
);

-- Парасочетания предыдущих двух
CREATE TABLE IF NOT EXISTS products_recipes (
recipe_id integer NOT NULL,
product_id integer NOT NULL,
FOREIGN KEY (recipe_id) REFERENCES recipes(id),
FOREIGN KEY (product_id) REFERENCES products(id),
PRIMARY KEY(recipe_id, product_id)
);"""

with sqlite3.connect("recipes.db") as conn:
    cursor = conn.cursor()
    cursor.executescript(txt)
    conn.commit()
