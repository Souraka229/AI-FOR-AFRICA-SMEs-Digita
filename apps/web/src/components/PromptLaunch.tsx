'use client';

import { FormEvent, useState } from 'react';
import { Button, Input } from '@afrosite/design-system';

const DEMO = 'boutique de tissus wax a Cadjehoun, livraison quartier, paiement Mobile Money';

export function PromptLaunch() {
  const [value, setValue] = useState(DEMO);

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
  }

  return (
    <form className="landing__prompt" onSubmit={onSubmit}>
      <Input
        aria-label="Description de l activite"
        value={value}
        onChange={(event) => setValue(event.target.value)}
      />
      <div className="landing__actions">
        <Button type="submit">Lancer le blueprint Commerce</Button>
        <Button type="button" variant="ghost" onClick={() => setValue(DEMO)}>
          Reprendre l exemple
        </Button>
      </div>
    </form>
  );
}
