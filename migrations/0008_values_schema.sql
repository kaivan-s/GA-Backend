-- Migration: Values-based morning reflection system
-- Per MORNING_VALUES_REFLECTION_BRIEF.md: values reflection, not recited affirmations

-- Core values that users can select from
CREATE TABLE IF NOT EXISTS public.values (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    icon TEXT,  -- SF Symbol name for iOS
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- User's selected values (they pick ones that resonate)
CREATE TABLE IF NOT EXISTS public.user_values (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    value_id UUID NOT NULL REFERENCES public.values(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id, value_id)
);

CREATE INDEX IF NOT EXISTS idx_user_values_user ON public.user_values(user_id);

-- Link morning prompts to values (a prompt reflects on a specific value)
ALTER TABLE public.prompts 
ADD COLUMN IF NOT EXISTS value_id UUID REFERENCES public.values(id);

-- Add reflection_type for morning prompts (backward = recall, forward = intention)
ALTER TABLE public.prompts 
ADD COLUMN IF NOT EXISTS reflection_type TEXT CHECK (reflection_type IN ('backward', 'forward'));

CREATE INDEX IF NOT EXISTS idx_prompts_value ON public.prompts(value_id, beat, is_active);

-- Seed core values
INSERT INTO public.values (slug, name, description, icon, sort_order) VALUES
('connection', 'Connection', 'Meaningful relationships and belonging', 'person.2.fill', 1),
('kindness', 'Kindness', 'Compassion toward yourself and others', 'heart.fill', 2),
('growth', 'Growth', 'Learning, improving, becoming', 'leaf.fill', 3),
('honesty', 'Honesty', 'Truth and authenticity in how you live', 'checkmark.shield.fill', 4),
('courage', 'Courage', 'Facing difficulty with bravery', 'flame.fill', 5),
('creativity', 'Creativity', 'Making, expressing, imagining', 'paintbrush.fill', 6),
('family', 'Family', 'Those you call home', 'house.fill', 7),
('health', 'Health', 'Caring for your body and mind', 'figure.walk', 8),
('peace', 'Peace', 'Calm, stillness, acceptance', 'moon.stars.fill', 9),
('purpose', 'Purpose', 'Meaning and contribution', 'star.fill', 10),
('gratitude', 'Gratitude', 'Appreciating what you have', 'hands.clap.fill', 11),
('resilience', 'Resilience', 'Bouncing back, persisting', 'arrow.up.heart.fill', 12),
('joy', 'Joy', 'Delight, play, lightness', 'sparkles', 13),
('faith', 'Faith', 'Trust in something larger', 'sun.max.fill', 14),
('fairness', 'Fairness', 'Justice and treating others well', 'scale.3d', 15)
ON CONFLICT (slug) DO NOTHING;
