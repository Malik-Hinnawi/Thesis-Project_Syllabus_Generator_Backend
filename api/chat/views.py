from flask_restx import Namespace, Resource, fields
from flask import request
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.users import User
from ..models.chats import Chat, Message, ResponseMessage
from .helpers.generation_helper import (list_blobs_with_prefix,
                                        load_models_and_vectorizers,
                                        SyllabusGenerator,
                                        get_sorted_by_importance,
                                        print_output)
import numpy

chat_namespace = Namespace('chat', description='Used to store chats')

chat_model = chat_namespace.model(
    'Chat', {
        'id': fields.Integer()
    }
)



create_message_model = chat_namespace.model(
    'CreateMessage', {
        'content': fields.String(required=True, description="Content of the message"),
    }
)

response_message_model = chat_namespace.model(
    'ResponseMessage', {
        'id': fields.Integer(),
        'chat_id': fields.Integer(),
        'message_id': fields.Integer(),
        'title': fields.String(),
        'link': fields.String(),
        'estimated_time': fields.Float(),
        'chapter': fields.Integer()
    }
)

message_model = chat_namespace.model(
    'Message', {
        'id': fields.Integer(),
        'chat_id': fields.Integer(),
        'content': fields.String(),
        'timestamp': fields.DateTime(),
        'file_id': fields.Integer(),
        'response_messages': fields.List(fields.Nested(response_message_model)),
    }
)

@chat_namespace.route('/user/chats')
class UserChats(Resource):
    @jwt_required()
    @chat_namespace.marshal_list_with(chat_model)
    def get(self):
        """
        Get all chats for the current user
        """
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        return user.chats

    @jwt_required()
    @chat_namespace.expect(chat_model)
    @chat_namespace.marshal_with(chat_model)
    def post(self):
        """
        Create a new chat for the current user
        """
        current_user_id = get_jwt_identity()
        new_chat = Chat(user_id=current_user_id)
        new_chat.save()
        return new_chat, HTTPStatus.CREATED


@chat_namespace.route('/<int:chat_id>/messages')
class ChatMessages(Resource):
    @jwt_required()
    @chat_namespace.marshal_list_with(message_model)
    def get(self, chat_id):
        """
        Get all messages for a specific chat
        """
        current_user_id = get_jwt_identity()
        chat = Chat.query.filter_by(id=chat_id, user_id=current_user_id).first_or_404()
        messages = chat.messages

        # Fetch associated response messages for each message
        for message in messages:
            response_messages = ResponseMessage.query.filter_by(message_id=message.id).all()
            message.response_messages = response_messages

        return messages

    @jwt_required()
    @chat_namespace.expect(create_message_model)
    @chat_namespace.marshal_list_with(response_message_model)
    def post(self, chat_id):
        """
        Add a new message to a chat and get a response
        """
        models = list_blobs_with_prefix("models/")
        vectorizers = list_blobs_with_prefix("vectorizers/")
        data = request.get_json()

        current_user_id = get_jwt_identity()
        chat = Chat.query.filter_by(id=chat_id, user_id=current_user_id).first_or_404()

        # Create and save the user's message
        new_message = Message(chat_id=chat.id, content=data['content'])
        new_message.save()

        # Generate response messages
        model_dict = load_models_and_vectorizers(models, vectorizers)
        syllabus = SyllabusGenerator(data['content'], model_dict)
        syllabus.get_related_all_chapters()
        results = get_sorted_by_importance(syllabus.get_statistics_per_book())

        response_messages = []
        n = 1
        for result in results:
            title = None
            link = None
            if n == 1 and len(result) >= 6:
                title = str(result[5][0])
                link = str(result[5][1])

            response_message = ResponseMessage(
                chat_id=chat_id,
                message_id=new_message.id,
                title= title,
                estimated_time=float(result[4]),
                chapter=str(result[2]),
                link=link
            )
            response_message.save()
            response_messages.append(response_message)
            n+=1

        return response_messages, HTTPStatus.CREATED


@chat_namespace.route('/test')
class Test(Resource):
    def get(self):
        models = list_blobs_with_prefix("models/")
        vectorizers = list_blobs_with_prefix("vectorizers/")
        books = list_blobs_with_prefix("Books/")
        print("Models:", models)
        print("Vectorizers:", vectorizers)
        print("Books:", books)

        input_string_2 = """
        In computing, threads enable programs to execute multiple tasks simultaneously. 
        They divide the workload into smaller chunks, allowing for efficient resource allocation and parallel execution. 
        This enhances performance and responsiveness, akin to a juggler effortlessly managing multiple objects at once."""

        model_dict = load_models_and_vectorizers(models, vectorizers)
        syllabus = SyllabusGenerator(input_string_2,model_dict)
        syllabus.get_related_all_chapters()
        result = get_sorted_by_importance(syllabus.get_statistics_per_book())
        print_output(result)

        response = {"message": "helloworld"}
        return response, HTTPStatus.OK
