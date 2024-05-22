from enum import Enum
from datetime import datetime
from ..utils import db


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer(), primary_key=True)
    chat_id = db.Column(db.Integer(), db.ForeignKey('chats.id'), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    file_id = db.Column(db.Integer(), db.ForeignKey('files.id'), nullable=True)  # Nullable if a message doesn't have an associated file

    def __repr__(self):
        return f"<Message {self.id} in Chat {self.chat_id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()


class ResponseMessage(db.Model):
    __tablename__ = 'response_messages'
    id = db.Column(db.Integer(), primary_key=True)
    chat_id = db.Column(db.Integer(), db.ForeignKey('chats.id'), nullable=False)
    message_id = db.Column(db.Integer(), db.ForeignKey('messages.id'), nullable=False)  # Foreign key referencing the Message model
    title = db.Column(db.String(255), nullable=True)
    link = db.Column(db.String(255), nullable=True)
    chapter = db.Column(db.String(255), nullable=False)
    estimated_time = db.Column(db.Float(), nullable=False)  # In hours
    message = db.relationship("Message", backref="response_messages")  # Relationship to access the associated message

    def __repr__(self):
        return f"<ResponseMessage {self.id} in Chat {self.chat_id} for Message {self.message_id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()


class Chat(db.Model):
    __tablename__ = 'chats'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)
    messages = db.relationship('Message', backref='chat', lazy=True)
    files = db.relationship('File', backref='chat', lazy=True)  # Add this line to create the relationship between Chat and File
    response_messages = db.relationship('ResponseMessage', backref='chat', lazy=True)

    def __repr__(self):
        return f"<Chat {self.id} for User {self.user_id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()
