from supabase import create_client
from backend.app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

# ============================================================
# Client 1: Regular Supabase Client (for user auth operations)
# Uses ANON_KEY - respects RLS policies
# ============================================================
supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_ANON_KEY
)

logger.info(f"✅ Supabase client initialized: {settings.SUPABASE_URL}")


# ============================================================
# Client 2: Service Role Client (for backend trusted operations)
# Uses SERVICE_ROLE_KEY - BYPASSES RLS policies
# Use this for server-side inserts that shouldn't be blocked by RLS
# ============================================================
try:
    supabase_service = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY
    )
    logger.info("✅ Supabase service client initialized (bypasses RLS)")
except AttributeError as e:
    logger.error(f"❌ SERVICE_ROLE_KEY not configured: {e}")
    logger.warning("⚠️  Activity events inserts will fail. Set SUPABASE_SERVICE_ROLE_KEY in .env")
    supabase_service = None