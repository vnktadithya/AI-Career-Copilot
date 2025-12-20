-- app/database/migrations/oo1_initial_schema.sql
-- Enable UUID extension (Supabase has this by default)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Core users table (Supabase Auth integration)
CREATE TABLE users (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email VARCHAR UNIQUE NOT NULL,
  name VARCHAR,
  role VARCHAR DEFAULT 'user',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User preferences and voice profile
CREATE TABLE user_preferences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  tone VARCHAR(20) DEFAULT 'storytelling' CHECK (tone IN ('formal', 'casual', 'technical', 'storytelling')),
  include_emojis BOOLEAN DEFAULT TRUE,
  sample_posts JSONB DEFAULT '[]'::JSONB,
  auto_approve_rules JSONB DEFAULT '{}'::JSONB,
  portfolio_repo_url VARCHAR,
  portfolio_branch VARCHAR,
  auto_deploy BOOLEAN DEFAULT FALSE,
  per_repo_config JSONB DEFAULT '{}'::JSONB,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id)
);

-- Connected platform accounts (GitHub, LinkedIn, Twitter/X, etc.)
CREATE TABLE connected_accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  platform VARCHAR(20) NOT NULL CHECK (platform IN ('github', 'linkedin', 'twitter')),
  access_token TEXT NOT NULL,
  refresh_token TEXT,
  token_scope TEXT,
  token_expires_at TIMESTAMP WITH TIME ZONE,
  profile_id VARCHAR,
  profile_data JSONB,
  connected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, platform)
);

-- Tracked repositories
CREATE TABLE repositories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  repo_url VARCHAR NOT NULL,
  repo_owner VARCHAR,
  repo_name VARCHAR,
  language VARCHAR,
  description TEXT,
  is_portfolio BOOLEAN DEFAULT FALSE,
  webhook_configured BOOLEAN DEFAULT FALSE,
  branch_strategy VARCHAR DEFAULT 'pr' CHECK (branch_strategy IN ('direct', 'pr')),
  default_branch VARCHAR DEFAULT 'main',
  last_synced TIMESTAMP WITH TIME ZONE,
  metadata JSONB DEFAULT '{}'::JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, repo_url)
);

-- Activity events from VS Code extension & GitHub webhooks
CREATE TABLE activity_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  repo_id UUID REFERENCES repositories(id) ON DELETE SET NULL,
  event_type VARCHAR NOT NULL, -- 'pr_merged', 'push', 'release', 'vscode_commit', etc.
  event_source VARCHAR, -- 'vscode_extension', 'github_webhook'
  payload JSONB NOT NULL,
  processed BOOLEAN DEFAULT FALSE,
  dedupe_key VARCHAR UNIQUE, -- Prevent duplicate processing
  received_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Story proposals (Inbox core table)
CREATE TABLE stories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  repo_id UUID REFERENCES repositories(id) ON DELETE SET NULL,
  activity_event_id UUID REFERENCES activity_events(id) ON DELETE SET NULL,
  trigger_event VARCHAR NOT NULL,
  trigger_source VARCHAR,
  gemini_proposal JSONB, -- {readme_update, portfolio_changes, linkedin_post, twitter_post, commit_suggestion, rationale}
  generation_status VARCHAR DEFAULT 'pending' CHECK (generation_status IN ('pending', 'generated', 'failed')),
  status VARCHAR DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'executed', 'failed', 'archived')),
  user_edits JSONB DEFAULT '{}'::JSONB,
  celery_task_id VARCHAR, -- Link to Celery execution
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  approved_at TIMESTAMP WITH TIME ZONE,
  executed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_stories_user_status ON stories(user_id, status);
CREATE INDEX idx_stories_created ON stories(created_at DESC);

-- Audit logs for all executed actions
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  story_id UUID REFERENCES stories(id) ON DELETE SET NULL,
  action_type VARCHAR NOT NULL, -- 'github_commit', 'github_pr', 'portfolio_deploy', 'linkedin_post', 'twitter_post', 'rollback'
  platform VARCHAR, -- 'github', 'linkedin', 'twitter', 'portfolio'
  target_url VARCHAR,
  target_id VARCHAR, -- commit SHA, post ID, PR number
  status VARCHAR DEFAULT 'pending' CHECK (status IN ('pending', 'success', 'failed', 'rolled_back')),
  response_data JSONB,
  error_message TEXT,
  celery_task_id VARCHAR,
  initiated_by VARCHAR DEFAULT 'agent',
  executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_story ON audit_logs(story_id);
CREATE INDEX idx_audit_status ON audit_logs(status);
CREATE INDEX idx_audit_executed ON audit_logs(executed_at DESC);

-- Celery task tracking (for UI polling)
CREATE TABLE celery_tasks (
  id VARCHAR PRIMARY KEY, -- Celery task ID
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  story_id UUID REFERENCES stories(id) ON DELETE SET NULL,
  task_name VARCHAR NOT NULL,
  status VARCHAR DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'STARTED', 'SUCCESS', 'FAILURE', 'RETRY')),
  result JSONB,
  traceback TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Image and Video storage (through Supabase)
CREATE TABLE story_media_assets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  story_id UUID REFERENCES stories(id) ON DELETE CASCADE,
  platform VARCHAR(20) NOT NULL CHECK (platform IN ('linkedin', 'twitter')),
  kind VARCHAR(20) NOT NULL CHECK (kind IN ('image', 'video')),
  storage_bucket VARCHAR NOT NULL,         -- e.g. 'career-story-linkedin-images'
  storage_path VARCHAR NOT NULL,           -- e.g. 'user/{user_id}/story/{story_id}/hero.png'
  storage_metadata JSONB DEFAULT '{}'::JSONB,
  platform_asset_id VARCHAR,               -- e.g. LinkedIn asset URN
  platform_metadata JSONB,                 -- full API response snapshot
  is_primary BOOLEAN DEFAULT FALSE,        -- main image for the post
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS Policies (Supabase Row Level Security)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own profile" ON users FOR SELECT USING (auth.uid() = id);

ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own preferences" ON user_preferences 
  FOR ALL USING (auth.uid() = user_id);

ALTER TABLE connected_accounts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own accounts" ON connected_accounts 
  FOR ALL USING (auth.uid() = user_id);

ALTER TABLE repositories ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own repos" ON repositories 
  FOR ALL USING (auth.uid() = user_id);

ALTER TABLE activity_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own events" ON activity_events 
  FOR ALL USING (auth.uid() = user_id);

ALTER TABLE stories ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own stories" ON stories 
  FOR ALL USING (auth.uid() = user_id);

ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own audit logs" ON audit_logs 
  FOR SELECT USING (auth.uid() = user_id);

ALTER TABLE celery_tasks ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own tasks" ON celery_tasks 
  FOR SELECT USING (auth.uid() = user_id);

ALTER TABLE story_media_assets ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users manage own media" ON story_media_assets
  FOR ALL USING (auth.uid() = user_id);

-- Indexes for performance
CREATE INDEX idx_repos_user ON repositories(user_id);
CREATE INDEX idx_stories_user_pending ON stories(user_id) WHERE status = 'pending';


-- New Modifications

-- =========================================================
-- Schema Extension: Semantic context for Gemini (v2)
-- =========================================================

ALTER TABLE stories
ADD COLUMN IF NOT EXISTS semantic_tags JSONB DEFAULT '[]'::JSONB;

-- =========================================================
-- Project Memory Snapshots (Rolling semantic memory)
-- =========================================================

CREATE TABLE IF NOT EXISTS project_memory_snapshots (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  repo_id UUID REFERENCES repositories(id) ON DELETE CASCADE,

  project_summary TEXT NOT NULL,
  -- High-level explanation of what the project is and why it exists

  technical_summary TEXT,
  -- Architecture, stack, key systems

  narrative_state JSONB DEFAULT '{}'::JSONB,
  -- {
  --   "stage": "active-development | beta | stable | maintenance",
  --   "last_major_milestone": "...",
  --   "public_storyline": "..."
  -- }

  publicly_announced JSONB DEFAULT '[]'::JSONB,
  -- List of story_ids or summaries already shared publicly (LinkedIn etc.)

  source_story_ids JSONB DEFAULT '[]'::JSONB,
  -- Which stories were compacted into this snapshot

  bootstrap_source VARCHAR DEFAULT 'observed'
    CHECK (bootstrap_source IN ('observed', 'inferred')),

  last_compacted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  UNIQUE(repo_id)
);


-- =========================================================
-- User Voice Profiles (learned writing style)
-- =========================================================

CREATE TABLE IF NOT EXISTS user_voice_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,

  voice_signature JSONB DEFAULT '{}'::JSONB,
    -- {
  --   "avg_sentence_length": 18,
  --   "emoji_frequency": 0.12,
  --   "tone_distribution": {"technical": 0.6, "storytelling": 0.4},
  --   "preferred_hooks": ["problem-first", "impact-first"]
  -- }

  canonical_samples JSONB DEFAULT '[]'::JSONB,
    -- Only best approved outputs (not everything)

  last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  UNIQUE(user_id)
);

-- =========================================================
-- Repository Context Cache (MCP optimization layer)
-- =========================================================

CREATE TABLE IF NOT EXISTS repo_context_cache (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  repo_id UUID REFERENCES repositories(id) ON DELETE CASCADE,

  readme_summary TEXT,
  -- Current README distilled to a short summary

  repo_structure JSONB,
  -- { "modules": 5, "key_dirs": ["api", "frontend"] }

  recent_commits JSONB DEFAULT '[]'::JSONB,
  -- Last 5 commits used for reasoning

  last_mcp_hash VARCHAR,
  -- Hash of repo state (to detect changes)

  last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  ttl TIMESTAMP WITH TIME ZONE,

  UNIQUE(repo_id)
);


-- =========================================================
-- RLS Policies for Context Tables
-- =========================================================

-- Project memory
ALTER TABLE project_memory_snapshots ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own project memory"
ON project_memory_snapshots
FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM repositories r
    WHERE r.id = project_memory_snapshots.repo_id
    AND r.user_id = auth.uid()
  )
);

-- User voice profile
ALTER TABLE user_voice_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users manage own voice profile"
ON user_voice_profiles
FOR ALL
USING (auth.uid() = user_id);

-- Repo context cache
ALTER TABLE repo_context_cache ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own repo cache"
ON repo_context_cache
FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM repositories r
    WHERE r.id = repo_context_cache.repo_id
    AND r.user_id = auth.uid()
  )
);
