"use client";

import { Button } from "@/components/ui/Button";

export default function ConsoleError({ reset }: { reset: () => void }) {
  return (
    <div role="alert">
      <h1 className="text-2xl font-semibold">Something went wrong</h1>
      <p className="mt-2 max-w-prose text-muted">
        This page could not load. Nothing was lost. Try again, and if it keeps
        happening, contact your web developer.
      </p>
      <Button className="mt-6" onClick={reset}>
        Try again
      </Button>
    </div>
  );
}
