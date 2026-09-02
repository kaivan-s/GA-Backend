-- Migration: Research-based gratitude enhancements
-- Adds causation prompts and angles per GRATITUDE_RESEARCH_BRIEF.md

-- Add causation_prompt to prompts (the "why did this happen?" follow-up)
ALTER TABLE public.prompts 
ADD COLUMN IF NOT EXISTS causation_prompt TEXT;

-- Add angle category for evening prompts (for rotation variety)
ALTER TABLE public.prompts 
ADD COLUMN IF NOT EXISTS angle TEXT CHECK (angle IN (
    'small_moment',      -- small thing that went right
    'person',            -- someone who helped/showed up
    'body_health',       -- something your body let you do
    'almost_wrong',      -- something that almost went wrong but didn't
    'looking_forward',   -- something you're looking forward to
    'ordinary_miss'      -- ordinary thing you'd miss if gone
));

-- Add causation_text to journal entries (user's "why" response)
ALTER TABLE public.journal_entries 
ADD COLUMN IF NOT EXISTS causation_text TEXT;

-- Create index for angle-based rotation
CREATE INDEX IF NOT EXISTS idx_prompts_angle ON public.prompts(beat, angle, is_active);

-- Update existing evening prompts to have default causation prompt
UPDATE public.prompts 
SET causation_prompt = 'What made this possible?'
WHERE beat = 'evening' AND causation_prompt IS NULL;
