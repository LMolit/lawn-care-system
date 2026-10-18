// Must match the backend's business_timezone setting. The server itself runs in UTC,
// so the zone is named explicitly instead of trusting the machine.
const BUSINESS_TZ = "America/Chicago";

const dateFormat = new Intl.DateTimeFormat("en-US", {
  dateStyle: "medium",
  timeZone: BUSINESS_TZ,
});

export function formatDate(iso: string): string {
  return dateFormat.format(new Date(iso));
}
