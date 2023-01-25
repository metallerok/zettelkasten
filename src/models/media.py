import sqlalchemy as sa
from src.models.primitives.base import SAUUID
from depot.fields.sqlalchemy import UploadedFileField
from depot.manager import DepotManager
from depot.fields.upload import UploadedFile
from PIL import Image
from depot.io import utils
from tempfile import SpooledTemporaryFile
from depot.io.interfaces import FileStorage
from .meta import Base
from uuid import uuid4, UUID


class UploadedImageWithThumb(UploadedFile):
    max_size = 1024
    thumbnail_format = 'PNG'
    thumbnail_size = (128, 128)

    def process_content(self, content, filename=None, content_type=None):
        orig_content = content
        content = utils.file_from_content(content)
        __, filename, content_type = FileStorage.fileinfo(orig_content)

        super(UploadedImageWithThumb, self).process_content(content, filename, content_type)

        if "image/" in content_type:
            uploaded_image = Image.open(content)
            if max(uploaded_image.size) >= self.max_size:
                uploaded_image.thumbnail((self.max_size, self.max_size), Image.BILINEAR)
                content = SpooledTemporaryFile(utils.INMEMORY_FILESIZE)
                uploaded_image.save(content, uploaded_image.format)

            thumbnail = uploaded_image.copy()
            thumbnail.thumbnail(self.thumbnail_size, Image.ANTIALIAS)
            thumbnail = thumbnail.convert('RGBA')
            thumbnail.format = self.thumbnail_format

            output = SpooledTemporaryFile(utils.INMEMORY_FILESIZE)
            thumbnail.save(output, self.thumbnail_format)
            output.seek(0)

            thumb_path, thumb_id = self.store_content(
                output,
                'thumb.%s' % self.thumbnail_format.lower()
            )
            self['thumb_id'] = thumb_id
            self['thumb_path'] = thumb_path

            thumbnail_file = self.thumb_file
            self['_thumb_public_url'] = thumbnail_file.public_url

    @property
    def thumb_file(self):
        return self.depot.get(self.thumb_id)

    @property
    def thumb_url(self):
        public_url = self['_thumb_public_url']
        if public_url:
            return public_url
        return DepotManager.get_middleware().url_for(self['thumb_path'])


class Media(Base):
    __tablename__ = 'media'

    id: UUID = sa.Column(SAUUID, primary_key=True, default=lambda: uuid4())

    md5 = sa.Column(sa.String(32), nullable=False)
    file = sa.Column(UploadedFileField(upload_type=UploadedImageWithThumb), nullable=False)

    created = sa.Column(sa.DateTime, default=sa.func.now())
    updated = sa.Column(sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())
    deleted = sa.Column(sa.DateTime, nullable=True)
