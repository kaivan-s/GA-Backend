-- Migration: Seed 5 Programs with authored content
-- Per PROGRAM_CONTENT_ALL5.md

-- ============================================================================
-- PROGRAM 1: Reconnecting with what matters (FREE intro)
-- ============================================================================
INSERT INTO public.programs (slug, title, subtitle, theme, duration_days, access, is_rerunnable, intro_copy, completion_copy, sort_order)
VALUES (
    'reconnecting-values',
    'Reconnecting with what matters',
    'A 14-day journey into your core values',
    'values',
    14,
    'free',
    true,
    'Over the next two weeks, we''ll do something quietly powerful: reconnect you with the things you actually care about — and notice where they already live in your days. This isn''t about becoming someone new or repeating things you''re "supposed" to believe. It''s about remembering what''s already true for you, and letting that steady you. A few minutes, morning and evening. That''s all.',
    'Two weeks ago, these values might have felt like words. Now you''ve seen them show up in real moments of your own life — and maybe lived them a little more on purpose. That''s the whole practice: not chasing who you should be, but noticing who you already are when you''re at your best. It''s yours to keep. You can carry it into the open daily practice, or begin again whenever you''d like a fresh look.',
    1
) ON CONFLICT (slug) DO UPDATE SET
    intro_copy = EXCLUDED.intro_copy,
    completion_copy = EXCLUDED.completion_copy;

-- Phases for Program 1
DELETE FROM public.program_phases WHERE program_id = (SELECT id FROM public.programs WHERE slug = 'reconnecting-values');

INSERT INTO public.program_phases (program_id, phase_number, title, teaching_copy, start_day, end_day)
SELECT id, 1, 'Surface', 'This week we''re just noticing. Not choosing values because they sound good — finding the ones that are actually yours. A value isn''t a goal you haven''t reached or a trait you wish you had. It''s simply something you care about in how you live. There are no right answers here.', 1, 5
FROM public.programs WHERE slug = 'reconnecting-values';

INSERT INTO public.program_phases (program_id, phase_number, title, teaching_copy, start_day, end_day)
SELECT id, 2, 'Notice', 'Now that you''ve surfaced what matters to you, this week is about evidence — noticing where these values already appear in your actual life. You live them more than you think. We''re not adding anything; we''re helping you see what''s already there.', 6, 10
FROM public.programs WHERE slug = 'reconnecting-values';

INSERT INTO public.program_phases (program_id, phase_number, title, teaching_copy, start_day, end_day)
SELECT id, 3, 'Live', 'You''ve found your values and seen where they live. This final stretch is gentle action — not a dramatic change, just living what matters a little more *on purpose*, and noticing how that feels. Small and deliberate beats big and forced.', 11, 14
FROM public.programs WHERE slug = 'reconnecting-values';

-- Days for Program 1
DELETE FROM public.program_days WHERE program_id = (SELECT id FROM public.programs WHERE slug = 'reconnecting-values');

DO $$
DECLARE
    prog_id UUID;
BEGIN
    SELECT id INTO prog_id FROM public.programs WHERE slug = 'reconnecting-values';
    
    INSERT INTO public.program_days (program_id, day_number, phase_number, morning_prompt, morning_question, evening_prompt, evening_question) VALUES
    -- Phase 1: Surface (Days 1-5)
    (prog_id, 1, 1, 'Let''s begin simply.', 'What''s something you care about in how you treat other people? Name one thing.', 'Looking back on today.', 'What''s one good moment from today — and why did it matter to you?'),
    (prog_id, 2, 1, 'Beyond people, there''s how you want to be in the world.', 'What''s a quality you''d be a little sad to lose in yourself?', 'Small things count.', 'Name one thing that went okay today, and what made it possible.'),
    (prog_id, 3, 1, 'Think of someone you quietly admire.', 'What is it about how they live that you respect? That''s often a clue to your own values.', 'Noticing the good.', 'What''s one thing you''re glad happened today — and your part in it, if any?'),
    (prog_id, 4, 1, 'Values show up in what bothers us too.', 'What''s something that genuinely frustrates you about the world? What value sits underneath that frustration?', 'A good moment, however small.', 'What''s one thing from today you''d want to remember, and why?'),
    (prog_id, 5, 1, 'A gentle gathering.', 'From this week, which one value feels most *you* right now? Just name it.', 'Closing the week''s noticing.', 'What went well today, and what made it happen?'),
    
    -- Phase 2: Notice (Days 6-10)
    (prog_id, 6, 2, 'Yesterday, somewhere, a value of yours showed up.', 'Think back — when did something you care about guide a choice you made recently?', 'Gratitude, tied to what matters.', 'What''s one thing today you''re grateful for that connects to something you value?'),
    (prog_id, 7, 2, 'The small, unnoticed moments.', 'When did you act on a value this week without even thinking about it?', 'A moment that fit.', 'What happened today that felt true to who you want to be — and why?'),
    (prog_id, 8, 2, 'Values under pressure.', 'When was a recent moment you held onto something you care about even though it was a little hard?', 'Recognizing yourself.', 'What''s one good thing from today, and what does it say about what matters to you?'),
    (prog_id, 9, 2, 'In relationships.', 'How did one of your values show up in how you treated someone recently?', 'The quiet wins.', 'What went well today that you might have overlooked — and why did it happen?'),
    (prog_id, 10, 2, 'Gathering the evidence.', 'Looking at this week — where have you seen yourself living what you care about?', 'Closing the noticing.', 'One good moment from today, and your hand in it?'),
    
    -- Phase 3: Live (Days 11-14)
    (prog_id, 11, 3, 'A small, deliberate choice.', 'Today, how might you honor one of your values on purpose? Nothing big — just one small way.', 'Looking back on the choice.', 'Did you get to live a value today? What happened, and how did it feel?'),
    (prog_id, 12, 3, 'Values as a compass.', 'If you let one value guide your day today, which would you choose, and what might it change?', 'Gratitude for the day.', 'What''s one thing you''re grateful for today, and why did it happen?'),
    (prog_id, 13, 3, 'The person you''re becoming.', 'When you live your values, who do you become? Picture that person for a moment.', 'A moment of alignment.', 'What happened today that you''re glad about — and how did it connect to what matters to you?'),
    (prog_id, 14, 3, 'Two weeks in.', 'What''s one thing you understand about yourself now that you didn''t fully see two weeks ago?', 'Closing the journey.', 'Looking back on these two weeks — what are you most grateful you noticed?');
END $$;

-- ============================================================================
-- PROGRAM 2: Self-compassion (PREMIUM - HIGH sensitivity)
-- ============================================================================
INSERT INTO public.programs (slug, title, subtitle, theme, duration_days, access, is_rerunnable, intro_copy, disclaimer_copy, completion_copy, sort_order)
VALUES (
    'self-compassion',
    'Self-compassion',
    'Befriending yourself through difficulty',
    'self_compassion',
    14,
    'premium',
    true,
    'Most of us speak to ourselves in a voice we''d never use on someone we love. Over the next two weeks, we''ll gently work toward a kinder inner voice — not by forcing positivity, but by first noticing how you treat yourself, understanding where that comes from, and slowly practicing something warmer. Go slowly. Be patient with yourself here, especially.',
    'This is a gentle reflective practice, not therapy. It can help you relate to yourself more kindly — but if you''re carrying something heavy, please also reach out to a friend, a professional, or a support line. You deserve real support, not just an app.',
    'Learning to be kinder to yourself isn''t a two-week fix — it''s a lifelong relationship. But you''ve done something real: you''ve noticed the voice, seen that you''re not alone in it, and practiced a gentler response. That''s the beginning of a genuine shift. Be patient with the days you slip back into the old voice — noticing is already the practice working. This is here whenever you need to return to it.',
    2
) ON CONFLICT (slug) DO UPDATE SET
    intro_copy = EXCLUDED.intro_copy,
    disclaimer_copy = EXCLUDED.disclaimer_copy,
    completion_copy = EXCLUDED.completion_copy;

-- Phases for Program 2
DELETE FROM public.program_phases WHERE program_id = (SELECT id FROM public.programs WHERE slug = 'self-compassion');

INSERT INTO public.program_phases (program_id, phase_number, title, teaching_copy, start_day, end_day)
SELECT id, 1, 'Notice', 'This week, we only notice — we don''t change anything yet. Awareness has to come before kindness. We''re going to gently observe how you talk to yourself, especially when things go wrong. No judging the judging. Just seeing it.', 1, 5
FROM public.programs WHERE slug = 'self-compassion';

INSERT INTO public.program_phases (program_id, phase_number, title, teaching_copy, start_day, end_day)
SELECT id, 2, 'Understand', 'This week adds understanding. That critical voice usually started as an attempt to protect you or keep you safe — it''s not your enemy, even when it''s unkind. And crucially: *everyone* has this voice. Struggling doesn''t make you broken or alone; it makes you human. That recognition is the heart of self-compassion.', 6, 10
FROM public.programs WHERE slug = 'self-compassion';

INSERT INTO public.program_phases (program_id, phase_number, title, teaching_copy, start_day, end_day)
SELECT id, 3, 'Respond', 'Now we practice responding differently. Not fake positivity — a realistic, warm voice, the kind you''d offer a good friend. This is a skill, and it feels awkward at first. That''s fine. You''re learning a new way to be with yourself.', 11, 14
FROM public.programs WHERE slug = 'self-compassion';

-- Days for Program 2
DELETE FROM public.program_days WHERE program_id = (SELECT id FROM public.programs WHERE slug = 'self-compassion');

DO $$
DECLARE
    prog_id UUID;
BEGIN
    SELECT id INTO prog_id FROM public.programs WHERE slug = 'self-compassion';
    
    INSERT INTO public.program_days (program_id, day_number, phase_number, morning_prompt, morning_question, evening_prompt, evening_question) VALUES
    -- Phase 1: Notice (Days 1-5)
    (prog_id, 1, 1, 'We begin by listening.', 'What''s something you''ve said to yourself recently when you made a mistake? Just notice the words, without judging them.', 'A softer close.', 'What''s one small thing that went okay today? Let yourself simply have it.'),
    (prog_id, 2, 1, 'The tone beneath the words.', 'When you''re hard on yourself, what tone does that inner voice use? Whose voice does it sometimes sound like?', 'Something to be glad about.', 'What''s one good moment from today, and what made it possible?'),
    (prog_id, 3, 1, 'Noticing the trigger.', 'What kinds of moments tend to switch on your harshest self-talk?', 'A gentle noticing.', 'Was there a moment today you were even slightly kind to yourself? What was it?'),
    (prog_id, 4, 1, 'The double standard.', 'Think of something you criticize yourself for. Would you say those same words to a friend in the same situation?', 'Closing softly.', 'What''s one thing from today you''re grateful for, and why?'),
    (prog_id, 5, 1, 'Gathering the week.', 'What have you noticed about how you treat yourself? Just name what you''ve seen.', 'A kind ending.', 'What went okay today that you can let yourself feel good about?'),
    
    -- Phase 2: Understand (Days 6-10)
    (prog_id, 6, 2, 'The critic''s intention.', 'Your inner critic might be trying to protect you in some clumsy way. What might it be afraid would happen if it went quiet?', 'Common humanity.', 'Whatever you struggled with today — remember others struggle with it too. What''s one thing you''re grateful for tonight?'),
    (prog_id, 7, 2, 'You are not alone in this.', 'The thing you''re hardest on yourself about — can you imagine how many other people quietly carry the same thing?', 'A shared human moment.', 'What''s one good thing from today, and what made it happen?'),
    (prog_id, 8, 2, 'Where it began.', 'When did you first learn to be this hard on yourself? You don''t have to fix it — just notice it with some tenderness.', 'Gentleness at day''s end.', 'What''s one thing today you can genuinely appreciate, however small?'),
    (prog_id, 9, 2, 'Imperfection is the norm.', 'What''s something you expect yourself to do perfectly that no human actually does perfectly?', 'Being human, together.', 'What went well today — and can you let it count, even if the day wasn''t perfect?'),
    (prog_id, 10, 2, 'Understanding, gathered.', 'What do you understand now about your inner critic that you didn''t a week ago?', 'A soft close.', 'One thing you''re grateful for today, and why it mattered?'),
    
    -- Phase 3: Respond (Days 11-14)
    (prog_id, 11, 3, 'The friend''s voice.', 'Think of something you''re struggling with. What would you say to a friend facing exactly this? Try offering those words to yourself.', 'A kinder reflection.', 'Was there a moment today you could have been kinder to yourself? What would that have sounded like?'),
    (prog_id, 12, 3, 'A hand on your own shoulder.', 'What do you most need to hear today? Can you say it to yourself, gently?', 'Gratitude for yourself.', 'What''s one thing *you* did today that you can appreciate, even a little?'),
    (prog_id, 13, 3, 'Kindness in hard moments.', 'Next time you slip or fail today, how might you respond with warmth instead of criticism?', 'Noticing the shift.', 'Did you speak to yourself a little more kindly today? What did you notice?'),
    (prog_id, 14, 3, 'Two weeks of practice.', 'What''s changed, even slightly, in how you treat yourself?', 'Closing with care.', 'What are you most grateful you gave yourself over these two weeks?');
END $$;

-- ============================================================================
-- PROGRAM 3: Self-belief, the honest way (PREMIUM - medium sensitivity)
-- ============================================================================
INSERT INTO public.programs (slug, title, subtitle, theme, duration_days, access, is_rerunnable, intro_copy, disclaimer_copy, completion_copy, sort_order)
VALUES (
    'self-belief',
    'Self-belief, the honest way',
    'Building confidence through evidence, not affirmation',
    'self_belief',
    14,
    'premium',
    true,
    'Real confidence isn''t repeating "I am amazing" until you believe it — that rarely works, and often backfires. It''s something quieter and sturdier: knowing what you value, seeing real evidence of who you are, and treating yourself fairly. Over two weeks, we''ll build self-belief the honest way — from the ground up, out of things that are actually true about you.',
    'This is a reflective practice for building a steadier sense of yourself over time. It''s not a quick fix or a replacement for support if you''re struggling with your self-worth — be gentle with yourself, and reach out to people who care about you.',
    'The steadiest kind of self-belief isn''t loud. It''s the quiet knowledge that you know what matters to you, you''ve seen real evidence of your own worth, and you can meet yourself fairly. You''ve spent two weeks gathering that — not inventing it, *noticing* it. It was always there. Carry it forward, and return whenever you need reminding.',
    3
) ON CONFLICT (slug) DO UPDATE SET
    intro_copy = EXCLUDED.intro_copy,
    disclaimer_copy = EXCLUDED.disclaimer_copy,
    completion_copy = EXCLUDED.completion_copy;

-- Phases for Program 3
DELETE FROM public.program_phases WHERE program_id = (SELECT id FROM public.programs WHERE slug = 'self-belief');

INSERT INTO public.program_phases (program_id, phase_number, title, teaching_copy, start_day, end_day)
SELECT id, 1, 'Surface', 'We start not with "what are you good at" but "what do you care about." Confidence built on values is sturdier than confidence built on achievements, because values can''t be taken from you. This week we surface the ground you''ll stand on.', 1, 5
FROM public.programs WHERE slug = 'self-belief';

INSERT INTO public.program_phases (program_id, phase_number, title, teaching_copy, start_day, end_day)
SELECT id, 2, 'Evidence', 'This week, we gather evidence. Not "I am confident" (a claim), but "here''s a time I handled something hard" (a fact). Facts are sturdier than affirmations because you can''t argue with what actually happened. We''re building a case for yourself out of real moments.', 6, 10
FROM public.programs WHERE slug = 'self-belief';

INSERT INTO public.program_phases (program_id, phase_number, title, teaching_copy, start_day, end_day)
SELECT id, 3, 'Internalize', 'Now we let the evidence settle into a steadier sense of self. This isn''t about feeling invincible — it''s about meeting yourself fairly, holding both your strengths and your limits without harshness. That balance *is* real confidence.', 11, 14
FROM public.programs WHERE slug = 'self-belief';

-- Days for Program 3
DELETE FROM public.program_days WHERE program_id = (SELECT id FROM public.programs WHERE slug = 'self-belief');

DO $$
DECLARE
    prog_id UUID;
BEGIN
    SELECT id INTO prog_id FROM public.programs WHERE slug = 'self-belief';
    
    INSERT INTO public.program_days (program_id, day_number, phase_number, morning_prompt, morning_question, evening_prompt, evening_question) VALUES
    -- Phase 1: Surface (Days 1-5)
    (prog_id, 1, 1, 'Beginning honestly.', 'What''s something you genuinely care about being — kind, honest, dependable? Name one.', 'A true moment.', 'What''s one thing today that went well, and what does it show about you?'),
    (prog_id, 2, 1, 'Quiet strengths.', 'What''s something you do well that you tend to dismiss or take for granted?', 'Evidence, gently.', 'What went okay today because of something *you* brought to it?'),
    (prog_id, 3, 1, 'What others rely on you for.', 'What do people in your life come to you for? That''s a real strength, whether or not you notice it.', 'A small proof.', 'What''s one good moment today, and your part in making it happen?'),
    (prog_id, 4, 1, 'Values as foundation.', 'What''s one value you can stand on no matter what happens today?', 'Grateful for your own effort.', 'What did you put effort into today, regardless of the outcome?'),
    (prog_id, 5, 1, 'The ground beneath you.', 'From this week — what''s one thing about yourself you can genuinely stand behind?', 'Closing the week.', 'What went well today, and why?'),
    
    -- Phase 2: Evidence (Days 6-10)
    (prog_id, 6, 2, 'A time you handled it.', 'Think of a hard thing you got through. What did you actually do? Give yourself the credit.', 'Today''s evidence.', 'What''s one thing today that proves you''re more capable than you sometimes feel?'),
    (prog_id, 7, 2, 'Growth you can measure.', 'What''s something you can do now that you couldn''t a few years ago?', 'A capable moment.', 'When did you handle something today, even a small thing, and how?'),
    (prog_id, 8, 2, 'Others'' trust as data.', 'Who trusts you, and what does their trust tell you about who you are?', 'Proof in the ordinary.', 'What went right today that you can take some quiet credit for?'),
    (prog_id, 9, 2, 'Surviving the hard days.', 'You''ve gotten through every hard day so far. What does that track record tell you?', 'Grateful for your resilience.', 'What did you get through today, and what does that say about you?'),
    (prog_id, 10, 2, 'The case, gathered.', 'Looking at this week''s evidence — what''s becoming harder to deny about yourself?', 'Closing the evidence.', 'One thing today you''re glad you did, and why?'),
    
    -- Phase 3: Internalize (Days 11-14)
    (prog_id, 11, 3, 'Fair, not inflated.', 'Can you hold one strength and one limitation of yours at the same time, without either one winning? Try it.', 'A balanced day.', 'What''s one thing you did well today, and one thing you''re at peace with not doing perfectly?'),
    (prog_id, 12, 3, 'Standing on your values.', 'Whatever today brings, what value will you not abandon? That steadiness is yours.', 'Grateful and grounded.', 'What are you grateful for today that came from being yourself?'),
    (prog_id, 13, 3, 'Speaking to yourself fairly.', 'How would a fair, honest friend describe you? Can you hold that description as possibly true?', 'Seeing yourself clearly.', 'What did today show you about who you actually are?'),
    (prog_id, 14, 3, 'Two weeks of building.', 'What do you believe about yourself now that feels more solid than it did two weeks ago?', 'Closing with steadiness.', 'What are you most grateful you came to see about yourself?');
END $$;

-- ============================================================================
-- PROGRAM 4: Letting go (PREMIUM - HIGH sensitivity)
-- ============================================================================
INSERT INTO public.programs (slug, title, subtitle, theme, duration_days, access, is_rerunnable, intro_copy, disclaimer_copy, completion_copy, sort_order)
VALUES (
    'letting-go',
    'Letting go',
    'Working with worry and what you can''t control',
    'letting_go',
    14,
    'premium',
    true,
    'So much of our stress comes from gripping things we can''t control — outcomes, other people, the past, the future. Letting go isn''t giving up or pretending not to care. It''s loosening your grip on what was never yours to hold, so you can put your energy where it actually reaches. Over two weeks, we''ll practice that, gently.',
    'This is a gentle reflective practice for working with worry and the things we grip too tightly. It is not therapy or treatment for anxiety. If worry is overwhelming your days, please reach out to a professional — that''s a sign of strength, not failure. You don''t have to carry it alone.',
    'Letting go isn''t something you do once — it''s a practice you return to, because the mind loves to grip. But you''ve learned the essential move: noticing what you''re holding, seeing what''s actually yours to control, and gently releasing the rest. Some things will take many rounds to release. That''s okay. The practice is here whenever your hands get full again.',
    4
) ON CONFLICT (slug) DO UPDATE SET
    intro_copy = EXCLUDED.intro_copy,
    disclaimer_copy = EXCLUDED.disclaimer_copy,
    completion_copy = EXCLUDED.completion_copy;

-- Phases for Program 4
DELETE FROM public.program_phases WHERE program_id = (SELECT id FROM public.programs WHERE slug = 'letting-go');

INSERT INTO public.program_phases (program_id, phase_number, title, teaching_copy, start_day, end_day)
SELECT id, 1, 'Surface', 'This week we just notice what you''re carrying — the worries, the loops, the things you replay. We''re not releasing anything yet. Naming what you''re holding is the first, necessary step. Be gentle; some of these will be tender.', 1, 5
FROM public.programs WHERE slug = 'letting-go';

INSERT INTO public.program_phases (program_id, phase_number, title, teaching_copy, start_day, end_day)
SELECT id, 2, 'Discern', 'This week is the heart of it: sorting what you can control from what you can''t. So much suffering comes from trying to control the uncontrollable. This isn''t about not caring — it''s about aiming your care where it can actually do something. Naming the line brings real relief.', 6, 10
FROM public.programs WHERE slug = 'letting-go';

INSERT INTO public.program_phases (program_id, phase_number, title, teaching_copy, start_day, end_day)
SELECT id, 3, 'Release', 'Now we practice release — not forcing a feeling away (that never works), but loosening your grip and gently turning toward what''s in front of you. Letting go is less a single act than a direction you keep choosing. Some things release easily; some take many tries. Both are fine.', 11, 14
FROM public.programs WHERE slug = 'letting-go';

-- Days for Program 4
DELETE FROM public.program_days WHERE program_id = (SELECT id FROM public.programs WHERE slug = 'letting-go');

DO $$
DECLARE
    prog_id UUID;
BEGIN
    SELECT id INTO prog_id FROM public.programs WHERE slug = 'letting-go';
    
    INSERT INTO public.program_days (program_id, day_number, phase_number, morning_prompt, morning_question, evening_prompt, evening_question) VALUES
    -- Phase 1: Surface (Days 1-5)
    (prog_id, 1, 1, 'Setting down the bag for a moment.', 'What''s been occupying your mind lately? Just name one thing you''ve been carrying.', 'A moment of ease.', 'Was there a moment today you felt even slightly lighter? What was happening?'),
    (prog_id, 2, 1, 'The loops we replay.', 'Is there a thought or worry that keeps circling back? Name it without judging yourself for it.', 'Something good, still.', 'Even with what''s on your mind — what''s one good thing from today?'),
    (prog_id, 3, 1, 'Old weight.', 'Is there something from the past you''re still holding? Just acknowledge it''s there.', 'A grateful pause.', 'What''s one thing today you''re glad happened, and why?'),
    (prog_id, 4, 1, 'Future worries.', 'What future "what if" has been taking up space in your mind lately?', 'Present good.', 'What went okay today, right here in the actual present?'),
    (prog_id, 5, 1, 'What you''re carrying, named.', 'Looking at this week — what are the main things you''ve been holding? Just see them.', 'Closing gently.', 'What''s one thing you''re grateful for tonight?'),
    
    -- Phase 2: Discern (Days 6-10)
    (prog_id, 6, 2, 'The dividing line.', 'Take one worry. What part of it is actually in your control, and what part simply isn''t?', 'Where you did have a say.', 'What''s something today you *could* influence, and did? How did that feel?'),
    (prog_id, 7, 2, 'Other people.', 'Is there someone whose choices you''ve been trying to control? What would it feel like to let their choices be theirs?', 'Your own lane.', 'What went well today that came from focusing on your own actions?'),
    (prog_id, 8, 2, 'The unchangeable past.', 'Is there a past event you keep wishing were different? It''s not yours to change now — only to carry more gently.', 'Grateful for now.', 'What''s one thing in the present you''re grateful for tonight?'),
    (prog_id, 9, 2, 'Effort vs. outcome.', 'What''s something where you can control your effort but not the result? Can you let the result go?', 'Honoring your effort.', 'What did you put honest effort into today, regardless of how it turned out?'),
    (prog_id, 10, 2, 'The line, clearer now.', 'What''s one thing you can finally see is not yours to control?', 'Closing the week.', 'What''s one good thing from today, and what made it possible?'),
    
    -- Phase 3: Release (Days 11-14)
    (prog_id, 11, 3, 'Loosening the grip.', 'Take one thing you can''t control. What would it feel like to set it down, just for today?', 'Lighter, even slightly.', 'Did anything feel a little lighter today after letting it be? What was it?'),
    (prog_id, 12, 3, 'Turning toward.', 'If you weren''t holding that worry so tightly, where could your attention go instead today?', 'Present-moment gratitude.', 'What''s one thing right in front of you today that you''re grateful for?'),
    (prog_id, 13, 3, 'Release as a practice.', 'What''s something you may need to let go of again and again? Can you make peace with that being okay?', 'Noticing the space.', 'What did you make room for today by not gripping so hard?'),
    (prog_id, 14, 3, 'Two weeks of loosening.', 'What feels a little lighter to carry now than it did two weeks ago?', 'Closing with openness.', 'What are you most grateful you were able to set down?');
END $$;

-- ============================================================================
-- PROGRAM 5: Noticing the good (Savoring) (PREMIUM - low sensitivity)
-- ============================================================================
INSERT INTO public.programs (slug, title, subtitle, theme, duration_days, access, is_rerunnable, intro_copy, completion_copy, sort_order)
VALUES (
    'savoring-good',
    'Noticing the good',
    'Training attention toward what''s here',
    'savoring',
    14,
    'premium',
    true,
    'Gratitude is being thankful for the good. Savoring is something a little different — actually *being there* for it while it''s happening, letting it land fully instead of rushing past. Most good moments slip by half-noticed. Over two weeks, we''ll practice catching them, slowing them down, and letting them count. It''s a quiet skill that changes how rich your ordinary days feel.',
    'You''ve been practicing one of the most underrated skills there is: actually being present for the good parts of your life. Not just having good moments, but *inhabiting* them. The more you notice, the more there seems to be — that''s not magic, it''s attention. Keep catching those moments. They were always there; now you''re there for them too.',
    5
) ON CONFLICT (slug) DO UPDATE SET
    intro_copy = EXCLUDED.intro_copy,
    completion_copy = EXCLUDED.completion_copy;

-- Phases for Program 5
DELETE FROM public.program_phases WHERE program_id = (SELECT id FROM public.programs WHERE slug = 'savoring-good');

INSERT INTO public.program_phases (program_id, phase_number, title, teaching_copy, start_day, end_day)
SELECT id, 1, 'Surface', 'This week we wake up to how much good passes by unnoticed — the small pleasures we rush through, the fine moments we don''t quite register. We''re not adding good things to your life yet; we''re noticing how much is already there and slipping past.', 1, 5
FROM public.programs WHERE slug = 'savoring-good';

INSERT INTO public.program_phases (program_id, phase_number, title, teaching_copy, start_day, end_day)
SELECT id, 2, 'Savor', 'Now we deepen from noticing to savoring — actually staying in a good moment, stretching it, letting it fill you. When something good happens, the practice is to pause and be *all the way there* for a few seconds. That pause is the whole skill.', 6, 10
FROM public.programs WHERE slug = 'savoring-good';

INSERT INTO public.program_phases (program_id, phase_number, title, teaching_copy, start_day, end_day)
SELECT id, 3, 'Deepen', 'This last stretch turns savoring from an exercise into a way of moving through your days — a lens you carry. The goal isn''t to savor everything (impossible), but to have the *option* always available, so ordinary life feels a little fuller. You''re building a habit of attention.', 11, 14
FROM public.programs WHERE slug = 'savoring-good';

-- Days for Program 5
DELETE FROM public.program_days WHERE program_id = (SELECT id FROM public.programs WHERE slug = 'savoring-good');

DO $$
DECLARE
    prog_id UUID;
BEGIN
    SELECT id INTO prog_id FROM public.programs WHERE slug = 'savoring-good';
    
    INSERT INTO public.program_days (program_id, day_number, phase_number, morning_prompt, morning_question, evening_prompt, evening_question) VALUES
    -- Phase 1: Surface (Days 1-5)
    (prog_id, 1, 1, 'A small anticipation.', 'What''s one small thing today you could genuinely look forward to, if you let yourself?', 'One caught moment.', 'What''s one good moment from today you might normally have rushed past?'),
    (prog_id, 2, 1, 'Everyday pleasures.', 'What''s an ordinary small pleasure — coffee, warmth, a song — you tend to have without really noticing?', 'Slowing it down.', 'Describe one good moment from today in a little detail. What did it actually feel like?'),
    (prog_id, 3, 1, 'The senses.', 'What''s something you could really notice with your senses today — a taste, a sound, the light?', 'A moment inhabited.', 'What''s one thing today you managed to be fully present for?'),
    (prog_id, 4, 1, 'The good you overlook.', 'What good thing is so regular in your life you''ve stopped seeing it?', 'Catching it in time.', 'What good moment today did you actually notice *while* it was happening?'),
    (prog_id, 5, 1, 'Awake to the good.', 'What''s one kind of good moment you want to get better at noticing?', 'Closing the week.', 'What''s the best small moment you caught today?'),
    
    -- Phase 2: Savor (Days 6-10)
    (prog_id, 6, 2, 'The pause.', 'Today, when something good happens, can you pause for three seconds and just be in it? Set that intention now.', 'A savored moment.', 'What moment today did you pause and fully take in? What was it like?'),
    (prog_id, 7, 2, 'Stretching it out.', 'What''s a good moment you tend to end too quickly? How could you let it last a little longer today?', 'Fully there.', 'When were you most present today, and what were you present *for*?'),
    (prog_id, 8, 2, 'Sharing amplifies.', 'Good moments grow when shared. Is there a small good thing you could share with someone today?', 'A shared or savored good.', 'What good moment today did you let yourself really enjoy?'),
    (prog_id, 9, 2, 'Savoring the ordinary.', 'What completely ordinary moment today could you treat as quietly precious?', 'The richness of small things.', 'What small thing today felt richer because you paid attention to it?'),
    (prog_id, 10, 2, 'Savoring, gathered.', 'What have you learned this week about being present for good moments?', 'Closing the savoring.', 'What''s one moment today you''re glad you didn''t rush past?'),
    
    -- Phase 3: Deepen (Days 11-14)
    (prog_id, 11, 3, 'A lens for the day.', 'What if today you looked for good moments the way you''d look for something you''d lost? What might you find?', 'What the lens caught.', 'Because you were looking, what good did you notice today that you''d otherwise have missed?'),
    (prog_id, 12, 3, 'Savoring memory.', 'What''s a good moment from your past you could revisit and savor for a few seconds right now?', 'Grateful and present.', 'What are you grateful you noticed today, and why did it matter?'),
    (prog_id, 13, 3, 'The abundance shift.', 'Have you noticed more good lately — or just noticed it more? What''s that like?', 'A fuller day.', 'How did paying attention change your day today?'),
    (prog_id, 14, 3, 'Two weeks of noticing.', 'How has your sense of your ordinary days changed over these two weeks?', 'Closing with fullness.', 'What''s the moment from these two weeks you''re most glad you were fully there for?');
END $$;
