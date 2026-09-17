"""
PyLedger Core - Notes
General-purpose notes attached to any entity
"""

from datetime import datetime
from typing import Optional, List


class Note:
    def __init__(self, content: str, author: str,
                 entity_type: str = '', entity_id: str = '',
                 note_id: str = None):
        self.note_id = note_id or f"N-{id(self)}"
        self.content = content
        self.author = author
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.created_at = datetime.now()
        self.updated_at = self.created_at

    def edit(self, new_content: str) -> 'Note':
        self.content = new_content
        self.updated_at = datetime.now()
        return self

    def to_dict(self) -> dict:
        return {
            'note_id': self.note_id,
            'content': self.content,
            'author': self.author,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class NoteManager:
    def __init__(self):
        self.notes = []

    def add(self, content: str, author: str,
            entity_type: str = '', entity_id: str = '') -> Note:
        note = Note(content, author, entity_type, entity_id)
        self.notes.append(note)
        return note

    def get_by_entity(self, entity_type: str, entity_id: str) -> List[Note]:
        return [n for n in self.notes
                if n.entity_type == entity_type and n.entity_id == entity_id]

    def get_by_author(self, author: str) -> List[Note]:
        return [n for n in self.notes if n.author == author]

    def get_recent(self, limit: int = 10) -> List[Note]:
        sorted_notes = sorted(self.notes, key=lambda n: n.created_at, reverse=True)
        return sorted_notes[:limit]

    def delete(self, note_id: str) -> bool:
        for i, n in enumerate(self.notes):
            if n.note_id == note_id:
                del self.notes[i]
                return True
        return False

    def to_dict(self) -> list:
        return [n.to_dict() for n in self.notes]
