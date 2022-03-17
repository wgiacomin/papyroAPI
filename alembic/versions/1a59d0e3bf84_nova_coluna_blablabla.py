"""Nova coluna blablabla

Revision ID: 1a59d0e3bf84
Revises: 7a9f9bf60b78
Create Date: 2022-03-16 23:36:03.939145

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a59d0e3bf84'
down_revision = '7a9f9bf60b78'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('status_usuario_livro',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_status_usuario_livro_id'), 'status_usuario_livro', ['id'], unique=False)
    op.add_column('usuario_livro', sa.Column('fk_livro', sa.Integer(), nullable=False))
    op.add_column('usuario_livro', sa.Column('fk_status', sa.Integer(), nullable=True))
    op.drop_constraint('usuario_livro_fk_cargo_fkey', 'usuario_livro', type_='foreignkey')
    op.drop_constraint('usuario_livro_fk_grupo_fkey', 'usuario_livro', type_='foreignkey')
    op.create_foreign_key(None, 'usuario_livro', 'status_usuario_livro', ['fk_status'], ['id'])
    op.create_foreign_key(None, 'usuario_livro', 'livro', ['fk_livro'], ['id'])
    op.drop_column('usuario_livro', 'fk_cargo')
    op.drop_column('usuario_livro', 'fk_grupo')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('usuario_livro', sa.Column('fk_grupo', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('usuario_livro', sa.Column('fk_cargo', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'usuario_livro', type_='foreignkey')
    op.drop_constraint(None, 'usuario_livro', type_='foreignkey')
    op.create_foreign_key('usuario_livro_fk_grupo_fkey', 'usuario_livro', 'grupo', ['fk_grupo'], ['id'])
    op.create_foreign_key('usuario_livro_fk_cargo_fkey', 'usuario_livro', 'cargo', ['fk_cargo'], ['id'])
    op.drop_column('usuario_livro', 'fk_status')
    op.drop_column('usuario_livro', 'fk_livro')
    op.drop_index(op.f('ix_status_usuario_livro_id'), table_name='status_usuario_livro')
    op.drop_table('status_usuario_livro')
    # ### end Alembic commands ###
