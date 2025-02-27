import psycopg2
import boto3 # type: ignore
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
load_dotenv()

# PostgreSQL Configuration
DB_PARAMS = {
    'dbname': 'flask_app',
    'user': 'sumant',
    'password': 'awhbharat',
    'host': 'localhost',
    'port': '5432'
}

# AWS S3 Configuration
S3_BUCKET = os.getenv("S3_BUCKET", "default")
S3_REGION = os.getenv("S3_REGION", "default")
S3_ACCESS_KEY=os.getenv("S3_ACCESS_KEY", "default")
S3_SECRET_KEY=os.getenv("S3_SECRET_KEY", "default")
s3 = boto3.client('s3', aws_access_key_id=S3_ACCESS_KEY, aws_secret_access_key=S3_SECRET_KEY)

def upload_image(image):
    filename = secure_filename(image.filename)
    #s3.upload_fileobj(image, S3_BUCKET, filename)
    #image_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{filename}"
    image_url="https://images.pexels.com/photos/1054666/pexels-photo-1054666.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
    return image_url
# Connect to PostgreSQL
def get_db_connection():
    return psycopg2.connect(**DB_PARAMS)