'use client';

import { useCallback, useState, type MouseEvent } from 'react';

export function WordmarkStroke() {
  const [spot, setSpot] = useState({ x: 42, y: 50, active: false });

  const onMove = useCallback((event: MouseEvent<HTMLDivElement>) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * 100;
    const y = ((event.clientY - rect.top) / rect.height) * 100;
    setSpot({ x, y, active: true });
  }, []);

  const fill = `radial-gradient(circle 11rem at ${spot.x}% ${spot.y}%, var(--spotlight) 0%, transparent 70%)`;

  return (
    <div
      className={`wordmark${spot.active ? ' wordmark--lit' : ''}`}
      onMouseMove={onMove}
      onMouseLeave={() => setSpot((current) => ({ ...current, active: false }))}
      role="img"
      aria-label="afrosite"
    >
      <p className="wordmark__layer wordmark__stroke">afrosite</p>
      <p className="wordmark__layer wordmark__fill" style={{ backgroundImage: fill }}>
        afrosite
      </p>
    </div>
  );
}
