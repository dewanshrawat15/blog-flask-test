from sqlalchemy import UUID, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

from sqlalchemy import Column, String, DateTime
from datetime import datetime
import os
from uuid import uuid4


load_dotenv()
Base = declarative_base()

postgres_user = os.environ.get("POSTGRES_USER")
postgres_password = os.environ.get("POSTGRES_PASSWORD")
postgres_host = os.environ.get("POSTGRES_HOST")
postgres_port = "5432"
DEV = os.environ.get("DEV")
is_prod = DEV == "False"
postgres_db = os.environ.get("POSTGRES_DB")


if not all([postgres_user, postgres_password, postgres_db]):
    raise ValueError(
        "Environment variables POSTGRES_USER, POSTGRES_PASSWORD, and"
        "POSTGRES_DB must be set."
    )

engine = create_engine(f'postgresql://{postgres_user}:{postgres_password}'
                       f'@{postgres_host}:{postgres_port}/{postgres_db}',
                       echo=True)

Session = sessionmaker(bind=engine)

"""Generates an API Key"""


class BlogPost(Base):  # type: ignore
    __tablename__ = "blogposts"
    id = Column(UUID(as_uuid=True), primary_key=True,
                index=True, default=uuid4)
    title = Column(String)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    def save(self):
        session = Session()
        try:
            session.add(self)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete(self):
        session = Session()
        try:
            session.delete(self)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at
        }


Base.metadata.create_all(engine)
