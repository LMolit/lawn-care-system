import type { Metadata } from "next";

export const metadata: Metadata = { title: "Dashboard" };

export default function DashboardPage() {
  return (
    <>
      <h1 className="text-3xl font-semibold">Dashboard</h1>
      <p className="mt-3 text-muted">
        You&apos;re signed in. The dashboard cards come next.
      </p>
    </>
  );
}
