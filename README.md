# Syllabus Generator Backend Project

## Overview
This project is a backend implementation for a Syllabus Generator, designed to create detailed syllabi and answer related questions. The backend is built using the Flask framework and integrates a BERT model trained on academic content.

## Requirements
The dependencies for this project are listed in the `requirements.txt` file. To install them, run:

```bash
pip install -r requirements.txt
```
## Tools Used
- **Flask Framework**: The project is developed using Flask, a lightweight web framework for building RESTful APIs.
-** BERT Model**: A pre-trained BERT model fine-tuned on 10 PDF books. This model is utilized for flat hierarchical classification tasks.

## Models

### BERT Model:
- **Training Data**: The BERT model is trained on a dataset of 10 academic PDF books.
- **Vectorization**: The content from these books is vectorized to facilitate efficient classification.
- **Classification Task**: The model is designed for flat hierarchical classification, making it suitable for organizing and generating structured syllabi.

## Modes of Operation:

### 1. Syllabus Generator
- **Purpose**: Generates a structured syllabus based on input parameters.
- **Output**: A comprehensive syllabus tailored to the user's requirements.

### 2. Q&A Mode
- **Purpose**: Answers user questions related to the syllabus content.
- **Additional Feature**: Provides YouTube links as recommendations to enhance learning and understanding.

## Backend Responsibility

- **Malik Nizar Asad Al Hinnawi**: Responsible for the development and maintenance of the backend API, integrating the machine learning model, and ensuring smooth interaction between the frontend and backend components.

## Other Collaborators:
- **Çağın Tunç**: Machine Learning Engineering - Responsible for training and fine-tuning the BERT model.
- **Halil Can Uyanık**: Frontend Development - Responsible for designing and implementing the user interface that interacts with the backend.

## License:
Can be seen under LICENSE in the main branch
## Contact:
For any questions or issues, please reach out to the project maintainers:

- Malik Nizar Asad Al Hinnawi: malikhinnawi01@gmail.com
- Çağın Tunç: cagintunc@hotmail.com
- Halil Can Uyanık: halil.can023@gmail.com 
