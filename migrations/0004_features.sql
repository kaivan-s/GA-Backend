-- Migration: Additional Features
-- Custom affirmations, achievements, etc.

-- Custom prompts (user-created affirmations)
CREATE TABLE IF NOT EXISTS public.custom_prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    beat TEXT NOT NULL CHECK (beat IN ('morning', 'evening')),
    body TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_custom_prompts_user ON public.custom_prompts(user_id, beat, is_active);

-- Achievements (badges earned by users)
CREATE TABLE IF NOT EXISTS public.achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    icon TEXT NOT NULL,  -- SF Symbol name
    category TEXT DEFAULT 'general',  -- 'streak', 'journey', 'milestone', 'general'
    threshold INT,  -- e.g., 7 for "7-day streak"
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- User achievements (badges earned)
CREATE TABLE IF NOT EXISTS public.user_achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    achievement_id UUID NOT NULL REFERENCES public.achievements(id),
    earned_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id, achievement_id)
);

CREATE INDEX idx_user_achievements ON public.user_achievements(user_id);

-- Seed default achievements
INSERT INTO public.achievements (slug, title, description, icon, category, threshold, sort_order) VALUES
    ('first_day', 'First Step', 'Completed your first day', 'leaf.fill', 'milestone', 1, 1),
    ('week_one', 'One Week', 'Showed up for 7 days', 'star.fill', 'milestone', 7, 2),
    ('month_one', 'One Month', 'Showed up for 30 days', 'moon.stars.fill', 'milestone', 30, 3),
    ('hundred_days', 'Century', 'Showed up for 100 days', 'trophy.fill', 'milestone', 100, 4),
    ('first_journey', 'Explorer', 'Started your first journey', 'map.fill', 'journey', 1, 10),
    ('journey_complete', 'Graduate', 'Completed a journey', 'graduationcap.fill', 'journey', 1, 11),
    ('first_entry', 'Reflector', 'Wrote your first journal entry', 'pencil.line', 'general', 1, 20),
    ('ten_entries', 'Journaler', 'Wrote 10 journal entries', 'book.fill', 'general', 10, 21),
    ('both_beats', 'Full Circle', 'Completed both morning and evening in one day', 'circle.fill', 'general', 1, 30),
    ('custom_created', 'Creator', 'Created your first custom affirmation', 'sparkles', 'general', 1, 40)
ON CONFLICT (slug) DO NOTHING;

-- Update entitlements source constraint to include 'dodo'
ALTER TABLE public.entitlements DROP CONSTRAINT IF EXISTS entitlements_source_check;
ALTER TABLE public.entitlements ADD CONSTRAINT entitlements_source_check 
    CHECK (source IN ('app_store', 'dodo', 'promo', 'gift'));
