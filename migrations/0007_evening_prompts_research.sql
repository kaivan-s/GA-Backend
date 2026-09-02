-- Migration: Research-based evening prompts
-- 40 prompts across 6 angles, each with specificity focus and causation follow-up
-- Per GRATITUDE_RESEARCH_BRIEF.md: specificity + causation + variety = effective practice

-- First, deactivate old evening prompts (keep for historical entries)
UPDATE public.prompts SET is_active = false WHERE beat = 'evening';

-- Get the evening theme ID
DO $$
DECLARE
    evening_theme_id UUID;
BEGIN
    SELECT id INTO evening_theme_id FROM public.themes WHERE slug = 'evening-gratitude';

    -- ANGLE 1: small_moment (7 prompts)
    -- Small things that went right today
    INSERT INTO public.prompts (theme_id, beat, body, causation_prompt, angle, is_free, is_active) VALUES
    (evening_theme_id, 'evening', 'Which small moment today made you pause and smile?', 'What made that moment happen?', 'small_moment', true, true),
    (evening_theme_id, 'evening', 'What tiny thing went right today that you almost didn''t notice?', 'Why do you think it went well?', 'small_moment', true, true),
    (evening_theme_id, 'evening', 'What brief moment of ease did you experience today?', 'What allowed that ease to happen?', 'small_moment', true, true),
    (evening_theme_id, 'evening', 'What small pleasure did you enjoy today?', 'What made it possible to enjoy that?', 'small_moment', true, true),
    (evening_theme_id, 'evening', 'What unexpected good thing happened today, even if small?', 'What do you think led to that?', 'small_moment', true, true),
    (evening_theme_id, 'evening', 'What moment today felt lighter than expected?', 'What contributed to that lightness?', 'small_moment', true, true),
    (evening_theme_id, 'evening', 'What small win did you have today?', 'What was your part in making it happen?', 'small_moment', true, true);

    -- ANGLE 2: person (7 prompts)
    -- Someone who helped or showed up
    INSERT INTO public.prompts (theme_id, beat, body, causation_prompt, angle, is_free, is_active) VALUES
    (evening_theme_id, 'evening', 'Who showed up for you today, even in a small way?', 'What do you think prompted them to do that?', 'person', true, true),
    (evening_theme_id, 'evening', 'Who made your day a little easier today?', 'What allowed them to help you?', 'person', true, true),
    (evening_theme_id, 'evening', 'Who did you connect with today that left you feeling good?', 'What made that connection possible?', 'person', true, true),
    (evening_theme_id, 'evening', 'Who surprised you with kindness today?', 'Why do you think they did that?', 'person', true, true),
    (evening_theme_id, 'evening', 'Who listened to you today when you needed it?', 'What enabled that conversation?', 'person', true, true),
    (evening_theme_id, 'evening', 'Who made you laugh or smile today?', 'What was happening that led to that moment?', 'person', true, true),
    (evening_theme_id, 'evening', 'Whose presence today made things better?', 'What brought you together today?', 'person', true, true);

    -- ANGLE 3: body_health (7 prompts)
    -- Something your body/health let you do
    INSERT INTO public.prompts (theme_id, beat, body, causation_prompt, angle, is_free, is_active) VALUES
    (evening_theme_id, 'evening', 'What did your body let you do today?', 'What supported your body in doing that?', 'body_health', true, true),
    (evening_theme_id, 'evening', 'What physical sensation did you enjoy today?', 'What created the conditions for that feeling?', 'body_health', true, true),
    (evening_theme_id, 'evening', 'When did your body feel at ease today?', 'What contributed to that moment of ease?', 'body_health', true, true),
    (evening_theme_id, 'evening', 'What simple physical ability served you well today?', 'What allows you to have that ability?', 'body_health', true, true),
    (evening_theme_id, 'evening', 'What did you eat or drink today that you genuinely enjoyed?', 'What made that possible for you?', 'body_health', true, true),
    (evening_theme_id, 'evening', 'When did you feel energized today?', 'What do you think gave you that energy?', 'body_health', true, true),
    (evening_theme_id, 'evening', 'What moment of physical comfort did you experience today?', 'What allowed that comfort?', 'body_health', true, true);

    -- ANGLE 4: almost_wrong (6 prompts)
    -- Something that almost went wrong but didn't
    INSERT INTO public.prompts (theme_id, beat, body, causation_prompt, angle, is_free, is_active) VALUES
    (evening_theme_id, 'evening', 'What almost went wrong today but didn''t?', 'What prevented it from going badly?', 'almost_wrong', true, true),
    (evening_theme_id, 'evening', 'What problem did you avoid today?', 'What helped you avoid it?', 'almost_wrong', true, true),
    (evening_theme_id, 'evening', 'What situation turned out better than you feared?', 'What made the difference?', 'almost_wrong', true, true),
    (evening_theme_id, 'evening', 'What difficulty did you navigate without it becoming worse?', 'What was your part in handling it?', 'almost_wrong', true, true),
    (evening_theme_id, 'evening', 'What stressful thing resolved more easily than expected?', 'What contributed to that resolution?', 'almost_wrong', true, true),
    (evening_theme_id, 'evening', 'What worked out despite your worries?', 'Looking back, what helped it work out?', 'almost_wrong', true, true);

    -- ANGLE 5: looking_forward (6 prompts)
    -- Something you're looking forward to
    INSERT INTO public.prompts (theme_id, beat, body, causation_prompt, angle, is_free, is_active) VALUES
    (evening_theme_id, 'evening', 'What are you looking forward to tomorrow?', 'What makes that possible for you?', 'looking_forward', true, true),
    (evening_theme_id, 'evening', 'What upcoming moment gives you a small sense of anticipation?', 'What in your life allows that to happen?', 'looking_forward', true, true),
    (evening_theme_id, 'evening', 'What simple thing tomorrow do you expect to enjoy?', 'What makes that likely?', 'looking_forward', true, true),
    (evening_theme_id, 'evening', 'What plan do you have that you''re glad about?', 'What enabled you to make that plan?', 'looking_forward', true, true),
    (evening_theme_id, 'evening', 'What''s one thing on the horizon that feels promising?', 'What''s creating that possibility?', 'looking_forward', true, true),
    (evening_theme_id, 'evening', 'What rest or renewal are you looking forward to?', 'What allows you to have that time?', 'looking_forward', true, true);

    -- ANGLE 6: ordinary_miss (7 prompts)
    -- Ordinary things you'd miss if they were gone
    INSERT INTO public.prompts (theme_id, beat, body, causation_prompt, angle, is_free, is_active) VALUES
    (evening_theme_id, 'evening', 'What ordinary thing today would you miss if it were gone?', 'What allows you to have that in your life?', 'ordinary_miss', true, true),
    (evening_theme_id, 'evening', 'What everyday comfort did you rely on today?', 'What makes that comfort available to you?', 'ordinary_miss', true, true),
    (evening_theme_id, 'evening', 'What routine brought you a quiet sense of stability today?', 'What supports that routine?', 'ordinary_miss', true, true),
    (evening_theme_id, 'evening', 'What do you take for granted that actually served you today?', 'What keeps that working in your life?', 'ordinary_miss', true, true),
    (evening_theme_id, 'evening', 'What background thing in your life made today possible?', 'What maintains that for you?', 'ordinary_miss', true, true),
    (evening_theme_id, 'evening', 'What reliable thing showed up again today?', 'What makes it reliable?', 'ordinary_miss', true, true),
    (evening_theme_id, 'evening', 'What part of your daily life are you quietly glad exists?', 'What allows that to be part of your life?', 'ordinary_miss', true, true);

END $$;
