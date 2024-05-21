from ..utils import db
from datetime import datetime


class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)
    file_name = db.Column(db.String(100), nullable=False)
    file_data = db.Column(db.Text(), nullable=False)  # Base64 encoded file content
    uploaded_at = db.Column(db.DateTime(), default=datetime.utcnow)
    chat_id = db.Column(db.Integer(), db.ForeignKey('chats.id'), nullable=False)
    messages = db.relationship('Message', backref='file', lazy=True)  # Add this line to create the relationship between File and Message

    def __repr__(self):
        return f"<File {self.file_name} for User {self.user_id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)