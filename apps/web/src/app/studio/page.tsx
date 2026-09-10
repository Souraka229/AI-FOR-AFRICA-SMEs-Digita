import type { Metadata } from "next";
import { AppNav } from "@/components/app-nav";
import { StudioClient } from "./studio-client";

export const metadata: Metadata = {
  title: "Studio — Afrosite",
  description:
    "Prompt en français vers un Blueprint JSON validé. Intent Agent, Product Architect, Gate 1.",
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
