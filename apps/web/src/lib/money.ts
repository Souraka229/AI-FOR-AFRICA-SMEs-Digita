export function formatXof(amount: number): string {
  return `${new Intl.NumberFormat("fr-BJ", {
    maximumFractionDigits: 0,
  }).format(amount)} FCFA`;
}
