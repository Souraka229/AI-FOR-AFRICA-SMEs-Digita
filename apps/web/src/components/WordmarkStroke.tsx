'use client';

import { useCallback, useState, type MouseEvent } from 'react';

export function WordmarkStroke() {
  const [spot, setSpot] = useState({ x: 50, y: 50 });

  const onMove = useCallback((event: MouseEvent<HTMLDivElement>) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * 100;
    const y = ((event.clientY - rect.top) / rect.height) * 100;
    setSpot({ x, y });
  }, []);

  const fill = `radial-gradient(circle 9rem at ${spot.x}% ${spot.y}%, var(--spotlight) 0%, transparent 68%)`;

  return (
    <div className="wordmark" onMouseMove={onMove}>
      <p className="wordmark__layer wordmark__stroke" aria-hidden="true">
        afrosite
      </p>
      <p className="wordmark__layer wordmark__fill" style={{ backgroundImage: fill }} aria-hidden="true">
        afrosite
      </p>
    </div>
  );
}
