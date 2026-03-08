import { AuthGuard } from "@/components/auth/AuthGuard";
import { DashboardNav } from "@/components/layout/DashboardNav";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGuard>
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="flex flex-col gap-8 lg:flex-row">
          <aside className="w-full shrink-0 lg:w-64">
            <DashboardNav />
          </aside>
          <main className="flex-1">{children}</main>
        </div>
      </div>
    </AuthGuard>
  );
}
