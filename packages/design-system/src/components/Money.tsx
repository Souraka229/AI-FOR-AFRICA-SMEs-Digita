type MoneyProps = {
  amountXof: number | string;
  className?: string;
};

function formatXof(amountXof: number | string): string {
  const value = typeof amountXof === 'string' ? Number(amountXof) : amountXof;
  const safe = Number.isFinite(value) ? value : 0;
  const grouped = new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 0 })
    .format(safe)
    .replace(/\u202f|\u00a0/g, ' ');
  return `${grouped} FCFA`;
}

export function Money({ amountXof, className = '' }: MoneyProps) {
  return <span className={['as-money', className].filter(Boolean).join(' ')}>{formatXof(amountXof)}</span>;
}
