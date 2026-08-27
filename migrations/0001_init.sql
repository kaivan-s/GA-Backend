-- Gratitude App: Initial Schema
-- Run in Supabase SQL Editor

-- Users (synced from Clerk)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clerk_user_id TEXT UNIQUE NOT NULL,
    email TEXT,
    display_name TEXT,
    timezone TEXT DEFAULT 'UTC',
    day_reset_hour INT DEFAULT 3,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_users_clerk ON public.users(clerk_user_id);

-- Themes (categories for prompts)
CREATE TABLE IF NOT EXISTS public.themes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    palette TEXT DEFAULT 'morning',
    is_premium BOOLEAN DEFAULT false,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Prompts (affirmations/gratitude questions)
CREATE TABLE IF NOT EXISTS public.prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    theme_id UUID REFERENCES public.themes(id),
    beat TEXT NOT NULL CHECK (beat IN ('morning', 'evening')),
    body TEXT NOT NULL,
    audio_path TEXT,
    is_free BOOLEAN DEFAULT true,
    is_premium BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_prompts_beat ON public.prompts(beat, is_active);

-- Journeys (multi-day guided programs)
CREATE TABLE IF NOT EXISTS public.journeys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT UNIQUE NOT NULL,
    theme_id UUID REFERENCES public.themes(id),
    title TEXT NOT NULL,
    description TEXT,
    length_days INT DEFAULT 7,
    is_free BOOLEAN DEFAULT false,
    is_premium BOOLEAN DEFAULT true,
    cover_path TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Journey days
CREATE TABLE IF NOT EXISTS public.journey_days (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journey_id UUID NOT NULL REFERENCES public.journeys(id) ON DELETE CASCADE,
    day_number INT NOT NULL,
    UNIQUE(journey_id, day_number)
);

-- Journey day prompts (link prompts to journey days)
CREATE TABLE IF NOT EXISTS public.journey_day_prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journey_day_id UUID NOT NULL REFERENCES public.journey_days(id) ON DELETE CASCADE,
    prompt_id UUID NOT NULL REFERENCES public.prompts(id),
    beat TEXT NOT NULL CHECK (beat IN ('morning', 'evening'))
);

-- User journeys (active journey enrollment)
CREATE TABLE IF NOT EXISTS public.user_journeys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    journey_id UUID NOT NULL REFERENCES public.journeys(id),
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'abandoned')),
    started_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_user_journeys_active ON public.user_journeys(user_id, status);

-- Ritual completions (beat completion records)
CREATE TABLE IF NOT EXISTS public.ritual_completions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    local_date DATE NOT NULL,
    beat TEXT NOT NULL CHECK (beat IN ('morning', 'evening')),
    prompt_id UUID REFERENCES public.prompts(id),
    user_journey_id UUID REFERENCES public.user_journeys(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id, local_date, beat)
);

CREATE INDEX idx_completions_user_date ON public.ritual_completions(user_id, local_date);

-- Journal entries (text responses to prompts)
CREATE TABLE IF NOT EXISTS public.journal_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    prompt_id UUID REFERENCES public.prompts(id),
    beat TEXT NOT NULL,
    local_date DATE NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_entries_user ON public.journal_entries(user_id, local_date);

-- Day stats (aggregated daily stats for progress)
CREATE TABLE IF NOT EXISTS public.day_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    local_date DATE NOT NULL,
    morning BOOLEAN DEFAULT false,
    evening BOOLEAN DEFAULT false,
    UNIQUE(user_id, local_date)
);

CREATE INDEX idx_day_stats_user ON public.day_stats(user_id, local_date);

-- Entitlements (subscription status)
CREATE TABLE IF NOT EXISTS public.entitlements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    tier TEXT DEFAULT 'free' CHECK (tier IN ('free', 'premium')),
    source TEXT DEFAULT 'app_store' CHECK (source IN ('app_store', 'promo', 'gift')),
    original_transaction_id TEXT,
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_entitlements_user ON public.entitlements(user_id, is_active);
CREATE INDEX idx_entitlements_txn ON public.entitlements(original_transaction_id);

-- Devices (for push notifications)
CREATE TABLE IF NOT EXISTS public.devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    device_token TEXT NOT NULL,
    platform TEXT DEFAULT 'ios',
    morning_time TEXT DEFAULT '08:00',
    evening_time TEXT DEFAULT '20:00',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id, device_token)
);

CREATE INDEX idx_devices_user ON public.devices(user_id, is_active);
