"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const items = [
  { href: "/admin", label: "Dashboard", exact: true },
  { href: "/admin/reviews", label: "Reviews", exact: false },
];

// A Client Component only because it needs usePathname to highlight the current page.
export function AdminNav() {
  const pathname = usePathname();

  return (
    <nav aria-label="Admin">
      <ul className="flex gap-1 md:flex-col">
        {items.map((item) => {
          const current = item.exact
            ? pathname === item.href
            : pathname === item.href || pathname.startsWith(`${item.href}/`);
          return (
            <li key={item.href}>
              <Link
                href={item.href}
                aria-current={current ? "page" : undefined}
                className={cn(
                  "block rounded-lg px-3 py-2 font-semibold hover:bg-white/10",
                  current && "bg-white/10",
                )}
              >
                {item.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
