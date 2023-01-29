"""001_ini

Revision ID: 722a59d84398
Revises: 
Create Date: 2023-01-29 12:43:42.026030

"""
from alembic import op
import sqlalchemy as sa
from src.models.primitives.base import SAUUID
from src.models.primitives.user import (
    SAEmail,
    SALastName,
    SAFirstName,
    SAMiddleName,
)
from src.models.primitives.folder import (
    SAFolderColor,
    SAFolderTitle,
)
from src.models.primitives.note import (
    SANoteColor,
    SANoteTitle,
)
from src.models.primitives.tag import (
    SATagTitle,
)
from src.models.event_log import SAEvent, SAEventType
from depot.fields.sqlalchemy import UploadedFileField


# revision identifiers, used by Alembic.
revision = '722a59d84398'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('auth_sessions',
    sa.Column('id', SAUUID(), nullable=False),
    sa.Column('token', sa.String(), nullable=False),
    sa.Column('user_id', SAUUID(), nullable=False),
    sa.Column('device_id', sa.String(), nullable=False),
    sa.Column('device_type', sa.String(), nullable=True),
    sa.Column('device_os', sa.String(), nullable=True),
    sa.Column('device_name', sa.String(), nullable=True),
    sa.Column('ip', sa.String(), nullable=True),
    sa.Column('user_agent', sa.String(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('expires_in', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_auth_sessions_device_id'), 'auth_sessions', ['device_id'], unique=False)
    op.create_index(op.f('ix_auth_sessions_token'), 'auth_sessions', ['token'], unique=False)
    op.create_index(op.f('ix_auth_sessions_user_id'), 'auth_sessions', ['user_id'], unique=False)
    op.create_table('events_log',
    sa.Column('id', SAUUID(), nullable=False),
    sa.Column('user_id', SAUUID(), nullable=True),
    sa.Column('object_id', sa.String(), nullable=True),
    sa.Column('type', SAEventType(), nullable=False),
    sa.Column('event', SAEvent(), nullable=False),
    sa.Column('info', sa.String(), nullable=True),
    sa.Column('datetime', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_events_log_object_id'), 'events_log', ['object_id'], unique=False)
    op.create_index(op.f('ix_events_log_type'), 'events_log', ['type'], unique=False)
    op.create_index(op.f('ix_events_log_user_id'), 'events_log', ['user_id'], unique=False)
    op.create_table('media',
    sa.Column('id', SAUUID(), nullable=False),
    sa.Column('md5', sa.String(length=32), nullable=False),
    sa.Column('file', UploadedFileField(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('password_change_tokens',
    sa.Column('id', SAUUID(), nullable=False),
    sa.Column('token', sa.String(), nullable=False),
    sa.Column('user_id', SAUUID(), nullable=False),
    sa.Column('email', SAEmail(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('expires_in', sa.DateTime(), nullable=True),
    sa.Column('used', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_password_change_tokens_token'), 'password_change_tokens', ['token'], unique=False)
    op.create_index(op.f('ix_password_change_tokens_user_id'), 'password_change_tokens', ['user_id'], unique=False)
    op.create_table('user',
    sa.Column('id', SAUUID(), nullable=False),
    sa.Column('email', SAEmail(), nullable=False),
    sa.Column('password', sa.String(), nullable=True),
    sa.Column('first_name', SAFirstName(), nullable=True),
    sa.Column('last_name', SALastName(), nullable=True),
    sa.Column('middle_name', SAMiddleName(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.DateTime(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('credential_version', SAUUID(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_table('folder',
    sa.Column('id', SAUUID(), nullable=False),
    sa.Column('title', SAFolderTitle(), nullable=False),
    sa.Column('color', SAFolderColor(), nullable=True),
    sa.Column('parent_id', SAUUID(), nullable=True),
    sa.Column('user_id', SAUUID(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['folder.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_folder_parent_id'), 'folder', ['parent_id'], unique=False)
    op.create_index(op.f('ix_folder_user_id'), 'folder', ['user_id'], unique=False)
    op.create_table('tag',
    sa.Column('id', SAUUID(), nullable=False),
    sa.Column('title', SATagTitle(), nullable=False),
    sa.Column('user_id', SAUUID(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tag_user_id'), 'tag', ['user_id'], unique=False)
    op.create_table('folder_tag',
    sa.Column('id', SAUUID(), nullable=False),
    sa.Column('folder_id', SAUUID(), nullable=False),
    sa.Column('tag_id', SAUUID(), nullable=False),
    sa.ForeignKeyConstraint(['folder_id'], ['folder.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_folder_tag_folder_id'), 'folder_tag', ['folder_id'], unique=False)
    op.create_index(op.f('ix_folder_tag_tag_id'), 'folder_tag', ['tag_id'], unique=False)
    op.create_table('note',
    sa.Column('id', SAUUID(), nullable=False),
    sa.Column('title', SANoteTitle(), nullable=False),
    sa.Column('color', SANoteColor(), nullable=True),
    sa.Column('text', sa.String(), nullable=True),
    sa.Column('folder_id', SAUUID(), nullable=True),
    sa.Column('user_id', SAUUID(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['folder_id'], ['folder.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_note_folder_id'), 'note', ['folder_id'], unique=False)
    op.create_index(op.f('ix_note_user_id'), 'note', ['user_id'], unique=False)
    op.create_table('note_tag',
    sa.Column('id', SAUUID(), nullable=False),
    sa.Column('note_id', SAUUID(), nullable=False),
    sa.Column('tag_id', SAUUID(), nullable=False),
    sa.ForeignKeyConstraint(['note_id'], ['note.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_note_tag_note_id'), 'note_tag', ['note_id'], unique=False)
    op.create_index(op.f('ix_note_tag_tag_id'), 'note_tag', ['tag_id'], unique=False)
    op.create_table('note_to_note_relation',
    sa.Column('id', SAUUID(), nullable=False),
    sa.Column('parent_note_id', SAUUID(), nullable=False),
    sa.Column('child_note_id', SAUUID(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['child_note_id'], ['note.id'], ),
    sa.ForeignKeyConstraint(['parent_note_id'], ['note.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_note_to_note_relation_child_note_id'), 'note_to_note_relation', ['child_note_id'], unique=False)
    op.create_index(op.f('ix_note_to_note_relation_parent_note_id'), 'note_to_note_relation', ['parent_note_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_note_to_note_relation_parent_note_id'), table_name='note_to_note_relation')
    op.drop_index(op.f('ix_note_to_note_relation_child_note_id'), table_name='note_to_note_relation')
    op.drop_table('note_to_note_relation')

    op.drop_index(op.f('ix_note_tag_tag_id'), table_name='note_tag')
    op.drop_index(op.f('ix_note_tag_note_id'), table_name='note_tag')
    op.drop_table('note_tag')

    op.drop_index(op.f('ix_note_user_id'), table_name='note')
    op.drop_index(op.f('ix_note_folder_id'), table_name='note')
    op.drop_table('note')

    op.drop_index(op.f('ix_folder_tag_tag_id'), table_name='folder_tag')
    op.drop_index(op.f('ix_folder_tag_folder_id'), table_name='folder_tag')
    op.drop_table('folder_tag')

    op.drop_index(op.f('ix_tag_user_id'), table_name='tag')
    op.drop_table('tag')

    op.drop_index(op.f('ix_folder_user_id'), table_name='folder')
    op.drop_index(op.f('ix_folder_parent_id'), table_name='folder')
    op.drop_table('folder')

    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')

    op.drop_index(op.f('ix_password_change_tokens_user_id'), table_name='password_change_tokens')
    op.drop_index(op.f('ix_password_change_tokens_token'), table_name='password_change_tokens')
    op.drop_table('password_change_tokens')

    op.drop_table('media')

    op.drop_index(op.f('ix_events_log_user_id'), table_name='events_log')
    op.drop_index(op.f('ix_events_log_type'), table_name='events_log')
    op.drop_index(op.f('ix_events_log_object_id'), table_name='events_log')
    op.drop_table('events_log')

    op.drop_index(op.f('ix_auth_sessions_user_id'), table_name='auth_sessions')
    op.drop_index(op.f('ix_auth_sessions_token'), table_name='auth_sessions')
    op.drop_index(op.f('ix_auth_sessions_device_id'), table_name='auth_sessions')
    op.drop_table('auth_sessions')
