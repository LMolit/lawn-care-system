import Link from "next/link";
import { cn } from "@/lib/utils";

type Variant = "primary" | "secondary" | "accent";
type Size = "md" | "lg";

type StyleProps = {
  variant?: Variant;
  size?: Size;
  className?: string;
};

const base =
  "inline-flex items-center justify-center gap-2 rounded-full font-semibold " +
  "transition duration-150 active:scale-[0.98] " +
  "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-forest " +
  "disabled:pointer-events-none disabled:opacity-50";

const variants: Record<Variant, string> = {
  primary: "bg-forest text-white hover:bg-forest-dark shadow-sm",
  secondary:
    "border-2 border-forest text-forest hover:bg-forest hover:text-white",
  accent: "bg-gold text-forest-dark hover:brightness-95 shadow-sm",
};

const sizes: Record<Size, string> = {
  md: "px-5 py-2.5 text-base",
  lg: "px-7 py-3.5 text-lg",
};

function buttonClasses({
  variant = "primary",
  size = "md",
  className,
}: StyleProps) {
  return cn(base, variants[variant], sizes[size], className);
}

// A real <button>: for form submits and click handlers.
export function Button({
  variant,
  size,
  className,
  ...props
}: StyleProps & React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={buttonClasses({ variant, size, className })}
      {...props}
    />
  );
}

// A link that looks like a button: for navigation.
export function ButtonLink({
  variant,
  size,
  className,
  ...props
}: StyleProps & React.ComponentProps<typeof Link>) {
  return (
    <Link className={buttonClasses({ variant, size, className })} {...props} />
  );
}
