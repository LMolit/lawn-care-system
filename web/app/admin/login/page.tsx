import type { Metadata } from "next";
import { LoginForm } from "@/components/admin/LoginForm";

export const metadata: Metadata = { title: "Sign in" };

// Render per request. A pre-rendered page would get a long shared-cache lifetime
// in production, and nothing under /admin should be cached.
export const dynamic = "force-dynamic";

export default function LoginPage() {
  return (
    <main className="flex flex-1 items-center justify-center px-5 py-16">
      <div className="w-full max-w-sm">
        <h1 className="text-3xl font-semibold">Liberty Lawn Care</h1>
        <p className="mt-2 text-muted">Sign in to manage your business.</p>
        <LoginForm />
      </div>
    </main>
  );
}
