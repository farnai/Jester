-- Migration 001: Extensions
-- Enables required cryptographic and UUID generation extensions

create extension if not exists pgcrypto;
create extension if not exists "uuid-ossp";
