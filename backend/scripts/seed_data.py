import random
from datetime import date, datetime, timedelta, timezone

from faker import Faker
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from app.db.base import (
    Customer, Expense, ExpenseCategory, Invoice, InvoiceLineItem, InvoiceStatus,
    Job, JobEvent, JobEventType, JobStatus, JobType, Lead, LeadStatus, Payment,
    PaymentMethod, Property, Review, Route, RouteStatus, RouteStop, Service,
    User,
)
from app.db.session import SessionLocal
from app.services.invoicing import get_next_invoice_number

fake = Faker()
db = SessionLocal()


def already_seeded() -> bool:
    return db.query(User).first() is not None


if already_seeded():
    print("Database already has data — aborting to avoid duplicating. "
          "This script is one-time-only by design.")
    exit(1)

# --- Users ---
admin = User(
    email="owner@lawncare.local",
    password_hash="placeholder_not_a_real_hash",  # real hashing comes in the backend spec
    name="Business Owner",
    active=True,
)
db.add(admin)
db.commit()

# --- Leads (created first, converted_customer_id left null for now) ---
leads = []
for _ in range(15):
    lead = Lead(
        name=fake.name(),
        email=fake.email(),
        phone=fake.phone_number(),
        address=fake.address(),
        message=fake.sentence(),
        status=random.choice(list(LeadStatus)),
    )
    db.add(lead)
    leads.append(lead)
db.commit()

# --- Customers (some linked back to a lead, some not) ---
customers = []
for i in range(20):
    linked_lead = leads[i] if i < len(leads) else None
    customer = Customer(
        name=fake.name(),
        email=fake.email(),
        phone=fake.phone_number(),
        lead_id=linked_lead.id if linked_lead else None,
        active=True,
    )
    db.add(customer)
    customers.append(customer)
db.commit()

# --- Resolve the circular reference: mark some leads as converted ---
for i in range(10):  # first 10 leads convert into the customer they seeded
    leads[i].status = LeadStatus.converted
    leads[i].converted_customer_id = customers[i].id
db.commit()

# --- Properties ---
properties = []
for customer in customers:
    lat = fake.latitude()
    lon = fake.longitude()
    point = from_shape(Point(lon, lat), srid=4326)

    prop = Property(
        customer_id=customer.id,
        address=fake.address(),
        location=point,
        lawn_size_sqft=random.randint(2000, 12000),
        access_notes=fake.sentence() if random.random() > 0.5 else None,
    )
    db.add(prop)
    properties.append(prop)
db.commit()

# --- Services ---
service_defs = [
    ("Weekly Mowing", 45.00, 30),
    ("Bi-Weekly Mowing", 55.00, 30),
    ("Fall Cleanup", 150.00, 120),
    ("Mulching", 200.00, 90),
    ("Aeration", 175.00, 60),
]
services = []
for name, price, duration in service_defs:
    svc = Service(name=name, base_price=price, estimated_duration_minutes=duration)
    db.add(svc)
    services.append(svc)
db.commit()

# --- Jobs ---
jobs = []
for _ in range(40):
    customer = random.choice(customers)
    prop = next(p for p in properties if p.customer_id == customer.id)
    service = random.choice(services)
    job = Job(
        customer_id=customer.id,
        property_id=prop.id,
        service_id=service.id,
        scheduled_date=date.today() - timedelta(days=random.randint(-30, 60)),
        status=random.choice(list(JobStatus)),
        estimated_duration_minutes=service.estimated_duration_minutes,
        actual_duration_minutes=random.randint(20, 150) if random.random() > 0.4 else None,
        price=service.base_price,
        job_type=random.choice(list(JobType)),
    )
    db.add(job)
    jobs.append(job)
db.commit()

# --- Job events ---
for job in jobs:
    if job.status in (JobStatus.completed, JobStatus.in_progress):
        db.add(JobEvent(
            job_id=job.id,
            event_type=JobEventType.started,
            timestamp=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30)),
        ))
    if job.status == JobStatus.completed:
        db.add(JobEvent(
            job_id=job.id,
            event_type=JobEventType.completed,
            timestamp=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 29)),
        ))
db.commit()

# --- Routes + route stops ---
scheduled_jobs = [j for j in jobs if j.status == JobStatus.scheduled][:10]
for i, job in enumerate(scheduled_jobs[:5]):
    route = Route(
        date=date.today() + timedelta(days=i),
        status=RouteStatus.planned,
        algorithm_used="nearest_neighbor_v1",
    )
    db.add(route)
    db.commit()
    db.add(RouteStop(route_id=route.id, job_id=job.id, sequence_order=1))
    db.commit()

# --- Reviews ---
for _ in range(12):
    db.add(Review(
        customer_id=random.choice(customers).id if random.random() > 0.3 else None,
        name=fake.name(),
        rating=random.randint(1, 5),
        comment=fake.sentence(),
        approved=random.random() > 0.2,
    ))
db.commit()

# --- Invoices, line items, payments ---
for job in [j for j in jobs if j.status == JobStatus.completed]:
    invoice = Invoice(
        customer_id=job.customer_id,
        invoice_number=get_next_invoice_number(db),
        issue_date=job.scheduled_date,
        due_date=job.scheduled_date + timedelta(days=14),
        status=random.choice(list(InvoiceStatus)),
        subtotal=job.price,
        tax=round(job.price * 0.07, 2),
        total=round(job.price * 1.07, 2),
    )
    db.add(invoice)
    db.commit()

    db.add(InvoiceLineItem(
        invoice_id=invoice.id,
        job_id=job.id,
        description=f"Service on {job.scheduled_date}",
        quantity=1,
        unit_price=job.price,
        total=job.price,
    ))

    if invoice.status == InvoiceStatus.paid:
        db.add(Payment(
            invoice_id=invoice.id,
            amount=invoice.total,
            method=random.choice(list(PaymentMethod)),
            paid_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 10)),
        ))
    db.commit()

# --- Expense categories + expenses ---
category_names = ["Fuel", "Equipment", "Supplies", "Insurance"]
categories = []
for name in category_names:
    cat = ExpenseCategory(name=name)
    db.add(cat)
    categories.append(cat)
db.commit()

for _ in range(25):
    db.add(Expense(
        category_id=random.choice(categories).id,
        description=fake.sentence(nb_words=4),
        amount=round(random.uniform(15, 300), 2),
        date=date.today() - timedelta(days=random.randint(0, 90)),
        vendor=fake.company(),
        job_id=random.choice(jobs).id if random.random() > 0.5 else None,
    ))
db.commit()

db.close()
print("Seed data created successfully.")


