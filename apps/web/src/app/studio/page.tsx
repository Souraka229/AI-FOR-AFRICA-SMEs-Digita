import type { Metadata } from "next";
import { AppNav } from "@/components/app-nav";
import { StudioClient } from "./studio-client";

export const metadata: Metadata = {
  title: "Studio — Afrosite",
  description:
    "Plan, coût estimé et audit trail en direct. Accord explicite avant preview.",
  robots: { index: false, follow: false },
};

export default function StudioPage() {
  return (
    <>
      <AppNav current="studio" />
      <StudioClient />
    </>
  );
}
