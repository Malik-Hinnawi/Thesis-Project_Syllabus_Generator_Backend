from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .auth.views import auth_namespace
from .chat.views import chat_namespace
from .file.views import file_namespace
from .config import config_dict
from .utils import db
from .models.users import User
from .models.files import File
from .models.chats import Message, Chat
from .models.links import Link
from flask_migrate import Migrate
from werkzeug.exceptions import NotFound, MethodNotAllowed
from transformers import BertForQuestionAnswering, BertTokenizer


def create_app(config=config_dict['dev']):
    app = Flask(__name__)
    app.config.from_object(config)

    def load_model_and_tokenizer():
        model_name = 'bert-large-uncased-whole-word-masking-finetuned-squad'
        app.model = BertForQuestionAnswering.from_pretrained(model_name)
        app.tokenizer = BertTokenizer.from_pretrained(model_name)
    load_model_and_tokenizer()

    CORS(app)

    authorizations = {
        "Bearer Auth": {
            'type': "apiKey",
            'in': 'header',
            'name': "Authorization",
            'description': "Add a JWT with ** Bearer &lt;JWT&gt; to authorize"
        }
    }

    api = Api(app,
              title="Syllabus Generator API",
              description="A REST API for an Syllabus Generator Service",
              authorizations=authorizations,
              security="Bearer Auth"
              )

    db.init_app(app)
    jwt = JWTManager(app)
    migrate = Migrate(app, db)

    @api.errorhandler(NotFound)
    def not_found(error):
        return {"error": "Not Found"}, 404

    @api.errorhandler(MethodNotAllowed)
    def not_found(error):
        return {"error": "Method Not allowed"}, 405

    api.add_namespace(auth_namespace, path='/api/auth')
    api.add_namespace(chat_namespace, path='/api/chat')
    api.add_namespace(file_namespace, path='/api/file')

    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'User': User,
            'File': File,
            'Chat': Chat,
            'Message': Message,
            'Link': Link,
        }
    return app
