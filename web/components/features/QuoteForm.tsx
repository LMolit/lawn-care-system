"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { z } from "zod";
import { CheckCircle2, CircleAlert } from "lucide-react";
import { submitLead } from "@/lib/api/leads";
import { site } from "@/lib/site";
import { Input } from "@/components/ui/Input";
import { TextArea } from "@/components/ui/TextArea";
import { Button, ButtonLink } from "@/components/ui/Button";

// Keeps only digits, drops a leading US "1", and formats as (630) 555-0123.
function formatPhone(raw: string) {
  let digits = raw.replace(/\D/g, "");
  if (digits.length === 11 && digits.startsWith("1")) digits = digits.slice(1);
  digits = digits.slice(0, 10);

  if (digits.length === 0) return "";
  if (digits.length <= 3) return `(${digits}`;
  if (digits.length <= 6) return `(${digits.slice(0, 3)}) ${digits.slice(3)}`;
  return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`;
}

const quoteSchema = z
  .object({
    name: z.string().trim().min(1, "Please enter your name"),
    email: z
      .string()
      .trim()
      .email("That email doesn't look right")
      .or(z.literal("")),
    phone: z
      .string()
      .trim()
      .refine(
        (value) => value === "" || value.replace(/\D/g, "").length === 10,
        "Please enter a full 10-digit phone number",
      ),
    address: z.string().trim().min(1, "Please enter your property address"),
    message: z.string().trim(),
    website: z.string(), // honeypot
  })
  .refine((data) => data.email !== "" || data.phone !== "", {
    message: "Please enter a phone number or an email so we can reach you",
    path: ["phone"],
  });

type QuoteFormData = z.infer<typeof quoteSchema>;

export function QuoteForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, submitCount },
  } = useForm<QuoteFormData>({
    resolver: zodResolver(quoteSchema),
    defaultValues: {
      name: "",
      email: "",
      phone: "",
      address: "",
      message: "",
      website: "",
    },
  });

  const mutation = useMutation({ mutationFn: submitLead });
  const [botDone, setBotDone] = useState(false);

  const phoneField = register("phone");
  const hasErrors = Object.keys(errors).length > 0;

  function onSubmit(data: QuoteFormData) {
    // Honeypot: real people never see this field. If it's filled, a bot did it.
    // Pretend success so the bot learns nothing, but send nothing.
    if (data.website) {
      setBotDone(true);
      return;
    }

    mutation.mutate({
      name: data.name,
      address: data.address,
      email: data.email || undefined,
      phone: data.phone || undefined,
      message: data.message || undefined,
    });
  }

  if (mutation.isSuccess || botDone) {
    return (
      <div className="flex flex-col items-center py-10 text-center">
        <CheckCircle2 size={56} className="text-forest" />
        <h2 className="mt-5 text-3xl font-semibold">
          Thanks, we got your request!
        </h2>
        <p className="mt-3 max-w-md text-lg text-muted">
          We&apos;ll get back to you soon with your free quote. Need us sooner?
          Call{" "}
          <a
            href={site.phoneHref}
            className="font-semibold text-forest underline"
          >
            {site.phone}
          </a>
          .
        </p>
        <ButtonLink href="/" variant="secondary" className="mt-8">
          Back to home
        </ButtonLink>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-10">
      {submitCount > 0 && hasErrors && (
        <div
          role="alert"
          className="flex items-center gap-3 rounded-xl border-2 border-red-600 bg-red-50 p-4 font-semibold text-red-800"
        >
          <CircleAlert className="shrink-0" />
          Please fix the highlighted fields below.
        </div>
      )}

      <fieldset className="space-y-6">
        <legend className="font-display text-2xl font-semibold text-forest-dark">
          How can we reach you?
        </legend>
        <p className="-mt-2 text-muted">
          Add a phone number, an email, or both.
        </p>

        <Input
          label="Your name"
          required
          autoComplete="name"
          error={errors.name?.message}
          {...register("name")}
        />

        <div className="grid gap-6 sm:grid-cols-2">
          <Input
            label="Phone"
            type="tel"
            inputMode="tel"
            autoComplete="tel"
            placeholder="(630) 555-0123"
            maxLength={14}
            error={errors.phone?.message}
            {...phoneField}
            onChange={(e) => {
              e.target.value = formatPhone(e.target.value);
              phoneField.onChange(e);
            }}
          />
          <Input
            label="Email"
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            error={errors.email?.message}
            {...register("email")}
          />
        </div>
      </fieldset>

      <fieldset className="space-y-6">
        <legend className="font-display text-2xl font-semibold text-forest-dark">
          About your property
        </legend>

        <Input
          label="Property address"
          required
          autoComplete="street-address"
          hint="Where the work will be done"
          error={errors.address?.message}
          {...register("address")}
        />

        <TextArea
          label="Tell us about your lawn"
          rows={5}
          hint="Services you're interested in, lawn size, anything we should know"
          error={errors.message?.message}
          {...register("message")}
        />
      </fieldset>

      {/* Honeypot: hidden from people and screen readers, visible to bots */}
      <div
        aria-hidden="true"
        className="absolute -left-[9999px] h-0 w-0 overflow-hidden"
      >
        <label>
          Leave this field empty
          <input
            type="text"
            tabIndex={-1}
            autoComplete="off"
            {...register("website")}
          />
        </label>
      </div>

      {mutation.isError && (
        <div
          role="alert"
          className="flex items-start gap-3 rounded-xl border-2 border-red-600 bg-red-50 p-4 text-red-800"
        >
          <CircleAlert className="mt-0.5 shrink-0" />
          <p>
            <span className="font-semibold">
              Something went wrong sending your request.
            </span>{" "}
            Please try again, or call us at{" "}
            <a href={site.phoneHref} className="font-semibold underline">
              {site.phone}
            </a>
            .
          </p>
        </div>
      )}

      <Button
        type="submit"
        size="lg"
        disabled={mutation.isPending}
        className="w-full"
      >
        {mutation.isPending ? "Sending..." : "Get My Free Quote"}
      </Button>
    </form>
  );
}
