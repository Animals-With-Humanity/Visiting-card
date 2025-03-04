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

def get_url(file_name,file_type):
    try:
        presigned_url = s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": S3_BUCKET, "Key": S3_ACCESS_KEY, "ContentType": file_type},
            ExpiresIn=300,  # URL valid for 5 minutes
        )
        public_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{S3_ACCESS_KEY}"
        return presigned_url,public_url
    except Exception as e:
        return ""


