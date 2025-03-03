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
DB_PARAMS = {
    'dbname': os.getenv('dbname'),   # Make sure this matches your DB name
    'user': os.getenv('user'),        # Your Postgres username
    'password': os.getenv('password'), # Your Postgres password
    'host': os.getenv('host'),
    'port': os.getenv('port')
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

def base64_to_file(base64_str, filename="uploaded_image.png"):
    """Converts a Base64 string to a file-like object"""
    if not base64_str or ',' not in base64_str:
        return None  # Handle invalid Base64 input
    
    encoded = base64_str.split(',', 1)[1]  # Remove "data:image/png;base64,"
    img_data = base64.b64decode(encoded)
    img_io = io.BytesIO(img_data)
    return FileStorage(stream=img_io, filename=filename, content_type="image/png")

def upload_image(image):
    """
    Uploads the image to S3.
    Returns the image URL.
    """
    filename = secure_filename(image.filename)
    try:
        s3.upload_fileobj(image, S3_BUCKET, filename)
        image_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{filename}"
        return image_url
    except Exception as e:
        print(f"S3 Upload Failed: {e}")
        return None  # Handle upload failure

