import { useId } from "react";
import { cn } from "@/lib/utils";
import { Field, fieldClasses } from "./Field";

type InputProps = React.ComponentProps<"input"> & {
  label: string;
  error?: string;
  hint?: string;
};

export function Input({
  label,
  error,
  hint,
  className,
  required,
  ...props
}: InputProps) {
  const id = useId();
  return (
    <Field id={id} label={label} error={error} hint={hint} required={required}>
      <input
        id={id}
        aria-invalid={!!error}
        aria-describedby={
          error ? `${id}-error` : hint ? `${id}-hint` : undefined
        }
        className={cn(fieldClasses(error), className)}
        {...props}
      />
    </Field>
  );
}
