from datetime import datetime
from ..utils import db

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer(), primary_key=True)
    chat_id = db.Column(db.Integer(), db.ForeignKey('chats.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    file_id = db.Column(db.Integer(), db.ForeignKey('files.id', ondelete='SET NULL'), nullable=True)  # Nullable if a message doesn't have an associated file

    def __repr__(self):
        return f"<Message {self.id} in Chat {self.chat_id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

class ResponseMessage(db.Model):
    __tablename__ = 'response_messages'
    id = db.Column(db.Integer(), primary_key=True)
    chat_id = db.Column(db.Integer(), db.ForeignKey('chats.id', ondelete='CASCADE'), nullable=False)
    message_id = db.Column(db.Integer(), db.ForeignKey('messages.id', ondelete='CASCADE'), nullable=False)  # Foreign key referencing the Message model
    title = db.Column(db.String(255), nullable=True)
    link = db.Column(db.String(255), nullable=True)
    chapter = db.Column(db.String(255), nullable=True)
    estimated_time = db.Column(db.Float(), nullable=True)  # In hours
    message = db.relationship("Message", backref="response_messages")  # Relationship to access the associated message
    topics = db.Column(db.Text(), nullable=True)
    content = db.Column(db.Text(), nullable=True)

    def __repr__(self):
        return f"<ResponseMessage {self.id} in Chat {self.chat_id} for Message {self.message_id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

class Chat(db.Model):
    __tablename__ = 'chats'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    messages = db.relationship('Message', backref='chat', lazy=True, cascade="all, delete-orphan")
    files = db.relationship('File', backref='chat', lazy=True, cascade="all, delete-orphan")  # Add this line to create the relationship between Chat and File
    response_messages = db.relationship('ResponseMessage', backref='chat', lazy=True, cascade="all, delete-orphan")
    type = db.Column(db.Integer(), default=0)

    def __repr__(self):
        return f"<Chat {self.id} for User {self.user_id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
