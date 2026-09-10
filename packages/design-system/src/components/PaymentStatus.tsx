type PaymentState = 'confirmed' | 'pending' | 'failed';

const LABELS: Record<PaymentState, string> = {
  confirmed: 'Paiement confirme',
  pending: 'En attente',
  failed: 'Echec',
};

type PaymentStatusProps = {
  status: PaymentState;
  className?: string;
};

export function PaymentStatus({ status, className = '' }: PaymentStatusProps) {
  return (
    <span className={['as-status', `as-status--${status}`, className].filter(Boolean).join(' ')}>
      {LABELS[status]}
    </span>
  );
}
