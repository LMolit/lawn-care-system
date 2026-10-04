import { ImageResponse } from "next/og";
import { readFile } from "node:fs/promises";
import { join } from "node:path";

export const alt = "Liberty Lawn Care: lawn care in Batavia, IL";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function Image() {
  const logo = await readFile(join(process.cwd(), "public/logo.png"));
  const logoSrc = `data:image/png;base64,${logo.toString("base64")}`;

  return new ImageResponse(
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        alignItems: "center",
        gap: 60,
        padding: 80,
        background: "#faf7f0",
      }}
    >
      <img
        src={logoSrc}
        width={380}
        height={380}
        style={{ objectFit: "contain" }}
        alt=""
      />
      <div style={{ display: "flex", flexDirection: "column" }}>
        <div
          style={{
            fontSize: 34,
            color: "#8b5e3c",
            letterSpacing: 4,
            textTransform: "uppercase",
          }}
        >
          Lawn care in Batavia, IL
        </div>
        <div
          style={{
            fontSize: 84,
            fontWeight: 700,
            color: "#1f4029",
            marginTop: 16,
            lineHeight: 1.05,
          }}
        >
          Liberty Lawn Care
        </div>
        <div style={{ fontSize: 36, color: "#5b6b60", marginTop: 24 }}>
          Get a free quote today
        </div>
      </div>
    </div>,
    size,
  );
}
