import boto3
import uuid
import os
from datetime import datetime
from typing import Optional, Dict, Any
from werkzeug.datastructures import FileStorage

import logging

class S3ImageService:
   def __init__(
       self, 
       bucket_name: str, 
       aws_access_key_id: Optional[str] = None,
       aws_secret_access_key: Optional[str] = None,
       region_name: str = 'us-east-1'
   ):
       """
       Service for uploading images to S3
       
       Args:
           bucket_name: S3 bucket name
           aws_access_key_id: Access key (optional if using environment variables)
           aws_secret_access_key: Secret key (optional if using environment variables)
           region_name: AWS region
       """
       self.bucket_name = bucket_name
       self.upload_prefix = 'uploads/'
       self.max_file_size = 10 * 1024 * 1024  # 10MB
       self.allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
       
       # Configure S3 client
       if aws_access_key_id and aws_secret_access_key:
           self.s3_client = boto3.client(
               's3',
               aws_access_key_id=aws_access_key_id,
               aws_secret_access_key=aws_secret_access_key,
               region_name=region_name
           )
       else:
           # Use default credentials (environment variables, IAM role, etc.)
           self.s3_client = boto3.client('s3', region_name=region_name)
       
       self.logger = logging.getLogger(__name__)

   def _validate_file(self, file: FileStorage) -> Dict[str, Any]:
       """
       Validates the file before uploading
       
       Args:
           file: File to validate
           
       Returns:
           Dict with validation result
       """
       if not file or file.filename == '':
           return {'valid': False, 'error': 'No file provided'}
       
       # Validate extension
       if not self._allowed_file(file.filename):
           return {'valid': False, 'error': 'File type not allowed'}
       
       # Validate size
       file.seek(0, 2)  # Go to end
       file_size = file.tell()
       file.seek(0)  # Return to beginning
       
       if file_size > self.max_file_size:
           return {'valid': False, 'error': f'File too large (maximum {self.max_file_size/1024/1024}MB)'}
       
       if file_size == 0:
           return {'valid': False, 'error': 'Empty file'}
       
       return {'valid': True, 'file_size': file_size}

   def _allowed_file(self, filename: str) -> bool:
       """
       Checks if the file extension is allowed
       """
       return '.' in filename and \
              filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

   def upload_image(self, file: FileStorage, custom_prefix: str = None) -> Dict[str, Any]:
       """
       Uploads an image to S3
       
       Args:
           file: Image file
           custom_prefix: Custom prefix for the path (optional)
           
       Returns:
           Dict with upload result
       """
       try:
           # Validate file
           validation = self._validate_file(file)
           if not validation['valid']:
               return {
                   'success': False,
                   'error': validation['error']
               }
           
           # Generate unique name
           prefix = custom_prefix if custom_prefix else self.upload_prefix
           file_extension = os.path.splitext(file.filename)[1].lower()
           unique_filename = f"{uuid.uuid4()}{file_extension}"
           object_key = f"{prefix}{unique_filename}"
           
           # Determine Content-Type
           content_type = file.content_type or self._get_content_type(file_extension)
           
           # Upload file to S3
           self.s3_client.upload_fileobj(
               file,
               self.bucket_name,
               object_key,
               ExtraArgs={
                   'ContentType': content_type,
                   'Metadata': {
                       'original_filename': file.filename,
                       'upload_date': datetime.now().isoformat(),
                       'file_size': str(validation['file_size'])
                   }
               }
           )
           
           self.logger.info(f"Image uploaded successfully: {object_key}")
           
           return {
               'success': True,
               'object_key': object_key,
               'original_filename': file.filename,
               'file_size': validation['file_size'],
               'content_type': content_type,
               'upload_date': datetime.now().isoformat()
           }
           
       except Exception as e:
           self.logger.error(f"Error uploading image: {str(e)}")
           return {
               'success': False,
               'error': f"Internal error: {str(e)}"
           }

   def upload_from_bytes(self, image_bytes: bytes, filename: str, custom_prefix: str = None) -> Dict[str, Any]:
       """
       Uploads image from bytes (useful for base64, PIL, etc.)
       
       Args:
           image_bytes: Image bytes
           filename: Filename
           custom_prefix: Custom prefix
           
       Returns:
           Dict with upload result
       """
       try:
           from io import BytesIO
           
           # Validate size
           if len(image_bytes) > self.max_file_size:
               return {
                   'success': False,
                   'error': f'Image too large (maximum {self.max_file_size/1024/1024}MB)'
               }
           
           if len(image_bytes) == 0:
               return {
                   'success': False,
                   'error': 'Empty image'
               }
           
           # Validate extension
           if not self._allowed_file(filename):
               return {
                   'success': False,
                   'error': 'File type not allowed'
               }
           
           # Generate unique name
           prefix = custom_prefix if custom_prefix else self.upload_prefix
           file_extension = os.path.splitext(filename)[1].lower()
           object_key = f"{prefix}/{filename.lower()}"
           
           # Determine Content-Type
           content_type = self._get_content_type(file_extension)
           
           # Upload to S3
           self.s3_client.upload_fileobj(
               BytesIO(image_bytes),
               self.bucket_name,
               object_key,
               ExtraArgs={
                   'ContentType': content_type,
                   'Metadata': {
                       'original_filename': filename,
                       'upload_date': datetime.now().isoformat(),
                       'file_size': str(len(image_bytes)),
                       'source': 'bytes'
                   }
               }
           )
           
           self.logger.info(f"Image uploaded from bytes: {object_key}")
           
           return {
               'success': True,
               'object_key': object_key,
               'original_filename': filename,
               'file_size': len(image_bytes),
               'content_type': content_type,
               'upload_date': datetime.now().isoformat()
           }
           
       except Exception as e:
           self.logger.error(f"Error uploading image from bytes: {str(e)}")
           return {
               'success': False,
               'error': f"Internal error: {str(e)}"
           }

   def _get_content_type(self, file_extension: str) -> str:
       """
       Gets the Content-Type based on file extension
       """
       content_types = {
           '.jpg': 'image/jpeg',
           '.jpeg': 'image/jpeg',
           '.png': 'image/png',
           '.gif': 'image/gif',
           '.webp': 'image/webp'
       }
       return content_types.get(file_extension.lower(), 'application/octet-stream')


   def image_exists(self, object_key: str) -> bool:
       """
       Checks if an image exists in S3
       
       Args:
           object_key: Object key
           
       Returns:
           bool: True if exists, False if not
       """
       try:
           self.s3_client.head_object(Bucket=self.bucket_name, Key=object_key)
           return True
       except:
           return False
