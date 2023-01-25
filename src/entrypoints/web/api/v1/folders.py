from sqlalchemy.orm import Session
from src.entrypoints.web.api.v1 import api_resource
from src.entrypoints.web.lib.decorators import auth_required
from src.entrypoints.web.errors.folder import (
    HTTPFolderNotFound,
    HTTPFolderCreationError,
    HTTPFolderUpdateError,
)

from src.repositories.folders import SAFoldersRepo
from src.services.folders.creator import (
    FolderCreator,
    FolderCreationInput,
    FolderCreationError,
)

from src.services.folders.updater import (
    FolderUpdater,
    FolderUpdateError,
)

from src.services.folders.remover import (
    FolderRemover,
    FolderRemoveError
)

from src.schemas.folder import (
    FolderDumpSchema,
    FolderCreationSchema,
    FolderByIdParamsSchema,
    FolderUpdateSchema,
    FoldersCollectionParamsSchema,
)

from src.message_bus import MessageBusABC

from src.models.user import User

from logging import getLogger

logger = getLogger(__name__)


@api_resource("/folders")
class FoldersCollectionHTTPController:
    @classmethod
    @auth_required()
    def on_get(cls, req, resp):
        req_params = FoldersCollectionParamsSchema().load(req.params)

        current_user: User = req.context.get("current_user")
        db_session: Session = req.context.get("db_session")

        folders_repo = SAFoldersRepo(db_session)

        folders = folders_repo.list(
            title=req_params["title"],
            user_id=current_user.id,
            parent_id=req_params["parent_id"],
        )

        folder_dump_schema = FolderDumpSchema()

        result = []

        for folder in folders:
            result.append({
                "folder": folder_dump_schema.dump(folder)
            })

        resp.text = result


@api_resource("/folder")
class FolderHTTPController:
    @classmethod
    @auth_required()
    def on_get(cls, req, resp):
        req_params = FolderByIdParamsSchema().load(req.params)

        current_user: User = req.context.get("current_user")
        db_session: Session = req.context.get("db_session")

        folders_repo = SAFoldersRepo(db_session)

        folder = folders_repo.get(id_=req_params["folder_id"], user_id=current_user.id)

        if folder is None:
            raise HTTPFolderNotFound

        resp.text = {
            "folder": FolderDumpSchema().dump(folder)
        }

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
                user_id=current_user.id,
            )
        except FolderCreationError:
            raise HTTPFolderCreationError

        db_session.commit()

        message_bus.batch_handle(
            creator.get_events(),
        )

        resp.text = {
            "folder": FolderDumpSchema().dump(folder)
        }

    @classmethod
    @auth_required()
    def on_patch(cls, req, resp):
        req_params = FolderByIdParamsSchema().load(req.params)
        req_body = FolderUpdateSchema().load(req.text)

        current_user: User = req.context.get("current_user")
        db_session: Session = req.context.get("db_session")
        message_bus: MessageBusABC = req.context.get("message_bus")

        folders_repo = SAFoldersRepo(db_session)

        folder = folders_repo.get(id_=req_params["folder_id"], user_id=current_user.id)

        if folder is None:
            raise HTTPFolderNotFound

        updater = FolderUpdater(
            folders_repo=folders_repo,
        )

        try:
            folder = updater.update(
                data=req_body,
                folder=folder,
                user_id=current_user.id,
            )
        except FolderUpdateError:
            raise HTTPFolderUpdateError

        db_session.commit()

        message_bus.batch_handle(
            updater.get_events(),
        )

        resp.text = {
            "folder": FolderDumpSchema().dump(folder)
        }

    @classmethod
    @auth_required()
    def on_delete(cls, req, resp):
        req_params = FolderByIdParamsSchema().load(req.params)

        current_user: User = req.context.get("current_user")
        db_session: Session = req.context.get("db_session")
        message_bus: MessageBusABC = req.context.get("message_bus")

        folders_repo = SAFoldersRepo(db_session)

        folder = folders_repo.get(id_=req_params["folder_id"], user_id=current_user.id)

        if folder is None:
            return

        remover = FolderRemover(
            folders_repo=folders_repo,
        )

        try:
            remover.remove(
                folder=folder,
                user_id=current_user.id,
            )
        except FolderRemoveError:
            return

        db_session.commit()

        message_bus.batch_handle(
            remover.get_events(),
        )
