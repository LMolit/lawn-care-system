from datetime import date as date_type, datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import Invoice, InvoiceLineItem, Job, JobStatus, Service, Customer, InvoiceStatus
from app.exceptions import NotFoundError, ConflictError, ValidationError
from app.services.invoicing import get_next_invoice_number
from app.services.email import render_invoice_pdf, send_invoice_email

def create_invoice(db: Session, *, customer_id: int, job_ids: list[int], due_date: date_type) -> Invoice:
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise NotFoundError(f"Customer {customer_id} not found")

    jobs = []
    for job_id in job_ids:
        job = db.get(Job, job_id)
        if job is None:
            raise NotFoundError(f"Job {job_id} not found")
        if job.customer_id != customer_id:
            raise ValidationError(f"Job {job_id} does not belong to customer {customer_id}")
        if job.status != JobStatus.completed:
            raise ValidationError(f"Job {job_id} is not completed (current status: {job.status.value})")

        already_billed = db.scalar(
            select(InvoiceLineItem).where(InvoiceLineItem.job_id == job_id)
        )
        if already_billed is not None:
            raise ConflictError(f"Job {job_id} has already been invoiced")

        jobs.append(job)

    line_items = []
    subtotal = 0.0
    for job in jobs:
        service = db.get(Service, job.service_id)
        line_total = job.price  # quantity 1 * unit_price
        line_items.append(
            InvoiceLineItem(
                job_id=job.id,
                description=service.name,
                quantity=1,
                unit_price=job.price,
                total=line_total,
            )
        )
        subtotal += line_total

    tax = 0.0
    total = subtotal + tax

    invoice = Invoice(
        customer_id=customer_id,
        invoice_number=get_next_invoice_number(db),
        issue_date=date_type.today(),
        due_date=due_date,
        subtotal=subtotal,
        tax=tax,
        total=total,
    )
    db.add(invoice)
    db.flush()  # need invoice.id before attaching line items

    for line_item in line_items:
        line_item.invoice_id = invoice.id
        db.add(line_item)

    db.commit()
    db.refresh(invoice)
    return invoice

def send_invoice(db: Session, *, id: int) -> Invoice:
    invoice = db.get(Invoice, id)
    if invoice is None:
        raise NotFoundError(f"Invoice {id} not found")

    customer = db.get(Customer, invoice.customer_id)

    pdf_bytes = render_invoice_pdf(invoice, customer)
    send_invoice_email(invoice, customer, pdf_bytes)

    invoice.status = InvoiceStatus.sent
    invoice.sent_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(invoice)
    return invoice
