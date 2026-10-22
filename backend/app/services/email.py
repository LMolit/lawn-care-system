# services/email.py
import logging

import resend
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from app.core.config import settings
from app.core.rate_limit import RateLimiter, RateLimitError

logger = logging.getLogger(__name__)

resend.api_key = settings.email_api_key

_template_env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(["html", "xml"]),
)

# Caps owner alerts across ALL visitors. The Resend free plan has a daily quota that
# invoices share, so a flood of junk submissions must not be able to use it up.
ALERTS_PER_HOUR = 20
_alert_limiter = RateLimiter(max_requests=ALERTS_PER_HOUR, window_seconds=3600)


def render_invoice_pdf(invoice, customer) -> bytes:
    template = _template_env.get_template("invoice.html")
    html_content = template.render(
        business_name=settings.business_name,
        invoice=invoice,
        customer=customer,
    )

    def _no_fetch(url, *args, **kwargs):
        raise ValueError(f"External fetch blocked: {url}")

    pdf_bytes = HTML(string=html_content, url_fetcher=_no_fetch).write_pdf()
    return pdf_bytes


def send_invoice_email(invoice, customer, pdf_bytes: bytes) -> None:
    resend.Emails.send(
        {
            "from": settings.email_from_address,
            "to": customer.email,
            "subject": f"Invoice {invoice.invoice_number} from {settings.business_name}",
            "html": f"<p>Please find attached invoice {invoice.invoice_number}.</p>",
            "attachments": [
                {
                    "filename": f"{invoice.invoice_number}.pdf",
                    "content": list(pdf_bytes),
                }
            ],
        }
    )


def send_owner_alert(subject: str, body: str) -> None:
    """Email the owner. Never raises: a failed alert must not break whatever triggered it."""
    if not settings.owner_alert_email:
        return
    try:
        _alert_limiter.hit("owner-alerts")
    except RateLimitError:
        logger.warning("Owner alert skipped: hourly alert limit reached")
        return
    try:
        resend.Emails.send(
            {
                "from": settings.email_from_address,
                "to": settings.owner_alert_email,
                "subject": subject,
                "text": body,
            }
        )
    except Exception as exc:
        # Log the kind of failure only
        logger.warning("Owner alert email failed: %s", type(exc).__name__)


# The subject and body below are fixed text plus a link we build ourselves. Nothing a
# stranger typed goes into an email: a "name" can contain a link that looks official.


def notify_new_lead(lead_id) -> None:
    link = f"{settings.site_url.rstrip('/')}/admin/leads/{lead_id}"
    send_owner_alert(
        "New quote request", f"You have a new quote request.\n\nOpen it: {link}\n"
    )


def notify_new_review() -> None:
    link = f"{settings.site_url.rstrip('/')}/admin/reviews?status=pending"
    send_owner_alert(
        "New review to moderate",
        f"A new review is waiting.\n\nOpen the queue: {link}\n",
    )
