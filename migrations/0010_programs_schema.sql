-- Migration: Programs System
-- Per PROGRAMS_SYSTEM_SPEC.md: guided multi-week arcs with 3 phases

-- Programs (the main container)
CREATE TABLE IF NOT EXISTS public.programs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    subtitle TEXT,
    theme TEXT,  -- e.g. "values", "self_compassion"
    duration_days INT NOT NULL DEFAULT 14,
    access TEXT NOT NULL DEFAULT 'premium' CHECK (access IN ('free', 'premium')),
    is_rerunnable BOOLEAN DEFAULT true,
    intro_copy TEXT,  -- warm framing shown before starting
    disclaimer_copy TEXT,  -- optional "this isn't therapy" note
    completion_copy TEXT,  -- closing consolidation
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Program Phases (3 per program: Surface, Notice, Deepen)
CREATE TABLE IF NOT EXISTS public.program_phases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    program_id UUID NOT NULL REFERENCES public.programs(id) ON DELETE CASCADE,
    phase_number INT NOT NULL CHECK (phase_number IN (1, 2, 3)),
    title TEXT NOT NULL,  -- e.g. "Noticing the critic"
    teaching_copy TEXT,  -- few sentences framing this movement
    start_day INT NOT NULL,
    end_day INT NOT NULL,
    UNIQUE(program_id, phase_number)
);

-- Program Days (content for each day)
CREATE TABLE IF NOT EXISTS public.program_days (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    program_id UUID NOT NULL REFERENCES public.programs(id) ON DELETE CASCADE,
    day_number INT NOT NULL,
    phase_number INT NOT NULL,  -- which phase this day is in
    morning_prompt TEXT NOT NULL,  -- themed values-reflection prompt
    morning_question TEXT NOT NULL,  -- the reflective question
    evening_prompt TEXT NOT NULL,  -- themed gratitude/reflection prompt
    evening_question TEXT NOT NULL,  -- incl. causal "because" step
    micro_teaching TEXT,  -- optional one-line insight
    UNIQUE(program_id, day_number)
);

-- User Programs (enrollment & progress)
CREATE TABLE IF NOT EXISTS public.user_programs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    program_id UUID NOT NULL REFERENCES public.programs(id),
    current_day INT NOT NULL DEFAULT 1,
    started_at TIMESTAMPTZ DEFAULT now(),
    last_activity_at TIMESTAMPTZ DEFAULT now(),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'completed', 'abandoned')),
    run_count INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_user_programs_user ON public.user_programs(user_id, status);
CREATE INDEX IF NOT EXISTS idx_user_programs_active ON public.user_programs(user_id) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_program_days_lookup ON public.program_days(program_id, day_number);
CREATE INDEX IF NOT EXISTS idx_program_phases_lookup ON public.program_phases(program_id, phase_number);
