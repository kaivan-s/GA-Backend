-- RPC function: upsert_day_stat
-- Called after ritual completion to update daily progress

CREATE OR REPLACE FUNCTION public.upsert_day_stat(
    p_user_id UUID,
    p_local_date DATE,
    p_beat TEXT
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO public.day_stats (user_id, local_date, morning, evening)
    VALUES (
        p_user_id,
        p_local_date,
        p_beat = 'morning',
        p_beat = 'evening'
    )
    ON CONFLICT (user_id, local_date) DO UPDATE SET
        morning = CASE WHEN p_beat = 'morning' THEN true ELSE public.day_stats.morning END,
        evening = CASE WHEN p_beat = 'evening' THEN true ELSE public.day_stats.evening END;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- RLS: Enable row level security on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.themes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.prompts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.journeys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.journey_days ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.journey_day_prompts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_journeys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ritual_completions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.journal_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.day_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.entitlements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.devices ENABLE ROW LEVEL SECURITY;

-- Service role bypasses RLS (backend uses service role key)
-- No client-side policies needed since all access goes through the backend
