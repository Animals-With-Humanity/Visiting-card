import psycopg2
import boto3
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
import base64
import io
from werkzeug.datastructures import FileStorage

load_dotenv()

# PostgreSQL Configuration
# DB_PARAMS = {
#     'dbname': os.getenv('dbname'),   # Make sure this matches your DB name
#     'user': os.getenv('user'),        # Your Postgres username
#     'password': os.getenv('password'), # Your Postgres password
#     'host': os.getenv('host'),
#     'port': os.getenv('port')
# }
DB_PARAMS = {
    'dbname': 'flask_app',   # Make sure this matches your DB name
    'user': 'postgres',        # Your Postgres username
    'password': 'password', # Your Postgres password
    'host': 'localhost',
    'port': '5432'
}


# AWS S3 Configuration (optional - only if you want real S3 image uploads)
S3_BUCKET = os.getenv("S3_BUCKET", "default")
S3_REGION = os.getenv("S3_REGION", "default")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "default")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "default")

s3 = boto3.client(
    's3',
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY
)

def get_db_connection():
    """
    Connects to PostgreSQL using the above DB_PARAMS.
    """
    return psycopg2.connect(**DB_PARAMS)
def upload_file(file):
    if file.filename == "":
            return "No selected file"

    filename = secure_filename(file.filename)
    file_key = f"{filename}"  # Organizing files in an 'uploads' folder

    try:
        # s3.upload_fileobj(file, S3_BUCKET, file_key)
        # file_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{file_key}"
        file_url = "https://images.pexels.com/photos/1054666/pexels-photo-1054666.jpeg"
        return file_url
    except Exception as e:
        print("error",e)


