-- Migration 021: Compatibility Evidence Trace
-- Adds dedicated JSONB evidence_trace column for auditability and explainability.

alter table public.compatibility_results
  add column if not exists evidence_trace jsonb not null default '[]'::jsonb;
