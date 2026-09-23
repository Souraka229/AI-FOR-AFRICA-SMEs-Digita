"use client";

import dynamic from "next/dynamic";

const HeroMark3D = dynamic(
  () => import("@/components/HeroMark3D").then((module) => module.HeroMark3D),
  { ssr: false },
);

export function HeroMarkClient() {
  return <HeroMark3D />;
}
