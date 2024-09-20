"""Add reply, like, and dislike features to Comment model

Revision ID: 92033dae4266
Revises: fec4866934a0
Create Date: 2024-09-19 10:09:50.495249

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92033dae4266'
down_revision = 'fec4866934a0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('parent_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('likes', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('dislikes', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'comment', ['parent_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('dislikes')
        batch_op.drop_column('likes')
        batch_op.drop_column('parent_id')

    # ### end Alembic commands ###