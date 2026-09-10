-- Ledger Afrosite — playbook §10 / §14
-- source de vérité des événements ; status dénormalisé pour la caisse.
-- Devise : XOF. Jamais de PAN/CVV.

CREATE TABLE IF NOT EXISTS tenants (
  slug TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  vertical TEXT NOT NULL CHECK (vertical IN ('commerce', 'restaurant', 'services')),
  city TEXT NOT NULL DEFAULT 'Cotonou',
  neighborhood TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ledger_entries (
  id UUID PRIMARY KEY,
  reference TEXT NOT NULL UNIQUE,
  tenant_slug TEXT NOT NULL REFERENCES tenants (slug),
  amount_xof INTEGER NOT NULL CHECK (amount_xof >= 0),
  channel TEXT NOT NULL CHECK (channel IN ('mtn_momo', 'moov_money', 'cash')),
  status TEXT NOT NULL CHECK (
    status IN ('pending', 'confirmed', 'failed', 'expired', 'refunded')
  ),
  verified_server BOOLEAN NOT NULL DEFAULT false,
  idem_key TEXT,
  refunded_amount_xof INTEGER NOT NULL DEFAULT 0 CHECK (refunded_amount_xof >= 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  confirmed_at TIMESTAMPTZ
);

CREATE UNIQUE INDEX IF NOT EXISTS ledger_idem_key_uidx
  ON ledger_entries (idem_key)
  WHERE idem_key IS NOT NULL;

CREATE TABLE IF NOT EXISTS ledger_events (
  id UUID PRIMARY KEY,
  reference TEXT NOT NULL REFERENCES ledger_entries (reference),
  type TEXT NOT NULL CHECK (
    type IN ('created', 'verified', 'failed', 'expired', 'refunded')
  ),
  amount_xof INTEGER,
  reason TEXT,
  at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ledger_events_ref_idx ON ledger_events (reference, at);

CREATE TABLE IF NOT EXISTS whatsapp_messages (
  id UUID PRIMARY KEY,
  tenant_slug TEXT NOT NULL REFERENCES tenants (slug),
  audience TEXT NOT NULL CHECK (audience IN ('customer', 'owner')),
  body TEXT NOT NULL,
  payment_ref TEXT,
  at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS cost_events (
  id UUID PRIMARY KEY,
  tenant_slug TEXT NOT NULL REFERENCES tenants (slug),
  agent TEXT NOT NULL,
  action TEXT NOT NULL,
  credits INTEGER NOT NULL CHECK (credits >= 0),
  at TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO tenants (slug, name, vertical, neighborhood) VALUES
  ('cadjehoun-wax', 'Wax Cadjehoun', 'commerce', 'Cadjehoun'),
  ('maquis-fidjrosse', 'Maquis Fidjrossè', 'restaurant', 'Fidjrossè'),
  ('salon-awa-cadjehoun', 'Salon Awa Cadjehoun', 'services', 'Cadjehoun')
ON CONFLICT (slug) DO NOTHING;
