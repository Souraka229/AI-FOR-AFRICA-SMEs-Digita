import Link from "next/link";
import { BrandMark } from "@/components/brand-mark";
import { ThemeToggle } from "@/components/theme-toggle";

export function AppNav({
  current,
  tenantSlug = "cadjehoun-wax",
}: {
  current?: "studio" | "boutique" | "caisse";
  tenantSlug?: string;
}) {
  const links = [
    { href: "/studio", id: "studio" as const, label: "Studio" },
    { href: `/t/${tenantSlug}`, id: "boutique" as const, label: "Boutique" },
    { href: `/dashboard/${tenantSlug}`, id: "caisse" as const, label: "Caisse" },
  ];

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/85 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-6xl items-center gap-4 px-4">
        <Link href="/" className="flex items-center gap-2 font-heading text-base font-semibold">
          <BrandMark className="size-6" />
          afrosite
        </Link>
        <nav className="flex items-center gap-1 text-sm">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`rounded-md px-3 py-1.5 ${
                current === link.id
                  ? "bg-muted font-medium text-foreground"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </nav>
        <div className="ml-auto">
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
