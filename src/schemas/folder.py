from marshmallow import Schema, fields, EXCLUDE
from src.schemas.primitives.folders import (
    FolderTitleField,
    FolderColorField,
)


class FolderByIdParamsSchema(Schema):
    folder_id = fields.UUID(required=True)


class FolderDumpSchema(Schema):
    id = fields.UUID(dump_only=True)

    title = FolderTitleField(dump_only=True)
    color = FolderColorField(dump_only=True)

    parent_id = fields.UUID(dump_only=True)

    children_folders = fields.Nested("FolderDumpSchema", many=True)

    created = fields.DateTime(dump_only=True)
    updated = fields.DateTime(dump_only=True)


class FolderCreationSchema(Schema):
    title = FolderTitleField(required=True)
    color = FolderColorField()

    parent_id = fields.UUID(required=False, allow_none=True, missing=None)


class FolderUpdateSchema(Schema):
    title = FolderTitleField(required=False)
    color = FolderColorField(required=False)

    parent_id = fields.UUID(required=False)

    class Meta:
        unknown = EXCLUDE
