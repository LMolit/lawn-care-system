"use server";

import { revalidatePath } from "next/cache";
import { z } from "zod";
import { REVIEW_STATUSES, updateReviewStatus } from "@/lib/admin/reviews";

const schema = z.object({
  id: z.uuid(),
  status: z.enum(REVIEW_STATUSES),
});

export async function setReviewStatusAction(formData: FormData) {
  // A Server Action is a public POST endpoint, so validate it like any other input.
  const parsed = schema.safeParse({
    id: formData.get("id"),
    status: formData.get("status"),
  });
  if (!parsed.success) throw new Error("Invalid review update");

  await updateReviewStatus(parsed.data.id, parsed.data.status);
  // Re-renders this page with fresh data once the change is saved.
  revalidatePath("/admin/reviews");
}
