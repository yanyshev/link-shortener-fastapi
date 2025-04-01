from uuid import uuid4
from sqlalchemy.orm import Session

from app.models import Link

def generate_unique_short_code(db: Session, length: int = 6) -> str:
    """Generates a unique short code that is not already in use."""
    while True:
        short_code = uuid4().hex[:length]
        if not db.query(Link).filter_by(short_code=short_code).first():
            return short_code