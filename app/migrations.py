from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def ensure_schema(engine: Engine) -> None:
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    if "subscriptions" in existing_tables:
        _ensure_column(
            engine,
            inspector,
            "subscriptions",
            "user_id",
            "INTEGER",
        )
    if "job_runs" in existing_tables:
        _ensure_column(engine, inspector, "job_runs", "user_id", "INTEGER")
    if "scheduler_config" in existing_tables:
        _ensure_column(
            engine,
            inspector,
            "scheduler_config",
            "user_id",
            "INTEGER",
        )


def _ensure_column(
    engine: Engine,
    inspector,
    table_name: str,
    column_name: str,
    column_sql: str,
) -> None:
    columns = {column["name"] for column in inspector.get_columns(table_name)}
    if column_name in columns:
        return
    with engine.begin() as connection:
        connection.execute(
            text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_sql}")
        )
