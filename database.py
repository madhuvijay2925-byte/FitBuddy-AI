from pathlib import Path
from datetime import datetime

from sqlalchemy import create_engine, String, Integer, Float, Text, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "fitbuddy.db"

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100))
    age: Mapped[int] = mapped_column(Integer)
    weight: Mapped[float] = mapped_column(Float)
    goal: Mapped[str] = mapped_column(String(100))
    intensity: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), index=True)

    original_plan: Mapped[str] = mapped_column(Text)
    updated_plan: Mapped[str | None] = mapped_column(Text, nullable=True)

    nutrition_tip: Mapped[str] = mapped_column(Text)

    feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


def init_db():
    Base.metadata.create_all(bind=engine)


def save_user(
    user_id,
    username,
    age,
    weight,
    goal,
    intensity
):
    db = SessionLocal()

    try:
        user = db.query(User).filter(
            User.user_id == user_id
        ).first()

        if user:
            user.username = username
            user.age = age
            user.weight = weight
            user.goal = goal
            user.intensity = intensity
        else:
            user = User(
                user_id=user_id,
                username=username,
                age=age,
                weight=weight,
                goal=goal,
                intensity=intensity
            )

            db.add(user)

        db.commit()
        db.refresh(user)

        return user

    finally:
        db.close()


def save_plan(
    user_id,
    original_plan,
    nutrition_tip
):
    db = SessionLocal()

    try:
        plan = Plan(
            user_id=user_id,
            original_plan=original_plan,
            nutrition_tip=nutrition_tip
        )

        db.add(plan)
        db.commit()
        db.refresh(plan)

        return plan

    finally:
        db.close()


def get_user(user_id):
    db = SessionLocal()

    try:
        return db.query(User).filter(
            User.user_id == user_id
        ).first()

    finally:
        db.close()


def get_plan(user_id):
    db = SessionLocal()

    try:
        return db.query(Plan).filter(
            Plan.user_id == user_id
        ).order_by(
            Plan.id.desc()
        ).first()

    finally:
        db.close()


def update_plan(
    user_id,
    updated_plan,
    feedback
):
    db = SessionLocal()

    try:
        plan = db.query(Plan).filter(
            Plan.user_id == user_id
        ).order_by(
            Plan.id.desc()
        ).first()

        if not plan:
            return None

        plan.updated_plan = updated_plan
        plan.feedback = feedback

        db.commit()
        db.refresh(plan)

        return plan

    finally:
        db.close()


def get_all_users():
    db = SessionLocal()

    try:
        return db.query(User).order_by(
            User.id.desc()
        ).all()

    finally:
        db.close()


def delete_user(user_id):
    db = SessionLocal()

    try:
        user = db.query(User).filter(
            User.user_id == user_id
        ).first()

        if user:
            db.delete(user)

        plans = db.query(Plan).filter(
            Plan.user_id == user_id
        ).all()

        for plan in plans:
            db.delete(plan)

        db.commit()

    finally:
        db.close()