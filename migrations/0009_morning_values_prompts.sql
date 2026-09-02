-- Migration: Values-based morning reflection prompts
-- 40 prompts across 15 values, mix of backward (recall) and forward (intention)
-- Per MORNING_VALUES_REFLECTION_BRIEF.md: "When did [value] show up?" not "I am [trait]"

-- Deactivate old morning prompts (keep for historical entries)
UPDATE public.prompts SET is_active = false WHERE beat = 'morning';

-- Get theme and value IDs
DO $$
DECLARE
    morning_theme_id UUID;
    v_connection UUID;
    v_kindness UUID;
    v_growth UUID;
    v_honesty UUID;
    v_courage UUID;
    v_creativity UUID;
    v_family UUID;
    v_health UUID;
    v_peace UUID;
    v_purpose UUID;
    v_gratitude UUID;
    v_resilience UUID;
    v_joy UUID;
    v_faith UUID;
    v_fairness UUID;
BEGIN
    SELECT id INTO morning_theme_id FROM public.themes WHERE slug = 'morning-affirmations';
    
    SELECT id INTO v_connection FROM public.values WHERE slug = 'connection';
    SELECT id INTO v_kindness FROM public.values WHERE slug = 'kindness';
    SELECT id INTO v_growth FROM public.values WHERE slug = 'growth';
    SELECT id INTO v_honesty FROM public.values WHERE slug = 'honesty';
    SELECT id INTO v_courage FROM public.values WHERE slug = 'courage';
    SELECT id INTO v_creativity FROM public.values WHERE slug = 'creativity';
    SELECT id INTO v_family FROM public.values WHERE slug = 'family';
    SELECT id INTO v_health FROM public.values WHERE slug = 'health';
    SELECT id INTO v_peace FROM public.values WHERE slug = 'peace';
    SELECT id INTO v_purpose FROM public.values WHERE slug = 'purpose';
    SELECT id INTO v_gratitude FROM public.values WHERE slug = 'gratitude';
    SELECT id INTO v_resilience FROM public.values WHERE slug = 'resilience';
    SELECT id INTO v_joy FROM public.values WHERE slug = 'joy';
    SELECT id INTO v_faith FROM public.values WHERE slug = 'faith';
    SELECT id INTO v_fairness FROM public.values WHERE slug = 'fairness';

    -- CONNECTION (3 prompts)
    INSERT INTO public.prompts (theme_id, beat, body, value_id, reflection_type, is_free, is_active) VALUES
    (morning_theme_id, 'morning', 'When did connection matter to you recently?', v_connection, 'backward', true, true),
    (morning_theme_id, 'morning', 'Who made you feel seen or heard lately?', v_connection, 'backward', true, true),
    (morning_theme_id, 'morning', 'How might you honor connection today?', v_connection, 'forward', true, true);

    -- KINDNESS (3 prompts)
    INSERT INTO public.prompts (theme_id, beat, body, value_id, reflection_type, is_free, is_active) VALUES
    (morning_theme_id, 'morning', 'When did you show kindness recently — to yourself or someone else?', v_kindness, 'backward', true, true),
    (morning_theme_id, 'morning', 'What small act of kindness touched you lately?', v_kindness, 'backward', true, true),
    (morning_theme_id, 'morning', 'Where might kindness guide you today?', v_kindness, 'forward', true, true);

    -- GROWTH (3 prompts)
    INSERT INTO public.prompts (theme_id, beat, body, value_id, reflection_type, is_free, is_active) VALUES
    (morning_theme_id, 'morning', 'When did you learn something recently, even something small?', v_growth, 'backward', true, true),
    (morning_theme_id, 'morning', 'What challenge helped you grow lately?', v_growth, 'backward', true, true),
    (morning_theme_id, 'morning', 'How might growth show up in your day?', v_growth, 'forward', true, true);

    -- HONESTY (3 prompts)
    INSERT INTO public.prompts (theme_id, beat, body, value_id, reflection_type, is_free, is_active) VALUES
    (morning_theme_id, 'morning', 'When did being honest with yourself matter recently?', v_honesty, 'backward', true, true),
    (morning_theme_id, 'morning', 'What truth did you honor lately?', v_honesty, 'backward', true, true),
    (morning_theme_id, 'morning', 'Where might honesty serve you today?', v_honesty, 'forward', true, true);

    -- COURAGE (3 prompts)
    INSERT INTO public.prompts (theme_id, beat, body, value_id, reflection_type, is_free, is_active) VALUES
    (morning_theme_id, 'morning', 'When did you do something brave recently, even if small?', v_courage, 'backward', true, true),
    (morning_theme_id, 'morning', 'What fear did you face lately?', v_courage, 'backward', true, true),
    (morning_theme_id, 'morning', 'Where might courage guide you today?', v_courage, 'forward', true, true);

    -- CREATIVITY (3 prompts)
    INSERT INTO public.prompts (theme_id, beat, body, value_id, reflection_type, is_free, is_active) VALUES
    (morning_theme_id, 'morning', 'When did you make or create something recently?', v_creativity, 'backward', true, true),
    (morning_theme_id, 'morning', 'What sparked your imagination lately?', v_creativity, 'backward', true, true),
    (morning_theme_id, 'morning', 'How might creativity show up today?', v_creativity, 'forward', true, true);

    -- FAMILY (3 prompts)
    INSERT INTO public.prompts (theme_id, beat, body, value_id, reflection_type, is_free, is_active) VALUES
    (morning_theme_id, 'morning', 'When did family — chosen or given — matter to you recently?', v_family, 'backward', true, true),
    (morning_theme_id, 'morning', 'Who in your family circle showed up for you lately?', v_family, 'backward', true, true),
    (morning_theme_id, 'morning', 'How might you honor family today?', v_family, 'forward', true, true);

    -- HEALTH (3 prompts)
    INSERT INTO public.prompts (theme_id, beat, body, value_id, reflection_type, is_free, is_active) VALUES
    (morning_theme_id, 'morning', 'When did you take care of your body or mind recently?', v_health, 'backward', true, true),
    (morning_theme_id, 'morning', 'What did your body thank you for lately?', v_health, 'backward', true, true),
    (morning_theme_id, 'morning', 'How might you care for yourself today?', v_health, 'forward', true, true);

    -- PEACE (3 prompts)
    INSERT INTO public.prompts (theme_id, beat, body, value_id, reflection_type, is_free, is_active) VALUES
    (morning_theme_id, 'morning', 'When did you feel calm or at ease recently?', v_peace, 'backward', true, true),
    (morning_theme_id, 'morning', 'What moment of stillness touched you lately?', v_peace, 'backward', true, true),
    (morning_theme_id, 'morning', 'Where might you find peace today?', v_peace, 'forward', true, true);

    -- PURPOSE (3 prompts)
    INSERT INTO public.prompts (theme_id, beat, body, value_id, reflection_type, is_free, is_active) VALUES
    (morning_theme_id, 'morning', 'When did your work or effort feel meaningful recently?', v_purpose, 'backward', true, true),
    (morning_theme_id, 'morning', 'What gave you a sense of purpose lately?', v_purpose, 'backward', true, true),
    (morning_theme_id, 'morning', 'How might purpose guide your day?', v_purpose, 'forward', true, true);

    -- GRATITUDE (2 prompts - less than others since evening is gratitude-focused)
    INSERT INTO public.prompts (theme_id, beat, body, value_id, reflection_type, is_free, is_active) VALUES
    (morning_theme_id, 'morning', 'What are you genuinely thankful for this morning?', v_gratitude, 'backward', true, true),
    (morning_theme_id, 'morning', 'What might you appreciate more fully today?', v_gratitude, 'forward', true, true);

    -- RESILIENCE (3 prompts)
    INSERT INTO public.prompts (theme_id, beat, body, value_id, reflection_type, is_free, is_active) VALUES
    (morning_theme_id, 'morning', 'When did you bounce back from something difficult recently?', v_resilience, 'backward', true, true),
    (morning_theme_id, 'morning', 'What hard thing did you get through lately?', v_resilience, 'backward', true, true),
    (morning_theme_id, 'morning', 'Where might resilience serve you today?', v_resilience, 'forward', true, true);

    -- JOY (3 prompts)
    INSERT INTO public.prompts (theme_id, beat, body, value_id, reflection_type, is_free, is_active) VALUES
    (morning_theme_id, 'morning', 'When did you feel genuine delight recently?', v_joy, 'backward', true, true),
    (morning_theme_id, 'morning', 'What made you laugh or smile lately?', v_joy, 'backward', true, true),
    (morning_theme_id, 'morning', 'Where might joy find you today?', v_joy, 'forward', true, true);

    -- FAITH (2 prompts)
    INSERT INTO public.prompts (theme_id, beat, body, value_id, reflection_type, is_free, is_active) VALUES
    (morning_theme_id, 'morning', 'When did trust in something larger comfort you recently?', v_faith, 'backward', true, true),
    (morning_theme_id, 'morning', 'How might faith guide you today?', v_faith, 'forward', true, true);

    -- FAIRNESS (2 prompts)
    INSERT INTO public.prompts (theme_id, beat, body, value_id, reflection_type, is_free, is_active) VALUES
    (morning_theme_id, 'morning', 'When did treating someone fairly matter to you recently?', v_fairness, 'backward', true, true),
    (morning_theme_id, 'morning', 'Where might fairness guide you today?', v_fairness, 'forward', true, true);

END $$;
