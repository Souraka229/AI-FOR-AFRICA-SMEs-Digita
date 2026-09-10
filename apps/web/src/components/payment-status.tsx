import type { PaymentStatus as LedgerStatus } from "@/lib/demo/store";
import { cn } from "@/lib/utils";
import { Money } from "@/components/money";

const LABEL: Record<LedgerStatus, string> = {
  pending: "en attente",
  confirmed: "paiement confirmé",
  failed: "échec",
  expired: "expiré",
  refunded: "remboursé",
};

const TONE: Record<LedgerStatus, string> = {
  pending: "text-pending",
  confirmed: "text-confirmed",
  failed: "text-destructive",
  expired: "text-muted-foreground",
  refunded: "text-muted-foreground",
};

/** Vert uniquement si `confirmed`. */
export function PaymentStatus({
  status,
  refundedAmountXof = 0,
  className,
}: {
  status: LedgerStatus;
  refundedAmountXof?: number;
  className?: string;
}) {
  return (
    <span className={cn(TONE[status], className)}>
      {LABEL[status]}
      {status === "confirmed" && refundedAmountXof > 0 ? (
        <>
          {" · remboursé "}
          <Money amountXof={refundedAmountXof} />
        </>
      ) : null}
    </span>
  );
}
