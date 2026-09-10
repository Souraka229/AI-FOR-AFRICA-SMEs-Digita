-- Catalogue + commandes — Phase 1 (feat/api-catalog, feat/api-orders)
-- Montants XOF uniquement. Prix jamais pris depuis le client à la commande.

CREATE TABLE IF NOT EXISTS catalog_items (
  tenant_slug TEXT NOT NULL REFERENCES tenants (slug),
  sku TEXT NOT NULL,
  name TEXT NOT NULL,
  price_xof INTEGER NOT NULL CHECK (price_xof >= 0),
  category TEXT NOT NULL,
  available BOOLEAN NOT NULL DEFAULT true,
  unit TEXT,
  PRIMARY KEY (tenant_slug, sku)
);

CREATE TABLE IF NOT EXISTS orders (
  id UUID PRIMARY KEY,
  tenant_slug TEXT NOT NULL REFERENCES tenants (slug),
  created_by TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('placed', 'cancelled')),
  amount_xof INTEGER NOT NULL CHECK (amount_xof > 0),
  currency TEXT NOT NULL DEFAULT 'XOF' CHECK (currency = 'XOF'),
  idem_key TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS orders_idem_uidx
  ON orders (tenant_slug, idem_key)
  WHERE idem_key IS NOT NULL;

CREATE TABLE IF NOT EXISTS order_lines (
  order_id UUID NOT NULL REFERENCES orders (id) ON DELETE CASCADE,
  sku TEXT NOT NULL,
  name TEXT NOT NULL,
  qty INTEGER NOT NULL CHECK (qty > 0),
  unit_price_xof INTEGER NOT NULL CHECK (unit_price_xof >= 0),
  line_total_xof INTEGER NOT NULL CHECK (line_total_xof >= 0)
);

INSERT INTO catalog_items (tenant_slug, sku, name, price_xof, category, available, unit) VALUES
  ('cadjehoun-wax', 'wax-cadjehoun-6y', 'Pagne wax 6 yards — motif Cadjehoun', 12500, 'tissus', true, 'pièce'),
  ('cadjehoun-wax', 'wax-fidjrosse-6y', 'Pagne wax 6 yards — motif Fidjrossè', 8000, 'tissus', true, 'pièce'),
  ('cadjehoun-wax', 'livraison-quartier', 'Livraison quartier', 4000, 'livraison', true, 'course'),
  ('maquis-fidjrosse', 'poisson-braise', 'Poisson braisé', 4500, 'grillades', true, NULL),
  ('maquis-fidjrosse', 'alloco-poulet', 'Poulet + alloco', 3500, 'grillades', true, NULL),
  ('maquis-fidjrosse', 'jus-bissap', 'Jus bissap', 500, 'boissons', true, NULL),
  ('salon-awa-cadjehoun', 'tresses-medium', 'Tresses moyennes', 8000, 'coiffure', true, NULL),
  ('salon-awa-cadjehoun', 'locking', 'Locking', 12000, 'coiffure', true, NULL),
  ('salon-awa-cadjehoun', 'soin-capillaire', 'Soin capillaire', 4000, 'soins', true, NULL)
ON CONFLICT (tenant_slug, sku) DO NOTHING;
