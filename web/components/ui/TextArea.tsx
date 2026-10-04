import { useId } from "react";
import { cn } from "@/lib/utils";
import { Field, fieldClasses } from "./Field";

type TextAreaProps = React.ComponentProps<"textarea"> & {
  label: string;
  error?: string;
  hint?: string;
};

export function TextArea({
  label,
  error,
  hint,
  className,
  required,
  ...props
}: TextAreaProps) {
  const id = useId();
  return (
    <Field id={id} label={label} error={error} hint={hint} required={required}>
      <textarea
        id={id}
        rows={4}
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
