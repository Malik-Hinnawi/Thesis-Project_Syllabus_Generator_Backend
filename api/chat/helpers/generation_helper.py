import joblib
import os
import math
from .youtube_helper import yh
import csv
from google.cloud import storage
from flask import current_app
import tempfile


def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    print(f"Blob {source_blob_name} downloaded to {destination_file_name}.")


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to {destination_blob_name}.")


def delete_blobs(vectorizers, models):
    """
    Delete vectorizer and model files
    """
    for path in vectorizers + models:
        try:
            os.remove(path)
            print(f"Deleted file: {path}")
        except FileNotFoundError:
            print(f"File not found: {path}")
        except Exception as e:
            print(f"Error occurred while deleting file {path}: {e}")


def get_hours(x):
    output = 1
    if x >= 0.5:
        output = (48 * x ** 2) + 2
    elif x >= 0.4:
        output = (28 * x ** 2) + ((2 * x) ** 4)
    elif x >= 0.3:
        output = (12 * x ** 2) + ((1.5 * x) ** 3)
    elif x >= 0.2:
        output = (6 * x ** 2)

    return math.ceil(max(output, 1))


def get_unit(book, chapter):
    bucket_name = current_app.config["GOOGLE_CLOUD_BUCKET"]
    book_files = {
        "computer_architecture_book": "csv/computer_architecture.csv",
        "data_intensive_book": "csv/data_intensive.csv",
        "ethic_1": "csv/ethics_1.csv",
        "ethic_2": "csv/ethics_2.csv",
        "os_book": "csv/os.csv",
        "hci": "csv/HCI.csv",
        "JavaScript": "csv/JavaScript.csv",
        "network_1": "csv/network_1.csv",
        "Robot_OS": "csv/Robot_OS.csv",
        "Robotic_python": "csv/Robotics_python.csv"
    }

    flattened_contents = {}

    if book in book_files:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file_name = tmp_file.name
            download_blob(bucket_name, book_files[book], tmp_file_name)

            with open(tmp_file_name, mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 2:
                        key = row[0].strip()
                        value = row[1].strip()
                        flattened_contents[key] = value

    if flattened_contents:
        normalized_dict = {str(key): value for key, value in flattened_contents.items()}
        return normalized_dict.get(str(chapter), None)

    return None


def list_blobs_with_prefix(prefix):
    """Lists all the blobs in the bucket that begin with the prefix."""
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(current_app.config["GOOGLE_CLOUD_BUCKET"], prefix=prefix)

    file_paths = []
    for blob in blobs:
        # Exclude folder names (if any) from the results
        if not blob.name.endswith('/'):
            file_paths.append(blob.name)

    return file_paths


def split_text(text, segment_size):
    words = text.split()
    segments = [words[i:i+segment_size] for i in range(0, len(words), segment_size)]
    return [' '.join(segment) for segment in segments]


def predicted_probabilities(input_string, model, vectorizer):
    segment_size = 300
    input_segments = split_text(input_string, segment_size)
    input_features = vectorizer.transform(input_segments).toarray()
    predicted_prob = model.predict_proba(input_features)
    result = zip(predicted_prob[0], model.classes_)
    return result


def get_key_words(content):
    exclude_list = ["overview", "summary", "intro", "introduction",
                    "abstraction", "background", "start"]
    result = ""
    number = 0
    if "," in content:
        tmp = content.split(",")
        for word in tmp:
            word = word.strip().rstrip().lower()
            if not (word in exclude_list):
                result += word + " "
                number += 1
                if number == 2:
                    return result + "in computer science"
    else:
        tmp = content.split(" ")
        for word in tmp:
            word = word.strip().rstrip().lower()
            result += word + " "
            number += 1
            if number >= 8:
                return result + "in computer science"


def get_sorted_by_importance(result):
    output = []
    tmp = [i[1] for i in result]
    tmp.sort(reverse=True)
    for t in tmp:
        for j in result:
            if t == j[1]:
                output.append(j)
    if len(output) > 0:
        output[0].append(yh.youtube_videos(get_key_words(output[0][3])))
    return output


def load_models_and_vectorizers(models, vectorizers):
    """Downloads and loads models and vectorizers from Google Cloud Storage."""
    bucket_name = current_app.config["GOOGLE_CLOUD_BUCKET"]
    model_dict = {}

    for model_path in models:
        model_name = os.path.basename(model_path).split("-")[0]
        with tempfile.NamedTemporaryFile(delete=False) as tmp_model_file:
            download_blob(bucket_name, model_path, tmp_model_file.name)
            model = joblib.load(tmp_model_file.name)

        vectorizer_path = f"vectorizers/{model_name}-vectorizer.joblib"
        with tempfile.NamedTemporaryFile(delete=False) as tmp_vectorizer_file:
            download_blob(bucket_name, vectorizer_path, tmp_vectorizer_file.name)
            vectorizer = joblib.load(tmp_vectorizer_file.name)

        model_dict[model_name] = [model, vectorizer]

    return model_dict


class SyllabusGenerator:
    _text_data = None
    _main_book = None
    _models = {}
    BOOK_INFO = {}

    def __init__(self, text_data, models):
        self._text_data = text_data
        self._models = models
        self.BOOK_INFO = {
            "computer_architecture_book": ["Computer as components: Wayne Wolf", None],
            "data_intensive_book": ["Designing data intensive applications: O'REILLY", None],
            "ethic_1": ["Ethics in IT: George W.Reynolds", None],
            "ethic_2": ["Ethics for the information age: Michael J. Quinn", None],
            "os_book": ["Operating System Concepts: WILEY", None],
            "hci": ["Human Computer Interaction", None],
            "JavaScript": ["Javascript Cookbook", None],
            "network_1": ["Computer Networking", None],
            "Robot_OS": ["Robot Operating Systems", None],
            "Robotic_python": ["Robotics with Python", None]
        }

    def get_related_all_chapters(self):
        for model in self._models.keys():
            probabilities = predicted_probabilities(self._text_data,
                                                    self._models[model][0], self._models[model][1])
            self.BOOK_INFO[model][1] = probabilities

    def get_statistics_per_book(self):
        result = []
        for i in self.BOOK_INFO.keys():
            book = self.BOOK_INFO[i]
            for j in list(book[1]):
                if float(j[0]) > 0.30:
                    unit_content = get_unit(i, j[1])
                    result.append([book[0], j[0], j[1],
                                   unit_content, get_hours(float(j[0]))])
        return result
