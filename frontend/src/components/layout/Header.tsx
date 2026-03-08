"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { cn } from "@/lib/utils";

const navLinks = [
  { href: "/pakketten", label: "Pakketten" },
  { href: "/organisaties", label: "Organisaties" },
  { href: "/standaarden", label: "Standaarden" },
];

function AuthButton() {
  const [mounted, setMounted] = useState(false);
  const { isAuthenticated, user, initialize } = useAuth();

  useEffect(() => {
    setMounted(true);
    initialize();
  }, [initialize]);

  if (!mounted) {
    return (
      <Link
        href="/login"
        className="rounded-md bg-primary-500 px-4 py-2 text-sm font-medium text-white hover:bg-primary-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2"
      >
        Inloggen
      </Link>
    );
  }

  return isAuthenticated ? (
    <Link
      href="/mijn-landschap"
      aria-label={`Dashboard: ingelogd als ${user?.naam || "gebruiker"}`}
      className="rounded-md bg-primary-500 px-4 py-2 text-sm font-medium text-white hover:bg-primary-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2"
    >
      {user?.naam || "Dashboard"}
    </Link>
  ) : (
    <Link
      href="/login"
      className="rounded-md bg-primary-500 px-4 py-2 text-sm font-medium text-white hover:bg-primary-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2"
    >
      Inloggen
    </Link>
  );
}

export function Header() {
  const pathname = usePathname();

  return (
    <header className="border-b border-gray-200 bg-white">
      <nav
        aria-label="Hoofdnavigatie"
        className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8"
      >
        <Link
          href="/"
          aria-label="Softwarecatalogus — Ga naar de startpagina"
          className="text-xl font-bold text-primary-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2"
        >
          Softwarecatalogus
        </Link>
        <div className="flex items-center gap-6">
          {navLinks.map(({ href, label }) => {
            const isActive =
              pathname === href || pathname.startsWith(href + "/");
            return (
              <Link
                key={href}
                href={href}
                aria-current={isActive ? "page" : undefined}
                className={cn(
                  "text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2",
                  isActive
                    ? "text-primary-600 underline underline-offset-4"
                    : "text-gray-700 hover:text-primary-500"
                )}
              >
                {label}
              </Link>
            );
          })}
          <AuthButton />
        </div>
      </nav>
    </header>
  );
}
