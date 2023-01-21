from sqlalchemy.orm import Session
from src.entrypoints.web.api.v1 import api_resource
from src.entrypoints.web.lib.decorators import auth_required
from src.entrypoints.web.errors.folder import (
    HTTPFolderNotFound,
    HTTPFolderCreationError,
)

from src.repositories.folders import SAFoldersRepo
from src.services.folders.creator import (
    FolderCreator,
    FolderCreationInput,
    FolderCreationError,
)

from src.schemas.folder import (
    FolderDumpSchema,
    FolderCreationSchema,
    FolderByIdParamsSchema,
)

from src.message_bus import MessageBusABC

from src.models.user import User

from uuid import UUID

from logging import getLogger

logger = getLogger(__name__)


@api_resource("/folder")
class FolderHTTPController:
    @classmethod
    @auth_required()
    def on_get(cls, req, resp):
        req_params = FolderByIdParamsSchema().load(req.params)

        current_user: User = req.context.get("current_user")
        db_session: Session = req.context.get("db_session")

        folders_repo = SAFoldersRepo(db_session)

        folder = folders_repo.get(id_=req_params["folder_id"], user_id=UUID(current_user.id))

        if folder is None:
            raise HTTPFolderNotFound

        resp.text = FolderDumpSchema().dump(folder)

    @classmethod
    @auth_required()
    def on_post(cls, req, resp):
        req_body = FolderCreationSchema().load(req.text)

        current_user: User = req.context.get("current_user")
        db_session: Session = req.context.get("db_session")
        message_bus: MessageBusABC = req.context.get("message_bus")

        folders_repo = SAFoldersRepo(db_session)
        creator = FolderCreator(
            folders_repo=folders_repo,
        )

        try:
            folder = creator.create(
                data=FolderCreationInput(
                    **req_body
                ),
                user_id=UUID(current_user.id)
            )
        except FolderCreationError:
            raise HTTPFolderCreationError

        db_session.commit()

        message_bus.batch_handle(
            creator.get_events(),
        )

        resp.text = FolderDumpSchema().dump(folder)
