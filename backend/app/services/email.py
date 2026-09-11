# services/email.py
import resend
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from app.core.config import settings

resend.api_key = settings.email_api_key

_template_env = Environment(loader=FileSystemLoader("templates"))


def render_invoice_pdf(invoice, customer) -> bytes:
    template = _template_env.get_template("invoice.html")
    html_content = template.render(
        business_name=settings.business_name,
        invoice=invoice,
        customer=customer,
    )
    pdf_bytes = HTML(string=html_content).write_pdf()
    return pdf_bytes


def send_invoice_email(invoice, customer, pdf_bytes: bytes) -> None:
    resend.Emails.send({
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
    })
