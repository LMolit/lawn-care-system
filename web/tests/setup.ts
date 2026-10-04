import "@testing-library/jest-dom/vitest";
import { afterEach } from "vitest";
import { cleanup } from "@testing-library/react";

// Remove rendered components after each test so tests can't affect each other
afterEach(() => cleanup());
