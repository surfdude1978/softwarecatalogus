"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/use-auth";

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
        className="rounded-md bg-primary-500 px-4 py-2 text-sm font-medium text-white hover:bg-primary-600"
      >
        Inloggen
      </Link>
    );
  }

  return isAuthenticated ? (
    <Link
      href="/mijn-landschap"
      className="rounded-md bg-primary-500 px-4 py-2 text-sm font-medium text-white hover:bg-primary-600"
    >
      {user?.naam || "Dashboard"}
    </Link>
  ) : (
    <Link
      href="/login"
      className="rounded-md bg-primary-500 px-4 py-2 text-sm font-medium text-white hover:bg-primary-600"
    >
      Inloggen
    </Link>
  );
}

export function Header() {
  return (
    <header className="border-b border-gray-200 bg-white">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <Link href="/" className="text-xl font-bold text-primary-500">
          Softwarecatalogus
        </Link>
        <div className="flex items-center gap-6">
          <Link
            href="/pakketten"
            className="text-sm font-medium text-gray-700 hover:text-primary-500"
          >
            Pakketten
          </Link>
          <Link
            href="/organisaties"
            className="text-sm font-medium text-gray-700 hover:text-primary-500"
          >
            Organisaties
          </Link>
          <Link
            href="/standaarden"
            className="text-sm font-medium text-gray-700 hover:text-primary-500"
          >
            Standaarden
          </Link>
          <AuthButton />
        </div>
      </nav>
    </header>
  );
}
