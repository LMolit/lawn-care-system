# services/email.py
import resend
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from app.core.config import settings

resend.api_key = settings.email_api_key

_template_env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


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
