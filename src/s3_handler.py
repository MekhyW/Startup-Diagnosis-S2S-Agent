import boto3
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

load_dotenv(".env.local")
logger = logging.getLogger("s3_handler")

class S3Handler:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name='us-east-2'
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME not found in environment variables")
    
    async def upload_transcription(self, interview_id: str, transcription: str) -> Optional[str]:
        """ Upload the full transcription to S3 """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            s3_key = f"transcriptions/{interview_id}_{timestamp}.txt"
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=transcription.encode('utf-8'),
                ContentType='text/plain',
                Metadata={'interview_id': interview_id, 'upload_timestamp': timestamp, 'content_type': 'transcription'}
            )
            logger.info(f"Transcription uploaded successfully: {s3_key}")
            return s3_key
        except ClientError as e:
            logger.error(f"Failed to upload transcription: {e}")
            return None
    
    async def upload_report(self, interview_id: str, report_data: Dict[str, Any]) -> Optional[str]:
        """ Upload the structured report JSON to S3 """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            s3_key = f"reports/{interview_id}_{timestamp}.json"
            json_content = json.dumps(report_data, indent=2, ensure_ascii=False)
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json_content.encode('utf-8'),
                ContentType='application/json',
                Metadata={'interview_id': interview_id, 'upload_timestamp': timestamp, 'content_type': 'report', 'schema_version': '1.0'}
            )
            logger.info(f"Report uploaded successfully: {s3_key}")
            return s3_key
        except ClientError as e:
            logger.error(f"Failed to upload report: {e}")
            return None
