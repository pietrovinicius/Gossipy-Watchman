from sqlalchemy import Engine

from app.models import Base
from app.db.session import _get_engine


def init_db(engine: Engine | None = None) -> None:
    eng = _get_engine(engine)
    Base.metadata.create_all(bind=eng)
