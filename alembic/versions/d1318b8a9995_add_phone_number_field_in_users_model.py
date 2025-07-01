"""add phone number field in users model

Revision ID: d1318b8a9995
Revises:
Create Date: 2025-07-02 00:55:45.816644

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d1318b8a9995"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone_number", sa.String(), nullable=True))


def downgrade() -> None:
    pass
