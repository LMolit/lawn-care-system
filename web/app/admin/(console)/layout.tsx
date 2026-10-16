import Link from "next/link";
import { LogOut } from "lucide-react";
import { adminFetch } from "@/lib/admin/api";
import type { paths } from "@/lib/api/schema";
import { logoutAction } from "./actions";

type Me =
  paths["/api/v1/auth/me"]["get"]["responses"]["200"]["content"]["application/json"];

export default async function ConsoleLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  // Doubles as the guard: no valid session means a redirect to the login page.
  const res = await adminFetch("/api/v1/auth/me");
  if (!res.ok) throw new Error(`Failed to load account (${res.status})`);
  const me: Me = await res.json();

  return (
    <div className="flex flex-1 flex-col md:flex-row">
      <aside className="flex flex-wrap items-center justify-between gap-4 bg-forest-dark px-5 py-4 text-white md:w-64 md:flex-col md:items-stretch md:justify-start md:gap-8 md:py-6">
        <div>
          <p className="font-display text-lg font-semibold">
            Liberty Lawn Care
          </p>
          <p className="text-sm text-white/70">Admin</p>
        </div>
        <nav aria-label="Admin">
          <Link
            href="/admin"
            className="block rounded-lg bg-white/10 px-3 py-2 font-semibold"
          >
            Dashboard
          </Link>
        </nav>
        <div className="md:mt-auto">
          <p className="mb-2 hidden truncate text-sm text-white/70 md:block">
            {me.email}
          </p>
          <form action={logoutAction}>
            <button
              type="submit"
              className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-semibold hover:bg-white/10 focus-visible:outline-2 focus-visible:outline-gold"
            >
              <LogOut size={18} />
              Sign out
            </button>
          </form>
        </div>
      </aside>
      <main className="flex-1 p-6 md:p-10">{children}</main>
    </div>
  );
}
