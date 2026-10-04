import { CircleAlert } from "lucide-react";
import { cn } from "@/lib/utils";

export function Field({
  id,
  label,
  error,
  hint,
  required,
  children,
}: {
  id: string;
  label: string;
  error?: string;
  hint?: string;
  required?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label
        htmlFor={id}
        className={cn(
          "mb-2 block text-sm font-semibold",
          error ? "text-red-700" : "text-forest-dark",
        )}
      >
        {label}
        {required && <span className="text-red-600"> *</span>}
      </label>
      {children}
      {hint && !error && (
        <p id={`${id}-hint`} className="mt-2 text-sm text-muted">
          {hint}
        </p>
      )}
      {error && (
        <p
          id={`${id}-error`}
          role="alert"
          className="mt-2 flex items-start gap-2 text-sm font-semibold text-red-700"
        >
          <CircleAlert size={18} className="mt-px shrink-0" />
          {error}
        </p>
      )}
    </div>
  );
}

export function fieldClasses(error?: string) {
  return cn(
    "w-full rounded-xl border-2 px-4 py-3.5 text-base text-ink",
    "placeholder:text-muted/60 transition focus:outline-none focus:ring-4",
    error
      ? "border-red-600 bg-red-50 focus:border-red-600 focus:ring-red-600/20"
      : "border-line bg-white focus:border-forest focus:ring-forest/20",
  );
}
