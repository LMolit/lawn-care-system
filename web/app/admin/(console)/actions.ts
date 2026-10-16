"use server";

import { redirect } from "next/navigation";
import { clearSessionCookies } from "@/lib/admin/session";

// Ends the session in this browser only. The tokens stay valid on the backend
// until they expire; "sign out everywhere" is a separate button, later.
export async function logoutAction() {
  await clearSessionCookies();
  redirect("/admin/login");
}
