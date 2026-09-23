type OrderState = 'received' | 'preparing' | 'ready' | 'urgent';

const LABELS: Record<OrderState, string> = {
  received: 'Recue',
  preparing: 'En preparation',
  ready: 'Prete',
  urgent: 'Urgente',
};

type OrderStatusProps = {
  status: OrderState;
  className?: string;
};

export function OrderStatus({ status, className = '' }: OrderStatusProps) {
  const tone = status === 'urgent' ? 'urgent' : 'pending';
  return (
    <span className={['as-status', `as-status--${tone}`, className].filter(Boolean).join(' ')}>
      {LABELS[status]}
    </span>
  );
}
