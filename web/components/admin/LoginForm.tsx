"use client";

import { useActionState } from "react";
import { CircleAlert } from "lucide-react";
import { loginAction, type LoginState } from "@/app/admin/login/actions";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";

const initialState: LoginState = {};

export function LoginForm() {
  // useActionState runs loginAction on submit and gives back whatever it returned
  // (our error and email), plus a `pending` flag while the request is in flight.
  const [state, formAction, pending] = useActionState(
    loginAction,
    initialState,
  );

  return (
    <form action={formAction} className="mt-8 space-y-5">
      <Input
        label="Email"
        name="email"
        type="email"
        autoComplete="username"
        autoCapitalize="none" // phone keyboards capitalize the first letter
        spellCheck={false}
        defaultValue={state.email}
        required
      />
      <Input
        label="Password"
        name="password"
        type="password"
        autoComplete="current-password"
        required
      />
      {state.error && (
        <p
          role="alert"
          className="flex items-start gap-2 text-sm font-semibold text-red-700"
        >
          <CircleAlert size={18} className="mt-px shrink-0" />
          {state.error}
        </p>
      )}
      <Button type="submit" size="lg" className="w-full" disabled={pending}>
        {pending ? "Signing in…" : "Sign in"}
      </Button>
    </form>
  );
}
