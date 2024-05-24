import os
from flask import current_app


class AIUpload:
    def __init__(
        self,
        filename,
        size,
        ext,
        description=None,
        owner=None,
        tags=None,
        uploaded_by=None,
        upload_date=None,
        is_public=False,
        is_featured=False,
    ):
        self.filename = filename
        self.size = size
        self.ext = ext
        self.description = description
        self.owner = owner
        self.tags = tags or []
        self.uploaded_by = uploaded_by
        self.upload_date = upload_date
        self.is_public = is_public
        self.is_featured = is_featured

    @property
    def basedir(self):
        return os.path.abspath(
            os.path.join(os.path.dirname(__file__), f"../../../labs")
        )

    @property
    def filepath(self):
        return os.path.join(self.basedir, self.filename)

    def save(self):
        with open(self.filepath, "wb") as f:
            pass
