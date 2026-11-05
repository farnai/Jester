-- Migration 033: Database Environment Metadata & Environment Fingerprinting
CREATE TABLE IF NOT EXISTS public.database_environment_meta (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    environment TEXT NOT NULL CHECK (environment IN ('development', 'test', 'staging', 'production')),
    cluster_fingerprint UUID NOT NULL,
    is_destructive_testing_allowed BOOLEAN NOT NULL DEFAULT false,
    initialized_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- RLS: Read-only for authenticated and anon, service_role can update
ALTER TABLE public.database_environment_meta ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access to environment meta"
    ON public.database_environment_meta
    FOR SELECT
    USING (true);

-- Stamp default as development (safe default: non-destructive)
INSERT INTO public.database_environment_meta (environment, cluster_fingerprint, is_destructive_testing_allowed, metadata)
SELECT 'development', gen_random_uuid(), false, '{"description": "JESTER Primary Local Development Environment", "stack": "Jester"}'::jsonb
WHERE NOT EXISTS (SELECT 1 FROM public.database_environment_meta);

