-- =============================================================================
-- Athena / Artemis — Initial Database Schema
-- Idempotent: safe to run multiple times
-- =============================================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ---------------------------------------------------------------------------
-- Helper: auto-update updated_at on row modification
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ---------------------------------------------------------------------------
-- Tasks
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tasks (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title           VARCHAR(200) NOT NULL,
    description     TEXT,
    quadrant        INTEGER NOT NULL CHECK (quadrant BETWEEN 1 AND 4),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'in_progress', 'completed')),
    pomodoro_count  INTEGER NOT NULL DEFAULT 0,
    due_date        TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at    TIMESTAMPTZ
);

DROP TRIGGER IF EXISTS update_tasks_updated_at ON tasks;
CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ---------------------------------------------------------------------------
-- Daily Plans (1-3-5 rule: 1 major, 3 medium, 5 small)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS daily_plans (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date            DATE NOT NULL UNIQUE,
    major_task_id   UUID REFERENCES tasks(id) ON DELETE SET NULL,
    medium_task_ids UUID[] NOT NULL DEFAULT '{}',
    small_task_ids  UUID[] NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

DROP TRIGGER IF EXISTS update_daily_plans_updated_at ON daily_plans;
CREATE TRIGGER update_daily_plans_updated_at
    BEFORE UPDATE ON daily_plans
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ---------------------------------------------------------------------------
-- Pomodoro Sessions
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS pomodoro_sessions (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id           UUID REFERENCES tasks(id) ON DELETE SET NULL,
    started_at        TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at          TIMESTAMPTZ,
    duration_minutes  INTEGER NOT NULL DEFAULT 25 CHECK (duration_minutes BETWEEN 1 AND 90),
    completed         BOOLEAN NOT NULL DEFAULT FALSE,
    interrupted       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

DROP TRIGGER IF EXISTS update_pomodoro_sessions_updated_at ON pomodoro_sessions;
CREATE TRIGGER update_pomodoro_sessions_updated_at
    BEFORE UPDATE ON pomodoro_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ---------------------------------------------------------------------------
-- RPC: Atomically increment pomodoro count on a task
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION increment_pomodoro_count(p_task_id UUID)
RETURNS INTEGER AS $$
DECLARE
    v_new_count INTEGER;
BEGIN
    UPDATE tasks
    SET pomodoro_count = pomodoro_count + 1
    WHERE id = p_task_id
    RETURNING pomodoro_count INTO v_new_count;

    RETURN v_new_count;
END;
$$ LANGUAGE plpgsql;

-- ---------------------------------------------------------------------------
-- Row-Level Security (enable for Supabase anon/authenticated access)
-- ---------------------------------------------------------------------------
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE pomodoro_sessions ENABLE ROW LEVEL SECURITY;

-- Allow full access for anon and authenticated roles (single-user app)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'tasks_allow_all') THEN
        EXECUTE 'CREATE POLICY tasks_allow_all ON tasks FOR ALL USING (true) WITH CHECK (true)';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'daily_plans_allow_all') THEN
        EXECUTE 'CREATE POLICY daily_plans_allow_all ON daily_plans FOR ALL USING (true) WITH CHECK (true)';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'pomodoro_sessions_allow_all') THEN
        EXECUTE 'CREATE POLICY pomodoro_sessions_allow_all ON pomodoro_sessions FOR ALL USING (true) WITH CHECK (true)';
    END IF;
END $$;

-- Grant access to anon and authenticated roles
GRANT ALL ON tasks TO anon, authenticated;
GRANT ALL ON daily_plans TO anon, authenticated;
GRANT ALL ON pomodoro_sessions TO anon, authenticated;
