import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import json



async def sync_github_account(
    db: AsyncSession,
    user_id: str,
    access_token: str,
    token_scope: str | None = None
):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json"
    }

    async with httpx.AsyncClient() as client:
        gh_user = (await client.get(
            "https://api.github.com/user",
            headers=headers
        )).json()

        repos = (await client.get(
            "https://api.github.com/user/repos?per_page=100",
            headers=headers
        )).json()

    # Store connected account
    await db.execute(
        text("""
        INSERT INTO connected_accounts
        (user_id, platform, access_token, token_scope, profile_id, profile_data)
        VALUES (:uid, 'github', :token, :scope, :pid, :pdata)
        ON CONFLICT (user_id, platform)
        DO UPDATE SET
          access_token = EXCLUDED.access_token,
          token_scope = EXCLUDED.token_scope,
          profile_data = EXCLUDED.profile_data
        """),
        {
            "uid": user_id,
            "token": access_token,
            "scope": token_scope,
            "pid": str(gh_user["id"]),
            "pdata": json.dumps({
                        "login": gh_user["login"],
                        "avatar_url": gh_user["avatar_url"],
                        "html_url": gh_user["html_url"]
                    })

        }
    )

    # Store repositories
    for repo in repos:
        await db.execute(
            text("""
            INSERT INTO repositories
            (user_id, repo_url, repo_owner, repo_name,
             language, description, default_branch, metadata, last_synced)
            VALUES
            (:uid, :url, :owner, :name, :lang, :desc, :branch, :meta, NOW())
            ON CONFLICT (user_id, repo_url) DO NOTHING
            """),
            {
                "uid": user_id,
                "url": repo["html_url"],
                "owner": repo["owner"]["login"],
                "name": repo["name"],
                "lang": repo["language"],
                "desc": repo["description"],
                "branch": repo["default_branch"],
                "meta": json.dumps(repo)
            }
        )

    await db.commit()
