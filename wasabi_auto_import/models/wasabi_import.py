import boto3
import logging
from odoo import models, api

_logger = logging.getLogger(__name__)

class WasabiAutoImport(models.Model):
    _name = 'wasabi.auto.import'
    _description = 'Wasabi Auto Attachment Import'

    @api.model
    def auto_import_from_wasabi(self):
        icp = self.env['ir.config_parameter'].sudo()

        # 🔐 Get credentials from settings
        access_key = icp.get_param('amazon_s3_connector.amazon_access_key')
        secret_key = icp.get_param('amazon_s3_connector.amazon_secret_key')
        bucket_name = icp.get_param('amazon_s3_connector.amazon_bucket_name')
        endpoint_url = icp.get_param('amazon_s3_connector.amazon_endpoint_url')
        connector_enabled = icp.get_param('amazon_s3_connector.amazon_connector')

        # Stop if connector disabled
        if connector_enabled != 'True':
            _logger.info("Amazon S3 Connector is disabled.")
            return

        if not all([access_key, secret_key, bucket_name, endpoint_url]):
            _logger.error("Missing S3 configuration parameters.")
            return

        # Wasabi always uses region_name='us-east-1' for API
        region_name = 'us-east-1'

        try:
            s3 = boto3.client(
                's3',
                endpoint_url=endpoint_url,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region_name
            )

            response = s3.list_objects_v2(Bucket=bucket_name)

            if 'Contents' not in response:
                return

            for obj in response['Contents']:
                file_key = obj['Key']

                # Skip folders
                if file_key.endswith('/'):
                    continue

                # Check if already imported
                existing = self.env['ir.attachment'].search([
                    ('wasabi_key', '=', file_key)
                ], limit=1)
                if existing:
                    continue

                # Download file
                file_obj = s3.get_object(Bucket=bucket_name, Key=file_key)
                file_content = file_obj['Body'].read()

                # ✅ Create attachment correctly (datas filled)
                self.env['ir.attachment'].create({
                    'name': file_key.split('/')[-1],
                    'type': 'binary',
                    'raw': file_content,  # Use raw so Odoo handles base64 internally
                    'mimetype': 'application/octet-stream',
                    'wasabi_key': file_key,
                })

                _logger.info(f"Imported file: {file_key}")

        except Exception as e:
            _logger.error(f"S3 Import Error: {str(e)}")