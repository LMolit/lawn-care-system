import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  adminFetch: vi.fn(),
  revalidatePath: vi.fn(),
}));
vi.mock("@/lib/admin/api", () => ({ adminFetch: mocks.adminFetch }));
vi.mock("next/cache", () => ({ revalidatePath: mocks.revalidatePath }));

import { setReviewStatusAction } from "@/app/admin/(console)/reviews/actions";

const ID = "3f2b8c1e-6a4d-4e0b-9c57-1d2e3f4a5b6c";

function form(id: string, status: string) {
  const data = new FormData();
  data.set("id", id);
  data.set("status", status);
  return data;
}

beforeEach(() => {
  mocks.adminFetch.mockReset();
  mocks.revalidatePath.mockReset();
  mocks.adminFetch.mockImplementation(
    async () => new Response("{}", { status: 200 }),
  );
});

describe("setReviewStatusAction", () => {
  it("sends the change to the backend and refreshes the page", async () => {
    await setReviewStatusAction(form(ID, "hidden"));
    const [url, init] = mocks.adminFetch.mock.calls[0];
    expect(url).toBe(`/api/v1/reviews/${ID}`);
    expect(init.method).toBe("PATCH");
    expect(JSON.parse(init.body)).toEqual({ status: "hidden" });
    expect(mocks.revalidatePath).toHaveBeenCalledWith("/admin/reviews");
  });

  it("rejects a status that does not exist, without calling the backend", async () => {
    await expect(setReviewStatusAction(form(ID, "spam"))).rejects.toThrow();
    expect(mocks.adminFetch).not.toHaveBeenCalled();
  });

  it("rejects an id that is not a UUID, without calling the backend", async () => {
    await expect(
      setReviewStatusAction(form("../../users", "approved")),
    ).rejects.toThrow();
    expect(mocks.adminFetch).not.toHaveBeenCalled();
  });

  it("does not refresh the page when the backend refuses", async () => {
    mocks.adminFetch.mockImplementation(
      async () => new Response("{}", { status: 404 }),
    );
    await expect(setReviewStatusAction(form(ID, "approved"))).rejects.toThrow();
    expect(mocks.revalidatePath).not.toHaveBeenCalled();
  });
});
