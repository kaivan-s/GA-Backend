-- Migration: Content Expansion
-- 40 morning affirmations + 40 evening prompts + 7-day journey content

-- ============================================
-- MORNING AFFIRMATIONS (Free Tier) - 40 total
-- ============================================

-- Self-Worth & Identity (15)
INSERT INTO public.prompts (theme_id, beat, body, is_free, is_premium)
SELECT t.id, 'morning', v.body, true, false
FROM public.themes t
CROSS JOIN (VALUES
    ('I am worthy of love and belonging, exactly as I am.'),
    ('I trust myself to handle whatever comes my way today.'),
    ('My feelings are valid, and I honor them.'),
    ('I am enough—not because of what I do, but because of who I am.'),
    ('I release the need to be perfect and embrace being real.'),
    ('I deserve rest, joy, and ease—not just productivity.'),
    ('My past does not define my future.'),
    ('I am allowed to take up space in this world.'),
    ('I forgive myself for past mistakes and choose growth.'),
    ('I am becoming the person I want to be, one day at a time.'),
    ('My worth is not measured by my achievements.'),
    ('I am capable of creating the life I want.'),
    ('I choose to believe in my own potential.'),
    ('I am worthy of the good things coming my way.'),
    ('I honor my boundaries and protect my peace.')
) AS v(body)
WHERE t.slug = 'self-worth'
ON CONFLICT DO NOTHING;

-- Presence & Peace (15)
INSERT INTO public.prompts (theme_id, beat, body, is_free, is_premium)
SELECT t.id, 'morning', v.body, true, false
FROM public.themes t
CROSS JOIN (VALUES
    ('Today I choose peace over worry.'),
    ('I release what I cannot control and focus on what I can.'),
    ('This moment is enough. I am enough.'),
    ('I breathe in calm and breathe out tension.'),
    ('I give myself permission to slow down today.'),
    ('I am present in this moment, and this moment is good.'),
    ('I let go of yesterday and do not borrow trouble from tomorrow.'),
    ('My mind is clear, my heart is open, my spirit is calm.'),
    ('I welcome today with curiosity instead of fear.'),
    ('I am grounded in the present, where life actually happens.'),
    ('I choose to respond thoughtfully rather than react quickly.'),
    ('There is nothing I need to fix about myself right now.'),
    ('I trust the timing of my life.'),
    ('I am safe in this moment.'),
    ('I let peace be my anchor today.')
) AS v(body)
WHERE t.slug = 'self-worth'
ON CONFLICT DO NOTHING;

-- Growth & Possibility (10)
INSERT INTO public.prompts (theme_id, beat, body, is_free, is_premium)
SELECT t.id, 'morning', v.body, true, false
FROM public.themes t
CROSS JOIN (VALUES
    ('I am growing stronger with every challenge I face.'),
    ('Every day is a fresh opportunity to begin again.'),
    ('I am open to new possibilities and unexpected gifts.'),
    ('My potential is not limited by my circumstances.'),
    ('I embrace change as a natural part of growth.'),
    ('Small steps in the right direction still count.'),
    ('I am learning, evolving, and becoming.'),
    ('I give myself credit for how far I have come.'),
    ('I am resilient—I have overcome before and I will again.'),
    ('Today holds something good, even if I cannot see it yet.')
) AS v(body)
WHERE t.slug = 'self-worth'
ON CONFLICT DO NOTHING;


-- ============================================
-- EVENING GRATITUDE PROMPTS (Free Tier) - 40 total
-- ============================================

-- Noticing the Good (15)
INSERT INTO public.prompts (theme_id, beat, body, is_free, is_premium)
SELECT t.id, 'evening', v.body, true, false
FROM public.themes t
CROSS JOIN (VALUES
    ('What made you smile today, even briefly?'),
    ('What small win can you celebrate from today?'),
    ('What is one thing that went better than expected?'),
    ('Who or what brought a moment of calm to your day?'),
    ('What is something beautiful you noticed today?'),
    ('What felt easy or effortless today?'),
    ('What is one thing you are looking forward to tomorrow?'),
    ('What simple pleasure did you enjoy today?'),
    ('What is something that worked out, even if imperfectly?'),
    ('What moment today would you want to remember?'),
    ('What made today slightly better than yesterday?'),
    ('What is one thing that felt right today?'),
    ('Where did you find a moment of peace?'),
    ('What surprised you in a good way today?'),
    ('What is one thing you did not have to worry about today?')
) AS v(body)
WHERE t.slug = 'gratitude'
ON CONFLICT DO NOTHING;

-- People & Connection (10)
INSERT INTO public.prompts (theme_id, beat, body, is_free, is_premium)
SELECT t.id, 'evening', v.body, true, false
FROM public.themes t
CROSS JOIN (VALUES
    ('Who showed you kindness today?'),
    ('Who are you grateful to have in your life?'),
    ('What conversation lifted your spirits today?'),
    ('Who made you feel seen or heard today?'),
    ('What act of kindness did you witness or give today?'),
    ('Who would you like to thank but have not yet?'),
    ('What relationship are you grateful for right now?'),
    ('Who believed in you when you needed it?'),
    ('What is something you appreciate about yourself?'),
    ('Who taught you something valuable recently?')
) AS v(body)
WHERE t.slug = 'gratitude'
ON CONFLICT DO NOTHING;

-- Learning & Growth (10)
INSERT INTO public.prompts (theme_id, beat, body, is_free, is_premium)
SELECT t.id, 'evening', v.body, true, false
FROM public.themes t
CROSS JOIN (VALUES
    ('What did you learn about yourself today?'),
    ('What challenge helped you grow?'),
    ('What can you let go of before you sleep?'),
    ('What did you do today that took courage?'),
    ('What mistake taught you something useful?'),
    ('How did you show up for yourself today?'),
    ('What is something you handled well?'),
    ('What strength did you use today?'),
    ('What is one thing you are proud of from today?'),
    ('What can tomorrow''s version of you thank you for doing today?')
) AS v(body)
WHERE t.slug = 'gratitude'
ON CONFLICT DO NOTHING;

-- Rest & Release (5)
INSERT INTO public.prompts (theme_id, beat, body, is_free, is_premium)
SELECT t.id, 'evening', v.body, true, false
FROM public.themes t
CROSS JOIN (VALUES
    ('What can you release to sleep more peacefully?'),
    ('What are you ready to leave in today?'),
    ('What thought can you set down for the night?'),
    ('What permission do you give yourself for tomorrow?'),
    ('What one word describes how you want to feel tomorrow?')
) AS v(body)
WHERE t.slug = 'gratitude'
ON CONFLICT DO NOTHING;


-- ============================================
-- "GETTING STARTED" JOURNEY - 7 Days x 2 Beats
-- ============================================

-- Add title/description columns to journey_days if not exist
ALTER TABLE public.journey_days ADD COLUMN IF NOT EXISTS title TEXT;
ALTER TABLE public.journey_days ADD COLUMN IF NOT EXISTS description TEXT;

-- Create journey prompts (these are special prompts for the journey)
INSERT INTO public.prompts (theme_id, beat, body, is_free, is_premium)
SELECT t.id, v.beat, v.body, true, false
FROM public.themes t
CROSS JOIN (VALUES
    -- Day 1
    ('morning', 'Today, I give myself permission to simply begin—nothing more.'),
    ('evening', 'What is one thing, no matter how small, that you are grateful happened today?'),
    -- Day 2
    ('morning', 'I am here, in this moment. That is enough.'),
    ('evening', 'Where did you feel most present today? What were you doing?'),
    -- Day 3
    ('morning', 'I speak to myself the way I would speak to someone I love.'),
    ('evening', 'How did you show yourself kindness today? If you did not, how could you tomorrow?'),
    -- Day 4
    ('morning', 'I have faced hard things before. I am stronger than I remember.'),
    ('evening', 'What challenge did you navigate today, and what does that say about you?'),
    -- Day 5
    ('morning', 'I release what I cannot control and focus on what I can.'),
    ('evening', 'What are you ready to let go of? What would feel lighter to release?'),
    -- Day 6
    ('morning', 'I am part of something larger than myself. I belong here.'),
    ('evening', 'Who or what made you feel connected today? How did that feel?'),
    -- Day 7
    ('morning', 'This is not the end—it is a foundation. I am building something meaningful.'),
    ('evening', 'Looking back at this week, what has shifted in you? What do you want to carry forward?')
) AS v(beat, body)
WHERE t.slug = 'self-worth'
ON CONFLICT DO NOTHING;

-- Create journey days and link prompts
DO $$
DECLARE
    j_id UUID;
    d_id UUID;
    p_id UUID;
    day_data RECORD;
BEGIN
    -- Get journey ID
    SELECT id INTO j_id FROM public.journeys WHERE slug = 'getting-started';
    
    -- Day definitions
    FOR day_data IN 
        SELECT * FROM (VALUES
            (1, 'Beginning', 'A gentle start to your practice.',
             'Today, I give myself permission to simply begin—nothing more.',
             'What is one thing, no matter how small, that you are grateful happened today?'),
            (2, 'Presence', 'Being here, now.',
             'I am here, in this moment. That is enough.',
             'Where did you feel most present today? What were you doing?'),
            (3, 'Self-Kindness', 'Speaking gently to yourself.',
             'I speak to myself the way I would speak to someone I love.',
             'How did you show yourself kindness today? If you did not, how could you tomorrow?'),
            (4, 'Strength', 'Remembering your resilience.',
             'I have faced hard things before. I am stronger than I remember.',
             'What challenge did you navigate today, and what does that say about you?'),
            (5, 'Letting Go', 'Releasing what you cannot control.',
             'I release what I cannot control and focus on what I can.',
             'What are you ready to let go of? What would feel lighter to release?'),
            (6, 'Connection', 'Belonging to something larger.',
             'I am part of something larger than myself. I belong here.',
             'Who or what made you feel connected today? How did that feel?'),
            (7, 'Continuing', 'Building a foundation.',
             'This is not the end—it is a foundation. I am building something meaningful.',
             'Looking back at this week, what has shifted in you? What do you want to carry forward?')
        ) AS t(day_num, title, description, morning_body, evening_body)
    LOOP
        -- Insert journey day
        INSERT INTO public.journey_days (journey_id, day_number, title, description)
        VALUES (j_id, day_data.day_num, day_data.title, day_data.description)
        ON CONFLICT (journey_id, day_number) DO UPDATE SET title = EXCLUDED.title, description = EXCLUDED.description
        RETURNING id INTO d_id;
        
        -- Link morning prompt
        SELECT id INTO p_id FROM public.prompts WHERE body = day_data.morning_body LIMIT 1;
        IF p_id IS NOT NULL AND d_id IS NOT NULL THEN
            INSERT INTO public.journey_day_prompts (journey_day_id, prompt_id, beat)
            VALUES (d_id, p_id, 'morning')
            ON CONFLICT DO NOTHING;
        END IF;
        
        -- Link evening prompt
        SELECT id INTO p_id FROM public.prompts WHERE body = day_data.evening_body LIMIT 1;
        IF p_id IS NOT NULL AND d_id IS NOT NULL THEN
            INSERT INTO public.journey_day_prompts (journey_day_id, prompt_id, beat)
            VALUES (d_id, p_id, 'evening')
            ON CONFLICT DO NOTHING;
        END IF;
    END LOOP;
END $$;
