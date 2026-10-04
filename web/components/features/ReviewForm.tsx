"use client";

import { useState } from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { z } from "zod";
import { CheckCircle2, CircleAlert } from "lucide-react";
import { submitReview } from "@/lib/api/reviews";
import { site } from "@/lib/site";
import { Input } from "@/components/ui/Input";
import { TextArea } from "@/components/ui/TextArea";
import { StarRatingInput } from "@/components/ui/StarRatingInput";
import { Button, ButtonLink } from "@/components/ui/Button";

const reviewSchema = z.object({
  name: z.string().trim().min(1, "Please enter your name"),
  rating: z.number().int().min(1, "Please choose a star rating").max(5),
  comment: z.string().trim(),
  website: z.string(), // honeypot
});

type ReviewFormData = z.infer<typeof reviewSchema>;

export function ReviewForm() {
  const {
    register,
    control,
    handleSubmit,
    formState: { errors, submitCount },
  } = useForm<ReviewFormData>({
    resolver: zodResolver(reviewSchema),
    defaultValues: { name: "", rating: 0, comment: "", website: "" },
  });

  const mutation = useMutation({ mutationFn: submitReview });
  const [botDone, setBotDone] = useState(false);
  const hasErrors = Object.keys(errors).length > 0;

  function onSubmit(data: ReviewFormData) {
    if (data.website) {
      setBotDone(true);
      return;
    }

    mutation.mutate({
      name: data.name,
      rating: data.rating,
      comment: data.comment || undefined,
    });
  }

  if (mutation.isSuccess || botDone) {
    return (
      <div className="flex flex-col items-center py-10 text-center">
        <CheckCircle2 size={56} className="text-forest" />
        <h2 className="mt-5 text-3xl font-semibold">
          Thank you for your review!
        </h2>
        <p className="mt-3 max-w-md text-lg text-muted">
          Reviews are checked before they&apos;re posted, so yours will appear
          on the site once it&apos;s approved.
        </p>
        <ButtonLink href="/" variant="secondary" className="mt-8">
          Back to home
        </ButtonLink>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-8">
      {submitCount > 0 && hasErrors && (
        <div
          role="alert"
          className="flex items-center gap-3 rounded-xl border-2 border-red-600 bg-red-50 p-4 font-semibold text-red-800"
        >
          <CircleAlert className="shrink-0" />
          Please fix the highlighted fields below.
        </div>
      )}

      <Controller
        name="rating"
        control={control}
        render={({ field }) => (
          <StarRatingInput
            value={field.value}
            onChange={field.onChange}
            error={errors.rating?.message}
          />
        )}
      />

      <Input
        label="Your name"
        required
        autoComplete="name"
        hint="Shown next to your review. First name and last initial is fine."
        error={errors.name?.message}
        {...register("name")}
      />

      <TextArea
        label="Your review"
        rows={5}
        hint="Optional. What did we do, and how did it turn out?"
        error={errors.comment?.message}
        {...register("comment")}
      />

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
              Something went wrong sending your review.
            </span>{" "}
            Please try again in a moment. If it keeps happening, call us at{" "}
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
        {mutation.isPending ? "Sending..." : "Submit My Review"}
      </Button>
    </form>
  );
}
