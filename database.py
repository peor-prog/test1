import aiosqlite

DB_NAME = "cafe.db"


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """
        )
        await db.commit()


async def add_product(name: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO products (name) VALUES (?)", (name,))
        await db.commit()


async def get_all_products():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT name FROM products") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]