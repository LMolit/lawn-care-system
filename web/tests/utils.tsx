import { render } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

export function renderWithProviders(ui: React.ReactElement) {
  // A fresh cache per test, with retries off so failures show up immediately
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });

  return {
    user: userEvent.setup(),
    ...render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>),
  };
}
