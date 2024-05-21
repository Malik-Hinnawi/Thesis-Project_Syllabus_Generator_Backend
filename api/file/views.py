from flask_restx import Namespace, Resource, fields
from flask import request
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.chats import Chat
from ..models.files import File
from datetime import datetime

file_namespace = Namespace('file', description='Operations related to file uploads and downloads')

file_model = file_namespace.model(
    'File', {
        'id': fields.Integer(),
        'user_id': fields.Integer(),
        'chat_id': fields.Integer(required=True, description="ID of the chat"),
        'file_name': fields.String(required=True, description="Name of the file"),
        'file_data': fields.String(required=True, description="Base64 encoded file data"),
        'uploaded_at': fields.DateTime(description="Timestamp of the file upload"),
    }
)

upload_file_model = file_namespace.model(
    'UploadFile', {
        'chat_id': fields.Integer(required=True, description="ID of the chat"),
        'file_name': fields.String(required=True, description="Name of the file"),
        'file_data': fields.String(required=True, description="Base64 encoded file data"),
    }
)


@file_namespace.route('/upload')
class UploadFile(Resource):
    @jwt_required()
    @file_namespace.expect(upload_file_model)
    @file_namespace.marshal_with(file_model, code=HTTPStatus.CREATED)
    def post(self):
        """
        Upload a new file to a specific chat
        """
        data = request.get_json()
        current_user_id = get_jwt_identity()
        chat_id = data.get('chat_id')
        chat = Chat.query.filter_by(id=chat_id, user_id=current_user_id).first_or_404()

        new_file = File(
            user_id=current_user_id,
            chat_id=chat_id,
            file_name=data.get('file_name'),
            file_data=data.get('file_data'),
            uploaded_at=datetime.utcnow()
        )

        new_file.save()

        return new_file, HTTPStatus.CREATED


@file_namespace.route('/<int:chat_id>/files')
class GetFiles(Resource):
    @jwt_required()
    @file_namespace.marshal_list_with(file_model)
    def get(self, chat_id):
        """
        Get all files for a specific chat
        """
        current_user_id = get_jwt_identity()
        chat = Chat.query.filter_by(id=chat_id, user_id=current_user_id).first_or_404()
        files = File.query.filter_by(chat_id=chat.id).all()

        return files, HTTPStatus.OK
