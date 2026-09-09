import React from 'react';

export const metadata = {
  title: 'Afrosite — AI Company Builder',
  description: 'La plateforme AI-native pour les PME africaines',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  );
}
