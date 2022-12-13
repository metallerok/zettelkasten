from src.models.note import Note, NoteColor, NoteTitle, NoteToNoteRelation
from uuid import uuid4


def test_note_model(db_session):
    original_note = Note(
        id=str(uuid4()),
        title=NoteTitle("Original note"),
        color=NoteColor("#fff333"),
    )

    related_note = Note(
        id=str(uuid4()),
        title=NoteTitle("Related note"),
        color=NoteColor("#fff333"),
    )

    original_note.notes_relations.append(
        NoteToNoteRelation(
            id=str(uuid4()),
            child_note_id=related_note.id,
        )
    )

    db_session.add(original_note)
    db_session.add(related_note)

    db_session.commit()
    db_session.expire_all()

    assert len(original_note.notes_relations) == 1
    assert original_note.notes_relations[0].child_note == related_note
