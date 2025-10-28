"""seed user data

Revision ID: 6d278d92961d
Revises: 0f4c2eb9e0fe
Create Date: 2025-10-28 07:48:53.116463

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d278d92961d'
down_revision = '0f4c2eb9e0fe'
branch_labels = None
depends_on = None


from alembic import op
import sqlalchemy as sa

users = sa.table(
    'user',
    sa.Column('id', sa.Integer),
    sa.Column('name', sa.String(50)),
    sa.Column('email', sa.String(50)),
)

def upgrade():
    op.bulk_insert(
        users,
        [
            {'id': 101, 'name': 'Contoh 1', 'email': 'contoh1@example.com'},
            {'id': 102, 'name': 'Contoh 2', 'email': 'contoh2@example.com'},
        ],
    )

def downgrade():
    op.execute(
        users.delete().where(users.c.id.in_([101, 102]))
    )