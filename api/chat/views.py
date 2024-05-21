from flask_restx import Namespace, Resource, fields
from flask import request
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.users import User
from ..models.chats import Chat, Message

chat_namespace = Namespace('chat', description='Used to store chats')

chat_model = chat_namespace.model(
    'Chat', {
        'id': fields.Integer()
    }
)

message_model = chat_namespace.model(
    'Message', {
        'id': fields.Integer(),
        'chat_id': fields.Integer(required=True, description="ID of the chat"),
        'content': fields.String(required=True, description="Content of the message"),
        'timestamp': fields.DateTime(description="Timestamp of the message"),
        'type': fields.Integer(description="Type of the message: 0 for request, 1 for response"),
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
        'content': fields.String(),
        'timestamp': fields.DateTime(),
        'type': fields.Integer(description="Type of the message: 0 for request, 1 for response"),
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
        return chat.messages

    @jwt_required()
    @chat_namespace.expect(create_message_model)
    @chat_namespace.marshal_with(response_message_model)
    def post(self, chat_id):
        """
        Add a new message to a chat and get a response
        """
        data = request.get_json()
        current_user_id = get_jwt_identity()
        chat = Chat.query.filter_by(id=chat_id, user_id=current_user_id).first_or_404()

        # Create and save the user's message
        new_message = Message(chat_id=chat.id, content=data['content'], type=0)
        new_message.save()

        # Generate a response message (dummy response for this example)
        response_content = f"Response to '{data['content']}'"
        response_message = Message(chat_id=chat.id, content=response_content, type=1)
        response_message.save()

        return response_message, HTTPStatus.CREATED


