export function BrandMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 48 48" aria-hidden="true" className={className}>
      <rect x="1.5" y="1.5" width="45" height="45" rx="11" className="fill-brand" />
      <path
        d="M24 12.5 L36.5 35.5 H29.2 L24 25 L18.8 35.5 H11.5 Z"
        className="fill-background"
      />
      <circle cx="24" cy="9" r="2.7" className="fill-gold" />
    </svg>
  );
}
