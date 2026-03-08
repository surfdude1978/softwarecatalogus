"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/mijn-landschap", label: "Mijn pakketlandschap", roles: ["gebruik_beheerder", "gebruik_raadpleger", "functioneel_beheerder"] },
  { href: "/aanbod", label: "Pakketaanbod beheren", roles: ["aanbod_beheerder", "functioneel_beheerder"] },
  { href: "/beheer/organisaties", label: "Organisatiebeheer", roles: ["functioneel_beheerder"] },
  { href: "/beheer/gemma", label: "GEMMA beheer", roles: ["functioneel_beheerder"] },
  { href: "/profiel", label: "Mijn profiel", roles: null },
];

export function DashboardNav() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const visibleItems = navItems.filter(
    (item) => item.roles === null || (user && item.roles.includes(user.rol))
  );

  return (
    <nav className="rounded-lg border border-gray-200 bg-white p-4">
      {user && (
        <div className="mb-4 border-b border-gray-100 pb-4">
          <p className="font-medium text-gray-900">{user.naam}</p>
          <p className="text-xs text-gray-500">{user.rol_display}</p>
          {user.organisatie_naam && (
            <p className="text-xs text-gray-500">{user.organisatie_naam}</p>
          )}
        </div>
      )}
      <ul className="space-y-1">
        {visibleItems.map((item) => (
          <li key={item.href}>
            <Link
              href={item.href}
              className={cn(
                "block rounded-md px-3 py-2 text-sm transition-colors",
                pathname === item.href
                  ? "bg-primary-50 font-medium text-primary-700"
                  : "text-gray-700 hover:bg-gray-50"
              )}
            >
              {item.label}
            </Link>
          </li>
        ))}
      </ul>
      <button
        onClick={() => logout()}
        className="mt-4 w-full rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50"
      >
        Uitloggen
      </button>
    </nav>
  );
}
