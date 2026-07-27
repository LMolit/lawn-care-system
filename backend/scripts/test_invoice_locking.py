import concurrent.futures

from app.db.session import SessionLocal
from app.services.invoicing import get_next_invoice_number


def create_one_invoice_number():
    db = SessionLocal()
    try:
        return get_next_invoice_number(db)
    finally:
        db.close()


def main():
    num_concurrent_calls = 10

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent_calls) as executor:
        futures = [executor.submit(create_one_invoice_number) for _ in range(num_concurrent_calls)]
        results = [f.result() for f in futures]

    print("Generated invoice numbers:", results)

    duplicates = len(results) - len(set(results))
    if duplicates == 0:
        print(f"PASS: all {len(results)} invoice numbers are unique.")
    else:
        print(f"FAIL: {duplicates} duplicate(s) found!")


if __name__ == "__main__":
    main()
