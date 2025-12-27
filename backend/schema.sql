-- Sub-Zero Database Schema
-- Supabase-compatible PostgreSQL schema
-- Users are handled by Supabase Auth (auth.users table)

-- Bank connections via Plaid
CREATE TABLE bank_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    plaid_access_token TEXT, -- Encrypted
    plaid_item_id TEXT,
    institution_name TEXT,
    connected_at TIMESTAMPTZ DEFAULT NOW()
);

-- Detected subscriptions
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    merchant_name TEXT NOT NULL,
    normalized_name TEXT,
    logo_url TEXT,
    monthly_price DECIMAL(10, 2),
    last_charge_date DATE,
    status TEXT DEFAULT 'active', -- active, cancelled, keeper, zombie
    cancellation_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Credential vault (encrypted blobs only)
CREATE TABLE credential_vault (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE CASCADE,
    encrypted_credentials BYTEA NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, subscription_id)
);

-- The Graveyard
CREATE TABLE graveyard (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id),
    service_name TEXT NOT NULL,
    monthly_savings DECIMAL(10, 2),
    cancelled_at TIMESTAMPTZ DEFAULT NOW(),
    proof_screenshot_url TEXT,
    proof_video_url TEXT,
    cancellation_method TEXT -- 'agent', 'manual', 'api'
);

-- Zombie alerts
CREATE TABLE zombie_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    graveyard_id UUID REFERENCES graveyard(id),
    detected_charge_amount DECIMAL(10, 2),
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    resolved BOOLEAN DEFAULT FALSE
);

-- Helper function for total savings
CREATE OR REPLACE FUNCTION get_total_savings(p_user_id UUID)
RETURNS DECIMAL AS $$
    SELECT COALESCE(SUM(monthly_savings * 12), 0)
    FROM graveyard
    WHERE user_id = p_user_id;
$$ LANGUAGE SQL;
