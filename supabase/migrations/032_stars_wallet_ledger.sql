-- 032_stars_wallet_ledger.sql
-- MVP Monetization Foundation: Wallets, Transaction Ledger, and Entitlements.
-- All balance mutations and purchases are server-owned, atomic, and idempotent.

-- 1. Wallets (current balance per user)
CREATE TABLE IF NOT EXISTS public.wallets (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    balance INTEGER NOT NULL DEFAULT 0 CHECK (balance >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

ALTER TABLE public.wallets ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.wallets FROM public, anon, authenticated;
GRANT SELECT ON public.wallets TO authenticated;
GRANT ALL ON public.wallets TO service_role;

DROP POLICY IF EXISTS wallets_select_own ON public.wallets;
CREATE POLICY wallets_select_own ON public.wallets
    FOR SELECT TO authenticated
    USING (auth.uid() = user_id);

-- 2. Wallet Transaction Ledger (immutable audit trail of all grants and expenditures)
CREATE TABLE IF NOT EXISTS public.wallet_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL CHECK (amount <> 0),
    balance_after INTEGER NOT NULL CHECK (balance_after >= 0),
    transaction_type TEXT NOT NULL,
    reference_id TEXT,
    description_ka TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_wallet_transactions_user_order 
    ON public.wallet_transactions (user_id, created_at DESC, id DESC);

CREATE UNIQUE INDEX IF NOT EXISTS idx_wallet_tx_idempotent_ref
    ON public.wallet_transactions (user_id, transaction_type, reference_id)
    WHERE reference_id IS NOT NULL;

ALTER TABLE public.wallet_transactions ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.wallet_transactions FROM public, anon, authenticated;
GRANT SELECT ON public.wallet_transactions TO authenticated;
GRANT ALL ON public.wallet_transactions TO service_role;

DROP POLICY IF EXISTS wallet_transactions_select_own ON public.wallet_transactions;
CREATE POLICY wallet_transactions_select_own ON public.wallet_transactions
    FOR SELECT TO authenticated
    USING (auth.uid() = user_id);

-- 3. Entitlements (unlocked features, weekly energy, personal insight layers)
CREATE TABLE IF NOT EXISTS public.entitlements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    item_type TEXT NOT NULL,
    item_key TEXT NOT NULL,
    unlocked_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    expires_at TIMESTAMPTZ,
    transaction_id UUID REFERENCES public.wallet_transactions(id) ON DELETE SET NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    CONSTRAINT uq_user_entitlement UNIQUE (user_id, item_type, item_key)
);

CREATE INDEX IF NOT EXISTS idx_entitlements_user_lookup
    ON public.entitlements (user_id, item_type, item_key);

ALTER TABLE public.entitlements ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.entitlements FROM public, anon, authenticated;
GRANT SELECT ON public.entitlements TO authenticated;
GRANT ALL ON public.entitlements TO service_role;

DROP POLICY IF EXISTS entitlements_select_own ON public.entitlements;
CREATE POLICY entitlements_select_own ON public.entitlements
    FOR SELECT TO authenticated
    USING (auth.uid() = user_id);

