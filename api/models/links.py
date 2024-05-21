from ..utils import db


class Link(db.Model):
    __tablename__ = 'links'
    id = db.Column(db.Integer(), primary_key=True)
    chat_id = db.Column(db.Integer(), db.ForeignKey('chats.id'), nullable=False)
    url = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Link {self.id} in Chat {self.chat_id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)