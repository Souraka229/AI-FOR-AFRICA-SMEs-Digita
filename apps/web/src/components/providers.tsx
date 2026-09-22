"use client";

import { ThemeProvider } from "next-themes";
import type { ComponentType, ReactNode } from "react";
import { AuthProvider } from "@/components/auth-provider";

type ThemeProviderWithChildrenProps = {
  attribute?: "class";
  defaultTheme?: string;
  enableSystem?: boolean;
  disableTransitionOnChange?: boolean;
  children?: ReactNode;
};

// next-themes 0.4.6 omits children from its emitted type under React 19.
const ThemeProviderWithChildren = ThemeProvider as unknown as ComponentType<
  ThemeProviderWithChildrenProps
>;

export function Providers({ children }: { children: ReactNode }) {
  return (
    <ThemeProviderWithChildren
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <AuthProvider>{children}</AuthProvider>
    </ThemeProviderWithChildren>
  );
}
