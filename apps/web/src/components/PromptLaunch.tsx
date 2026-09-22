"use client";

import { useRouter } from "next/navigation";
import { type FormEvent, useState } from "react";
import { Button, Input } from "@afrosite/design-system";

const DEMO = "boutique de tissus wax à Cadjehoun, livraison quartier, paiement Mobile Money";

export function PromptLaunch() {
  const router = useRouter();
  const [value, setValue] = useState(DEMO);

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const prompt = value.trim();
    if (!prompt) return;
    router.push(`/studio?prompt=${encodeURIComponent(prompt)}`);
  }

  return (
    <form className="landing__prompt" onSubmit={onSubmit}>
      <Input
        aria-label="Description de l'activité"
        value={value}
        onChange={(event) => setValue(event.target.value)}
      />
      <div className="landing__actions">
        <Button type="submit">Lancer le blueprint Commerce</Button>
        <Button type="button" variant="ghost" onClick={() => setValue(DEMO)}>
          Reprendre l&apos;exemple
        </Button>
      </div>
    </form>
  );
}
