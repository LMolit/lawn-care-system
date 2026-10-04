import { Star } from "lucide-react";

export function StarRating({
  rating,
  size = 18,
}: {
  rating: number;
  size?: number;
}) {
  return (
    <div
      role="img"
      aria-label={`${rating} out of 5 stars`}
      className="flex gap-0.5"
    >
      {[1, 2, 3, 4, 5].map((n) => (
        <Star
          key={n}
          size={size}
          aria-hidden="true"
          className={n <= rating ? "fill-gold text-gold" : "text-line"}
        />
      ))}
    </div>
  );
}
