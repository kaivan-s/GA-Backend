-- Seed: Free content + intro journey

-- Themes
INSERT INTO public.themes (slug, title, palette, is_premium, sort_order) VALUES
('self-worth', 'Self-Worth', 'morning', false, 1),
('gratitude', 'Gratitude', 'evening', false, 2),
('abundance', 'Abundance', 'morning', true, 3),
('relationships', 'Relationships', 'evening', true, 4)
ON CONFLICT (slug) DO NOTHING;

-- Morning affirmations (free)
INSERT INTO public.prompts (theme_id, beat, body, is_free, is_premium)
SELECT t.id, 'morning', v.body, true, false
FROM public.themes t
CROSS JOIN (VALUES
    ('I am worthy of love and belonging.'),
    ('Today I choose peace over worry.'),
    ('I trust myself to handle whatever comes my way.'),
    ('I am growing stronger every day.'),
    ('My potential is limitless.')
) AS v(body)
WHERE t.slug = 'self-worth';

-- Evening gratitude prompts (free)
INSERT INTO public.prompts (theme_id, beat, body, is_free, is_premium)
SELECT t.id, 'evening', v.body, true, false
FROM public.themes t
CROSS JOIN (VALUES
    ('What made you smile today?'),
    ('Who showed you kindness today?'),
    ('What small win can you celebrate?'),
    ('What are you looking forward to tomorrow?'),
    ('What did you learn today?')
) AS v(body)
WHERE t.slug = 'gratitude';

-- Intro journey (free, 7 days)
INSERT INTO public.journeys (slug, title, description, length_days, is_free, is_premium)
VALUES (
    'getting-started',
    'Getting Started',
    'A gentle 7-day introduction to daily affirmations and gratitude.',
    7,
    true,
    false
) ON CONFLICT (slug) DO NOTHING;

-- Premium Journeys
INSERT INTO public.journeys (slug, title, description, length_days, is_free, is_premium, theme_id)
VALUES 
    ('abundance-mindset', 'Abundance Mindset', 'Transform scarcity thinking into abundance consciousness over 14 days.', 14, false, true, 
        (SELECT id FROM public.themes WHERE slug = 'abundance')),
    ('self-love-deep-dive', 'Self-Love Deep Dive', 'A 21-day journey to cultivate unconditional self-acceptance.', 21, false, true,
        (SELECT id FROM public.themes WHERE slug = 'self-worth')),
    ('gratitude-mastery', 'Gratitude Mastery', 'Deepen your gratitude practice with this 10-day guided experience.', 10, false, true,
        (SELECT id FROM public.themes WHERE slug = 'gratitude')),
    ('relationship-healing', 'Relationship Healing', 'Heal and strengthen your connections over 14 transformative days.', 14, false, true,
        (SELECT id FROM public.themes WHERE slug = 'relationships'))
ON CONFLICT (slug) DO NOTHING;
