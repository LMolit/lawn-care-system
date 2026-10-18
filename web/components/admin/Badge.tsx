import { cn } from "@/lib/utils";

type Tone = "neutral" | "success" | "warning";

const tones: Record<Tone, string> = {
  neutral: "bg-line text-muted",
  success: "bg-forest/10 text-forest-dark",
  warning: "bg-gold/25 text-forest-dark",
};

export function Badge({
  tone = "neutral",
  className,
  ...props
}: { tone?: Tone } & React.HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold",
        tones[tone],
        className,
      )}
      {...props}
    />
  );
}
