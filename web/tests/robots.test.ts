import { describe, expect, it } from "vitest";
import robots from "@/app/robots";
import sitemap from "@/app/sitemap";

describe("the admin console stays out of search", () => {
  it("disallows /admin in robots.txt", () => {
    const rules = robots().rules;
    const list = Array.isArray(rules) ? rules : [rules];
    expect(list.flatMap((rule) => rule.disallow ?? [])).toContain("/admin");
  });

  it("never lists /admin in the sitemap", () => {
    for (const entry of sitemap()) {
      expect(entry.url).not.toContain("/admin");
    }
  });
});
