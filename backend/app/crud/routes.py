from datetime import date as date_type

from sqlalchemy import select
from sqlalchemy.orm import Session
from geoalchemy2.shape import to_shape

from app.db.base import Job, JobStatus, Property, Route, RouteStop
from app.services.routing import get_distance_matrix, nearest_neighbor_route

# Placeholder starting point (business home/shop address) — no dedicated
# table for this yet, so it's a plain constant for now. Replace with a real
# config value once the business's actual home base coordinates are known.
HOME_LOCATION = (41.5, -87.5)


def generate_route(db: Session, *, route_date: date_type) -> Route:
    jobs = list(
        db.scalars(
            select(Job).where(Job.scheduled_date == route_date, Job.status == JobStatus.scheduled)
        )
    )

    route = Route(date=route_date, algorithm_used="nearest_neighbor_v1")
    db.add(route)

    if not jobs:
        db.commit()
        return route

    # Build the coordinate list: HOME_LOCATION first, then each job's property location, in job order
    locations = [HOME_LOCATION]

    for job in jobs:
        property = db.get(Property, job.property_id)
        point = to_shape(property.location)
        locations.append((point.y, point.x))  # y = latitude, x = longitude

    distance_matrix = get_distance_matrix(locations)

    stops = [{"job_id": job.id} for job in jobs]
    ordered_stops = nearest_neighbor_route(HOME_LOCATION, stops, distance_matrix)

    for sequence_order, stop in enumerate(ordered_stops, start=1):
        route_stop = RouteStop(
            route_id=route.id,
            job_id=stop["job_id"],
            sequence_order=sequence_order,
        )
        db.add(route_stop)

    db.commit()
    return route


def get_route_by_date(db: Session, *, route_date: date_type) -> Route | None:
    return db.scalar(select(Route).where(Route.date == route_date))
