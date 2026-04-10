"""add workout types table

Revision ID: a1f4c2d9e8b7
Revises: 74858962b483
Create Date: 2026-04-10 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1f4c2d9e8b7"
down_revision: Union[str, Sequence[str], None] = "74858962b483"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


workout_types_table = sa.table(
    "workout_types",
    sa.column("WorkoutType_ID", sa.Integer),
    sa.column("WorkoutType_Name", sa.String),
)


DEFAULT_WORKOUT_TYPES = [
    {"WorkoutType_Name": "squats"},
    {"WorkoutType_Name": "abdos"},
    {"WorkoutType_Name": "pumps"},
    {"WorkoutType_Name": "tractions"},
    {"WorkoutType_Name": "biking"},
    {"WorkoutType_Name": "running"},
    {"WorkoutType_Name": "other"},
]


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "workout_types",
        sa.Column("WorkoutType_ID", sa.Integer(), nullable=False),
        sa.Column("WorkoutType_Name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("WorkoutType_ID"),
    )
    op.create_index(op.f("ix_workout_types_WorkoutType_ID"), "workout_types", ["WorkoutType_ID"], unique=False)
    op.create_index(op.f("ix_workout_types_WorkoutType_Name"), "workout_types", ["WorkoutType_Name"], unique=True)

    op.bulk_insert(workout_types_table, DEFAULT_WORKOUT_TYPES)

    with op.batch_alter_table("workout_sessions", schema=None) as batch_op:
        batch_op.add_column(sa.Column("WorkoutType_ID", sa.Integer(), nullable=True))

    op.execute(
        sa.text(
            """
            UPDATE workout_sessions
            SET "WorkoutType_ID" = (
                SELECT wt."WorkoutType_ID"
                FROM workout_types wt
                WHERE lower(wt."WorkoutType_Name") = CASE
                    WHEN lower(COALESCE(workout_sessions."Session_Type", '')) LIKE '%squat%' THEN 'squats'
                    WHEN lower(COALESCE(workout_sessions."Session_Type", '')) LIKE '%abdo%' THEN 'abdos'
                    WHEN lower(COALESCE(workout_sessions."Session_Type", '')) LIKE '%pump%' THEN 'pumps'
                    WHEN lower(COALESCE(workout_sessions."Session_Type", '')) LIKE '%traction%' THEN 'tractions'
                    WHEN lower(COALESCE(workout_sessions."Session_Type", '')) LIKE '%bike%' THEN 'biking'
                    WHEN lower(COALESCE(workout_sessions."Session_Type", '')) LIKE '%run%' THEN 'running'
                    ELSE 'other'
                END
            )
            """
        )
    )

    with op.batch_alter_table("workout_sessions", schema=None) as batch_op:
        batch_op.alter_column("WorkoutType_ID", existing_type=sa.Integer(), nullable=False)
        batch_op.create_foreign_key(
            "fk_workout_sessions_workout_type",
            "workout_types",
            ["WorkoutType_ID"],
            ["WorkoutType_ID"],
        )
        batch_op.drop_column("Session_Type")


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("workout_sessions", schema=None) as batch_op:
        batch_op.add_column(sa.Column("Session_Type", sa.String(), nullable=True))

    op.execute(
        sa.text(
            """
            UPDATE workout_sessions
            SET "Session_Type" = (
                SELECT wt."WorkoutType_Name"
                FROM workout_types wt
                WHERE wt."WorkoutType_ID" = workout_sessions."WorkoutType_ID"
            )
            """
        )
    )

    with op.batch_alter_table("workout_sessions", schema=None) as batch_op:
        batch_op.drop_constraint("fk_workout_sessions_workout_type", type_="foreignkey")
        batch_op.drop_column("WorkoutType_ID")

    op.drop_index(op.f("ix_workout_types_WorkoutType_Name"), table_name="workout_types")
    op.drop_index(op.f("ix_workout_types_WorkoutType_ID"), table_name="workout_types")
    op.drop_table("workout_types")
