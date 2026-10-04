import type { paths } from "./schema";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export type LeadInput =
  paths["/api/v1/leads"]["post"]["requestBody"]["content"]["application/json"];

export async function submitLead(lead: LeadInput) {
  const res = await fetch(`${API_URL}/api/v1/leads`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(lead),
  });
  if (!res.ok) throw new Error(`Failed to submit lead (${res.status})`);
  return res.json();
}
