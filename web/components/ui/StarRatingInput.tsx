"use client";

import { useState } from "react";
import { Star, CircleAlert } from "lucide-react";
import { cn } from "@/lib/utils";

const labels = ["Poor", "Fair", "Good", "Very good", "Excellent"];

export function StarRatingInput({
  value,
  onChange,
  error,
  name = "rating",
}: {
  value: number;
  onChange: (rating: number) => void;
  error?: string;
  name?: string;
}) {
  const [hover, setHover] = useState(0);
  const shown = hover || value;

  return (
    <fieldset>
      <legend
        className={cn(
          "mb-2 text-sm font-semibold",
          error ? "text-red-700" : "text-forest-dark",
        )}
      >
        Your rating <span className="text-red-600">*</span>
      </legend>

      <div
        className={cn(
          "inline-flex gap-1 rounded-xl border-2 px-3 py-2",
          error ? "border-red-600 bg-red-50" : "border-transparent",
        )}
        onMouseLeave={() => setHover(0)}
      >
        {[1, 2, 3, 4, 5].map((n) => (
          <label
            key={n}
            className="cursor-pointer"
            onMouseEnter={() => setHover(n)}
          >
            <input
              type="radio"
              name={name}
              value={n}
              checked={value === n}
              onChange={() => onChange(n)}
              className="peer sr-only"
              aria-label={`${n} out of 5 stars, ${labels[n - 1]}`}
            />
            <Star
              size={40}
              aria-hidden="true"
              className={cn(
                "rounded-md transition peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-forest",
                n <= shown ? "fill-gold text-gold" : "text-line",
              )}
            />
          </label>
        ))}
      </div>

      <p className="mt-2 h-5 text-sm text-muted" aria-live="polite">
        {shown > 0 ? labels[shown - 1] : ""}
      </p>

      {error && (
        <p
          role="alert"
          className="mt-1 flex items-start gap-2 text-sm font-semibold text-red-700"
        >
          <CircleAlert size={18} className="mt-px shrink-0" />
          {error}
        </p>
      )}
    </fieldset>
  );
}
