from sqlalchemy.orm import Session
from src.entrypoints.web.api.v1 import api_resource
from src.entrypoints.web.lib.decorators import auth_required
from src.entrypoints.web.errors.note import (
    HTTPNoteNotFound,
    HTTPNoteCreationError,
    HTTPNoteUpdateError,
    HTTPNoteRelationCreationError,
)
from src.entrypoints.web.errors.folder import (
    HTTPFolderNotFound,
)

from src.repositories.folders import SAFoldersRepo
from src.repositories.notes import SANotesRepo

from src.services.notes.creator import (
    NoteCreator,
    NoteCreationInput,
    NoteCreationError,
)

from src.services.notes.updater import (
    NoteUpdater,
    NoteUpdateError,
)

from src.services.notes.remover import (
    NoteRemover,
    NoteRemoveError,
)

from src.services.notes.relation_creator import (
    NoteRelationCreationError,
    NoteRelationCreator,
    NoteRelationCreationInput,
)

from src.services.notes.relation_remover import (
    NoteRelationRemover,
    NoteRelationRemoveError,
)

from src.schemas.note import (
    NoteDumpSchema,
    NoteCreationInputSchema,
    NoteUpdateSchema,
    NoteByIdParamsSchema,
    NotesCollectionParamsSchema,
    NoteRelationCreationBodySchema,
    NoteRelationCreationParamsSchema,
    NoteRelationRemoveParamsSchema,
)

from src.message_bus import MessageBusABC

from src.models.user import User

from logging import getLogger

logger = getLogger(__name__)


@api_resource("/notes")
class NotesCollectionHTTPController:
    @classmethod
    @auth_required()
    def on_get(cls, req, resp):
        req_params = NotesCollectionParamsSchema().load(req.params)

        current_user: User = req.context.get("current_user")
        db_session: Session = req.context.get("db_session")

        notes_repo = SANotesRepo(db_session)

        notes = notes_repo.list(
            title=req_params["title"],
            by_folder=req_params["by_folder"],
            folder_id=req_params["folder_id"],
            user_id=current_user.id,
        )

        note_dump_schema = NoteDumpSchema()

        result = []

        for note in notes:
            result.append({
                "note": note_dump_schema.dump(note)
            })

        resp.text = result


@api_resource("/note")
class NoteHTTPController:
    @classmethod
    @auth_required()
    def on_get(cls, req, resp):
        req_params = NoteByIdParamsSchema().load(req.params)

        current_user: User = req.context.get("current_user")
        db_session: Session = req.context.get("db_session")

        notes_repo = SANotesRepo(db_session)

        note = notes_repo.get(id_=req_params["note_id"], user_id=current_user.id)

        if note is None:
            raise HTTPNoteNotFound

        resp.text = {
            "note": NoteDumpSchema().dump(note)
        }

    @classmethod
    @auth_required()
    def on_post(cls, req, resp):
        req_body = NoteCreationInputSchema().load(req.text)

        current_user: User = req.context.get("current_user")
        db_session: Session = req.context.get("db_session")
        message_bus: MessageBusABC = req.context.get("message_bus")

        folders_repo = SAFoldersRepo(db_session)
        notes_repo = SANotesRepo(db_session)

        folder_id = req_body.pop("folder_id", None)
        folder = None

        if folder_id:
            folder = folders_repo.get(id_=folder_id, user_id=current_user.id)

            if folder is None:
                raise HTTPFolderNotFound

        creator = NoteCreator(notes_repo=notes_repo)

        try:
            note = creator.create(
                data=NoteCreationInput(
                    **req_body
                ),
                folder=folder,
                user_id=current_user.id
            )
        except NoteCreationError as e:
            raise HTTPNoteCreationError(message=e.message)

        db_session.commit()

        message_bus.batch_handle(
            creator.get_events(),
        )

        resp.text = {
            "note": NoteDumpSchema().dump(note)
        }

    @classmethod
    @auth_required()
    def on_patch(cls, req, resp):
        req_params = NoteByIdParamsSchema().load(req.params)
        req_body = NoteUpdateSchema().load(req.text)

        current_user: User = req.context.get("current_user")
        db_session: Session = req.context.get("db_session")
        message_bus: MessageBusABC = req.context.get("message_bus")

        folders_repo = SAFoldersRepo(db_session)
        notes_repo = SANotesRepo(db_session)

        note = notes_repo.get(id_=req_params["note_id"], user_id=current_user.id)

        if note is None:
            raise HTTPNoteNotFound

        updater = NoteUpdater(
            folders_repo=folders_repo,
        )

        try:
            note = updater.update(
                data=req_body,
                note=note,
                user_id=current_user.id,
            )
        except NoteUpdateError as e:
            raise HTTPNoteUpdateError(message=e.message)

        db_session.commit()

        message_bus.batch_handle(
            updater.get_events(),
        )

        resp.text = {
            "note": NoteDumpSchema().dump(note)
        }

    @classmethod
    @auth_required()
    def on_delete(cls, req, resp):
        req_params = NoteByIdParamsSchema().load(req.params)

        current_user: User = req.context.get("current_user")
        db_session: Session = req.context.get("db_session")
        message_bus: MessageBusABC = req.context.get("message_bus")

        notes_repo = SANotesRepo(db_session)

        note = notes_repo.get(id_=req_params["note_id"], user_id=current_user.id)

        if note is None:
            return

        remover = NoteRemover(
            notes_repo=notes_repo
        )

        try:
            remover.remove(
                note=note,
                user_id=current_user.id,
            )
        except NoteRemoveError:
            return

        db_session.commit()

        message_bus.batch_handle(
            remover.get_events(),
        )


@api_resource("/note-relation")
class NoteRelationHTTPController:
    @classmethod
    @auth_required()
    def on_patch(cls, req, resp):
        req_params = NoteRelationCreationParamsSchema().load(req.params)
        req_body = NoteRelationCreationBodySchema().load(req.text)

        current_user: User = req.context.get("current_user")
        db_session: Session = req.context.get("db_session")
        message_bus: MessageBusABC = req.context.get("message_bus")

        notes_repo = SANotesRepo(db_session)

        parent_note = notes_repo.get(id_=req_params["parent_note_id"], user_id=current_user.id)

        if parent_note is None:
            raise HTTPNoteNotFound(id_=req_params["parent_note_id"])

        child_note = notes_repo.get(id_=req_params["child_note_id"], user_id=current_user.id)

        if child_note is None:
            raise HTTPNoteNotFound(id_=req_params["child_note_id"])

        relation_creator = NoteRelationCreator()

        try:
            parent_note = relation_creator.create(
                data=NoteRelationCreationInput(
                    parent_note=parent_note,
                    child_note=child_note,
                    description=req_body["description"],
                ),
                user_id=current_user.id,
            )
        except NoteRelationCreationError as e:
            raise HTTPNoteRelationCreationError(message=e.message)

        db_session.commit()

        message_bus.batch_handle(
            relation_creator.get_events(),
        )

        resp.text = {
            "note": NoteDumpSchema().dump(parent_note)
        }

    @classmethod
    @auth_required()
    def on_delete(cls, req, resp):
        req_params = NoteRelationRemoveParamsSchema().load(req.params)

        current_user: User = req.context.get("current_user")
        db_session: Session = req.context.get("db_session")
        message_bus: MessageBusABC = req.context.get("message_bus")

        notes_repo = SANotesRepo(db_session)

        parent_note = notes_repo.get(id_=req_params["parent_note_id"], user_id=current_user.id)

        if parent_note is None:
            raise HTTPNoteNotFound(id_=req_params["parent_note_id"])

        child_note = notes_repo.get(id_=req_params["child_note_id"], user_id=current_user.id)

        if child_note is None:
            raise HTTPNoteNotFound(id_=req_params["child_note_id"])

        relation_remover = NoteRelationRemover()

        try:
            parent_note = relation_remover.remove(
                parent_note=parent_note,
                child_note=child_note,
                user_id=current_user.id,
            )
        except NoteRelationRemoveError:
            pass

        db_session.commit()

        message_bus.batch_handle(
            relation_remover.get_events(),
        )

        resp.text = {
            "note": NoteDumpSchema().dump(parent_note)
        }
