import { cn } from "@/lib/utils";
import { formatXof } from "@/lib/money";

/** Montant XOF — tokens heading + tabular. Vert interdit ici. */
export function Money({
  amountXof,
  className,
}: {
  amountXof: number;
  className?: string;
}) {
  return (
    <span className={cn("font-heading tabular-nums", className)}>
      {formatXof(amountXof)}
    </span>
  );
}
