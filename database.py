import aiosqlite
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "bot.db")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                situaciya TEXT,
                popytki TEXT,
                vopros TEXT,
                tema TEXT,
                is_subscriber INTEGER DEFAULT 0,
                status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                reviews_total INTEGER DEFAULT 3,
                reviews_used INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                file_id TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def upsert_user(user_id: int, username: str, first_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username=excluded.username,
                first_name=excluded.first_name
        """, (user_id, username or "", first_name or ""))
        await db.commit()

async def get_active_subscription(user_id: int):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT id, user_id, start_date, end_date, reviews_total, reviews_used, is_active
            FROM subscriptions
            WHERE user_id = ? AND is_active = 1 AND end_date > ?
            ORDER BY id DESC LIMIT 1
        """, (user_id, now)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "user_id": row[1],
                    "start_date": row[2],
                    "end_date": row[3],
                    "reviews_total": row[4],
                    "reviews_used": row[5],
                    "is_active": row[6]
                }
            return None

async def add_subscription(user_id: int, days: int = 30, reviews: int = 3):
    now = datetime.utcnow()
    end_date = now + timedelta(days=days)
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    end_str = end_date.strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        # Deactivate old subscriptions if any
        await db.execute("UPDATE subscriptions SET is_active = 0 WHERE user_id = ?", (user_id,))
        await db.execute("""
            INSERT INTO subscriptions (user_id, start_date, end_date, reviews_total, reviews_used, is_active)
            VALUES (?, ?, ?, ?, 0, 1)
        """, (user_id, now_str, end_str, reviews))
        await db.commit()
    return end_date

async def use_subscription_review(user_id: int):
    sub = await get_active_subscription(user_id)
    if sub and sub["reviews_used"] < sub["reviews_total"]:
        async with aiosqlite.connect(DB_PATH) as db:
            new_used = sub["reviews_used"] + 1
            await db.execute("""
                UPDATE subscriptions SET reviews_used = ? WHERE id = ?
            """, (new_used, sub["id"]))
            await db.commit()
            return new_used, sub["reviews_total"]
    return None

async def get_last_free_submission(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT created_at FROM submissions
            WHERE user_id = ? AND is_subscriber = 0
            ORDER BY id DESC LIMIT 1
        """, (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0]
            return None

async def save_submission(user_id: int, situaciya: str, popytki: str, vopros: str, tema: str, is_subscriber: bool = False):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO submissions (user_id, situaciya, popytki, vopros, tema, is_subscriber)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, situaciya, popytki, vopros, tema, 1 if is_subscriber else 0))
        sub_id = cursor.lastrowid
        await db.commit()
        return sub_id

async def get_submission(sub_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT s.id, s.user_id, s.situaciya, s.popytki, s.vopros, s.tema, s.is_subscriber, s.status, s.created_at, u.username, u.first_name
            FROM submissions s
            LEFT JOIN users u ON s.user_id = u.user_id
            WHERE s.id = ?
        """, (sub_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "user_id": row[1],
                    "situaciya": row[2],
                    "popytki": row[3],
                    "vopros": row[4],
                    "tema": row[5],
                    "is_subscriber": bool(row[6]),
                    "status": row[7],
                    "created_at": row[8],
                    "username": row[9],
                    "first_name": row[10]
                }
            return None

async def save_payment(user_id: int, username: str, file_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO payments (user_id, username, file_id)
            VALUES (?, ?, ?)
        """, (user_id, username or "", file_id))
        pid = cursor.lastrowid
        await db.commit()
        return pid

async def get_all_subscribers():
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT s.user_id, u.username, u.first_name, s.start_date, s.end_date, s.reviews_used, s.reviews_total
            FROM subscriptions s
            LEFT JOIN users u ON s.user_id = u.user_id
            WHERE s.is_active = 1 AND s.end_date > ?
            ORDER BY s.end_date ASC
        """, (now,)) as cursor:
            rows = await cursor.fetchall()
            return [
                {
                    "user_id": r[0],
                    "username": r[1],
                    "first_name": r[2],
                    "start_date": r[3],
                    "end_date": r[4],
                    "reviews_used": r[5],
                    "reviews_total": r[6]
                }
                for r in rows
            ]

async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as c:
            users_count = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM submissions") as c:
            subs_count = (await c.fetchone())[0]
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        async with db.execute("SELECT COUNT(*) FROM subscriptions WHERE is_active=1 AND end_date > ?", (now,)) as c:
            active_subs_count = (await c.fetchone())[0]
        return {
            "users": users_count,
            "submissions": subs_count,
            "subscribers": active_subs_count
        }
