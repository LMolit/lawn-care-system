import Link from "next/link";
import { cn } from "@/lib/utils";
import { Badge } from "./Badge";

export type TabItem = {
  label: string;
  href: string;
  count?: number;
  active: boolean;
};

// Each tab is a link to its own URL, so the page stays a plain Server Component
// and reload and back-button just work.
export function Tabs({ items, label }: { items: TabItem[]; label: string }) {
  return (
    <nav aria-label={label} className="flex gap-1 border-b border-line">
      {items.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          aria-current={item.active ? "page" : undefined}
          className={cn(
            "-mb-px flex items-center gap-2 border-b-2 px-4 py-3 text-sm font-semibold",
            "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-forest",
            item.active
              ? "border-forest text-forest-dark"
              : "border-transparent text-muted hover:text-forest-dark",
          )}
        >
          {item.label}
          {item.count !== undefined && (
            <Badge tone={item.active ? "success" : "neutral"}>
              {item.count}
            </Badge>
          )}
        </Link>
      ))}
    </nav>
  );
}
