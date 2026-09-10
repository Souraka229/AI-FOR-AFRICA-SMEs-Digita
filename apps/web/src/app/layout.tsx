import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";
import { Space_Grotesk, IBM_Plex_Sans, IBM_Plex_Mono } from "next/font/google";
import { Providers } from "@/components/providers";
import "./globals.css";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  weight: ["500", "600", "700"],
  variable: "--font-space-grotesk",
  display: "swap",
});

const ibmPlexSans = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-ibm-plex-sans",
  display: "swap",
});

const ibmPlexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-ibm-plex-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Afrosite — vendez et encaissez, sans une ligne de code",
  description:
    "Décrivez votre activité. Repartez avec un outil pour vendre, prendre les commandes et encaisser en Mobile Money — en français, en FCFA. Commerces, restaurants et prestataires au Bénin.",
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? "https://afrosite.app"),
  openGraph: {
    type: "website",
    title: "Afrosite — vendez et encaissez, sans une ligne de code",
    description:
      "Catalogue, commandes, caisse et paiement Mobile Money. En français, en FCFA.",
    locale: "fr_FR",
  },
  alternates: { canonical: "/" },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#FBF4EC" },
    { media: "(prefers-color-scheme: dark)", color: "#16110E" },
  ],
};

export default function RootLayout({
  children,
}: Readonly<{ children: ReactNode }>) {
  return (
    <html
      lang="fr"
      suppressHydrationWarning
      className={`${spaceGrotesk.variable} ${ibmPlexSans.variable} ${ibmPlexMono.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col overflow-x-hidden">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
