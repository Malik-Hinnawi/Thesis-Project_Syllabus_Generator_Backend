from flask_restx import Namespace, Resource, fields
from flask import request, current_app
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.users import User
from ..models.chats import Chat, Message, ResponseMessage
from .helpers.generation_helper import (list_blobs_with_prefix,
                                        load_models_and_vectorizers,
                                        SyllabusGenerator,
                                        get_sorted_by_importance,
                                        delete_blobs
                                        )
from .helpers.q_and_a_helper import QAGenerator
from .helpers.youtube_helper import yh
from werkzeug.exceptions import BadRequest

chat_namespace = Namespace('chat', description='Used to store chats')

chat_model = chat_namespace.model(
    'Chat', {
        'id': fields.Integer,
        'type': fields.Integer()
    }
)

create_message_model = chat_namespace.model(
    'CreateMessage', {
        'content': fields.String(required=True, description="Content of the message"),
    }
)

delete_message_model = chat_namespace.model(
    'DeleteMessage', {
        'message': fields.String(description="Content of a message"),
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
        'chapter': fields.Integer(),
        'content': fields.String(),
        'topics': fields.String()
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

answer_model = chat_namespace.model(
    'AnswerMessage', {
        'id': fields.Integer(),
        'chat_id': fields.Integer(),
        'message_id': fields.Integer(),
        'title': fields.String(),
        'link': fields.String(),
        'content': fields.String()
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
        data = request.get_json()
        current_user_id = get_jwt_identity()
        if data['type'] not in [0, 1]:
            raise BadRequest("type should either be 0 (syllabus generator) or 1 (q and a)")
        new_chat = Chat(user_id=current_user_id, type=data['type'])
        new_chat.save()
        return new_chat, HTTPStatus.CREATED


@chat_namespace.route('/user/chats/<int:chat_id>')
class UserDeleteChats(Resource):
    @jwt_required()
    @chat_namespace.marshal_with(delete_message_model)
    def delete(self, chat_id):
        """
        Delete a chat for the current user
        """
        chat = Chat.query.filter_by(id=chat_id).first_or_404()
        chat.delete()
        response = {'message': 'Chat deleted successfully'}
        return response, HTTPStatus.OK


@chat_namespace.route('/<int:chat_id>/syllabus-generator')
class SyllabusGeneratorMessages(Resource):
    @jwt_required()
    @chat_namespace.expect(create_message_model)
    @chat_namespace.marshal_list_with(response_message_model)
    def post(self, chat_id):
        """
        Add a new message to a chat and get a syllabus generation as a response
        """
        models = list_blobs_with_prefix("models/")
        vectorizers = list_blobs_with_prefix("vectorizers/")
        data = request.get_json()

        current_user_id = get_jwt_identity()
        chat = Chat.query.filter_by(id=chat_id, user_id=current_user_id).first_or_404()
        if chat.type != 0:
            raise BadRequest("chat type should be 0 (syllabus generator)")

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

            content = f"""[Estimated time: {float(result[4])} HOURS] FROM '{result[0]}' BOOK,
             you should check chapter {str(result[2])}.\n\t
             Chapter {str(result[2])} Main Subjects:\n\t\t\t{str(result[3])}"""

            response_message = ResponseMessage(
                chat_id=chat_id,
                message_id=new_message.id,
                title=title,
                estimated_time=float(result[4]),
                chapter=str(result[2]),
                link=link,
                topics=result[3],
                content=content
            )
            response_message.save()
            response_messages.append(response_message)
            n += 1

        delete_blobs(vectorizers, models)
        return response_messages, HTTPStatus.CREATED


@chat_namespace.route('/<int:chat_id>/q-and-a')
class QAMessages(Resource):
    @jwt_required()
    @chat_namespace.expect(create_message_model)
    @chat_namespace.marshal_list_with(answer_model)
    def post(self, chat_id):
        """
        Add a new message to a chat and get a response
        """
        data = request.get_json()
        question = data['content']
        current_user_id = get_jwt_identity()
        chat = Chat.query.filter_by(id=chat_id, user_id=current_user_id).first_or_404()

        if chat.type != 1:
            raise BadRequest("chat type should be 1 (q and a)")

        # Create and save the user's message
        new_message = Message(chat_id=chat.id, content=question)
        new_message.save()

        link = yh.youtube_videos(question)
        q_a_generator = QAGenerator(current_app.model,
                                    current_app.tokenizer,
                                    'https://www.geeksforgeeks.org/'
                                    )
        title = None
        answer = q_a_generator.generate(question)
        if link is not None:
            temp = link
            link = temp[1]
            title = temp[0]

        response_message = ResponseMessage(chat_id=chat_id,
                                           message_id=new_message.id,
                                           content=answer,
                                           link=link,
                                           title=title
                                           )
        response_message.save()
        response_messages = [response_message]
        return response_messages, HTTPStatus.CREATED


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
