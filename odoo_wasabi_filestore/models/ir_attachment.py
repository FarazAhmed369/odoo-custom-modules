# import boto3
# import base64
# from odoo import models
#
# class IrAttachment(models.Model):
#     _inherit = 'ir.attachment'
#
#     def _get_s3_client(self):
#         return boto3.client(
#             's3',
#             endpoint_url='https://s3.us-west-1.wasabisys.com',  # ✅ Updated
#             aws_access_key_id='PRYZAPJD78J66SD9Y0CK',
#             aws_secret_access_key='uuLFpaSijDAAhTlrljFADoXJoo1qR5ZVcmalwvAs',
#         )
#
#     def _file_write(self, value, checksum):
#         bin_value = base64.b64decode(value)
#         s3 = self._get_s3_client()
#
#         bucket = 'new-local-bucket'   # ✅ Updated bucket name
#         key = f"{self._cr.dbname}/{checksum}"
#
#         s3.put_object(
#             Bucket=bucket,
#             Key=key,
#             Body=bin_value,
#         )
#
#         return key
#
#     def _file_read(self, fname):
#         s3 = self._get_s3_client()
#         bucket = 'new-local-bucket'
#
#         obj = s3.get_object(
#             Bucket=bucket,
#             Key=fname
#         )
#
#         return base64.b64encode(obj['Body'].read())
#
#     def _file_delete(self, fname):
#         s3 = self._get_s3_client()
#         bucket = 'new-local-bucket'
#
#         s3.delete_object(
#             Bucket=bucket,
#             Key=fname,
#         )