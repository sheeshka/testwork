"""seed_orders

Revision ID: 2ef3d7f3388c
Revises: 225d7f1a8d57
Create Date: 2026-03-11 03:26:04.178884

"""
from typing import Sequence, Union

import uuid
from datetime import datetime

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2ef3d7f3388c'
down_revision: Union[str, None] = '225d7f1a8d57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

orders_table = sa.table(
    'orders',
    sa.column('id', sa.Uuid),
    sa.column('amount', sa.Numeric),
    sa.column('payment_status', sa.String),
    sa.column('created_at', sa.DateTime),
    sa.column('updated_at', sa.DateTime),
)

SEED_DATA = [
    {"id": uuid.uuid4(), "amount": 1500.00, "payment_status": "not_paid"},
    {"id": uuid.uuid4(), "amount": 3200.50, "payment_status": "not_paid"},
    {"id": uuid.uuid4(), "amount": 750.00, "payment_status": "not_paid"},
]


def upgrade() -> None:
    now = datetime.utcnow()
    for order in SEED_DATA:
        order["created_at"] = now
        order["updated_at"] = now
    op.bulk_insert(orders_table, SEED_DATA)


def downgrade() -> None:
    for order in SEED_DATA:
        op.execute(
            orders_table.delete().where(orders_table.c.id == order["id"])
        )
