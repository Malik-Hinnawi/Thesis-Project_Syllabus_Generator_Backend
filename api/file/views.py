from flask_restx import Namespace, Resource, fields
from flask import request, current_app
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
from google.cloud import storage
from ..models.chats import Chat
from ..models.files import File
from datetime import datetime
import base64

file_namespace = Namespace('file', description='Operations related to file uploads and downloads')

file_model = file_namespace.model(
    'File', {
        'id': fields.Integer(),
        'user_id': fields.Integer(),
        'chat_id': fields.Integer(required=True, description="ID of the chat"),
        'file_name': fields.String(required=True, description="Name of the file"),
        'file_data': fields.String(description="URL of the file"),
        'uploaded_at': fields.DateTime(description="Timestamp of the file upload"),
    }
)

upload_file_model = file_namespace.model(
    'UploadFile', {
        'chat_id': fields.Integer(required=True, description="ID of the chat"),
        'file_name': fields.String(required=True, description="Name of the file"),
    }
)


def upload_to_gcs(bucket_name, destination_blob_name, file):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_file(file, content_type=file.content_type)

    return blob.public_url


@file_namespace.route('/upload')
class UploadFile(Resource):
    @jwt_required()
    @file_namespace.expect(upload_file_model)
    @file_namespace.marshal_with(file_model, code=HTTPStatus.CREATED)
    def post(self):
        """
        Upload a new file to a specific chat
        """
        if 'file' not in request.files:
            return {"message": "No file part in the request"}, HTTPStatus.BAD_REQUEST

        file = request.files['file']
        if file.filename == '':
            return {"message": "No file selected for uploading"}, HTTPStatus.BAD_REQUEST

        data = request.form
        current_user_id = get_jwt_identity()
        chat_id = data.get('chat_id')
        chat = Chat.query.filter_by(id=chat_id, user_id=current_user_id).first_or_404()

        file_name = file.filename
        bucket_name = current_app.config['GOOGLE_CLOUD_BUCKET']
        destination_blob_name = f"user_{current_user_id}/chat_{chat_id}/{file_name}"
        file_url = upload_to_gcs(bucket_name, destination_blob_name, file)
        print("File URL:" + file_url)

        new_file = File(
            user_id=current_user_id,
            chat_id=chat_id,
            file_name=file_name,
            file_data=file_url,  # Store the URL instead of the file data
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
