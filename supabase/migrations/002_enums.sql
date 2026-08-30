-- Migration 002: Enums
-- Defines enumeration types for birth time precision, connection status, and conversation types

create type public.birth_time_precision as enum (
  'exact',
  'approximate',
  'unknown'
);

create type public.connection_status as enum (
  'pending',
  'accepted',
  'declined',
  'blocked',
  'removed'
);

create type public.conversation_type as enum (
  'direct'
);
