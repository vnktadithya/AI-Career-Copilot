from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import json


async def get_user_preferences(db: AsyncSession, user_id):
    query = text("""
        SELECT
            tone,
            include_emojis,
            portfolio_repo_url,
            portfolio_branch,
            auto_deploy,
            sample_posts
        FROM user_preferences
        WHERE user_id = :user_id
    """)

    result = await db.execute(query, {"user_id": user_id})
    row = result.fetchone()

    if not row:
        return None

    data = dict(row._mapping)

    # 🔥 CRITICAL FIX
    # Convert [] → {}
    if not isinstance(data.get("sample_posts"), dict):
        data["sample_posts"] = {}

    return data


async def create_user_preferences(db: AsyncSession, user_id, data: dict):
    query = text("""
        INSERT INTO user_preferences (
            user_id,
            tone,
            include_emojis,
            portfolio_repo_url,
            portfolio_branch,
            auto_deploy,
            sample_posts
        )
        VALUES (
            :user_id,
            :tone,
            :include_emojis,
            :portfolio_repo_url,
            :portfolio_branch,
            :auto_deploy,
            :sample_posts
        )
        ON CONFLICT (user_id)
        DO UPDATE SET
            tone = EXCLUDED.tone,
            include_emojis = EXCLUDED.include_emojis,
            portfolio_repo_url = EXCLUDED.portfolio_repo_url,
            portfolio_branch = EXCLUDED.portfolio_branch,
            auto_deploy = EXCLUDED.auto_deploy,
            sample_posts = EXCLUDED.sample_posts
    """)

    await db.execute(
        query,
        {
            "user_id": user_id,
            "tone": data["tone"],
            "include_emojis": data["include_emojis"],
            "portfolio_repo_url": data.get("portfolio_repo_url"),
            "portfolio_branch": data.get("portfolio_branch"),
            "auto_deploy": data["auto_deploy"],

            # 🔥 ALWAYS JSON DICT
            "sample_posts": json.dumps(data.get("sample_posts", {})),
        },
    )

    await db.commit()
