from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # =========================
    # Aramex Fields
    # =========================

    # arx_facility = fields.Char("Facility")
    # arx_hs_code = fields.Char("HS Code")
    # arx_storer_key = fields.Char("Storer Key")

    # arx_collection = fields.Char("Collection")
    # arx_color = fields.Char("Color")
    # arx_country_origin = fields.Char("Country of Origin")
    # arx_cost = fields.Float("Cost")
    # arx_price = fields.Float("Price")
    # arx_serial_count = fields.Integer("Serial Count")
    # arx_serial_length = fields.Integer("Serial Length")
    # arx_manufacturer_sku = fields.Char("Manufacturer SKU")
    # arx_upc = fields.Char("UPC")
    # arx_upc_uom = fields.Char("UPC UOM")

    arx_sync_status = fields.Selection([
        ("draft", "Draft"),
        ("success", "Success"),
        ("failed", "Failed"),
    ], default="draft", tracking=True)

    arx_last_response = fields.Text("Last API Response", readonly=True)
    arx_last_sync_date = fields.Datetime("Last Sync Date", readonly=True)

    # =========================
    # SYNC METHOD
    # =========================

    def action_sync_multi_aramex(self):
        config = self.env['ir.config_parameter'].sudo()
        ssa_login = config.get_param("aramex.ssa_login")
        ssa_password = config.get_param("aramex.ssa_password")
        arx_facility = config.get_param("aramex.facility")
        arx_storer_key = config.get_param("aramex.storer_key")
        base_url = config.get_param("aramex.url")
        endpoint = "WS_EDI_TEST_V02/RestService_API/SKU/ImportSKUs"
        url = f"{base_url}{endpoint}"
    
        if not ssa_login or not ssa_password or not url:
            raise ValidationError("Aramex API credentials or URL not configured.")
    
        headers = {"Content-Type": "application/json"}
    
        for rec in self:
            try:
                # Mandatory validation
                if not rec.name:
                    raise ValidationError("Description missing on %s" % rec.display_name)
                if not arx_facility:
                    raise ValidationError("Facility missing on %s" % rec.display_name)
                if not rec.hs_code:
                    raise ValidationError("HS Code missing on %s" % rec.display_name)
                if not rec.default_code:
                    raise ValidationError("Internal Reference missing on %s" % rec.display_name)
                if not arx_storer_key:
                    raise ValidationError("Storer Key missing on %s" % rec.display_name)
    
                payload = {
                    "ApplicationHeader": {
                        "RequestedDate": datetime.now().isoformat(),
                        "RequestedSystem": "Odoo",
                        "TransactionID": rec.default_code,
                    },
                    "DataHeader": [{
                        "Description": rec.name,
                        "Facility": arx_facility,
                        "HSCode": rec.hs_code,
                        "SKU": rec.default_code,
                        "StorerKey": arx_storer_key,
                        "UPC": rec.barcode,
                        # "COLLECTION": rec.arx_collection,
                        # "COLOR": rec.arx_color,
                        # "COUNTRYOFORIGIN": rec.arx_country_origin,
                        # "Cost": rec.arx_cost,
                        # "Price": rec.arx_price,
                        # "SerialCount": rec.arx_serial_count,
                        # "SerialLength": rec.arx_serial_length,
                        # "ManufacturerSKU": rec.arx_manufacturer_sku,
                        # "UPC": rec.arx_upc,
                        # "UPC_UOM": rec.arx_upc_uom,
                    }],
                    "SSA": {
                        "SSA_Login": ssa_login,
                        "SSA_Password": ssa_password,
                    },
                }
    
                response = requests.post(url, json=payload, headers=headers, timeout=60)
                response.raise_for_status()
    
                rec.arx_sync_status = "success"
                rec.arx_last_response = response.text
                rec.arx_last_sync_date = fields.Datetime.now()
    
            except Exception as e:
                rec.arx_sync_status = "failed"
                rec.arx_last_response = str(e)
                rec.arx_last_sync_date = fields.Datetime.now()
                _logger.error("Aramex Sync Error for %s: %s", rec.name, str(e))
    
        return True
    
    def action_sync_aramex(self):
        for rec in self:

            # Get Config Parameters
            config = self.env['ir.config_parameter'].sudo()
            ssa_login = config.get_param("aramex.ssa_login")
            ssa_password = config.get_param("aramex.ssa_password")
            arx_facility = config.get_param("aramex.facility")
            arx_storer_key = config.get_param("aramex.storer_key")
            base_url = config.get_param("aramex.url")
            endpoint = "/WS_EDI_TEST_V02/RestService_API/SKU/ImportSKUs"
            url = f"{base_url}{endpoint}"

            # Mandatory Field Validation
            if not rec.name:
                raise ValidationError("Description is required.")
            if not arx_facility:
                raise ValidationError("Facility is required.")
            if not rec.hs_code:
                raise ValidationError("HS Code is required.")
            if not rec.default_code:
                raise ValidationError("Internal Reference (SKU) is required.")
            if not arx_storer_key:
                raise ValidationError("Storer Key is required.")

            if not ssa_login or not ssa_password or not url:
                raise ValidationError("Aramex API credentials or URL not configured.")

            payload = {
                "ApplicationHeader": {
                    "RequestedDate": datetime.now().isoformat(),
                    "RequestedSystem": "Odoo",
                    "TransactionID": rec.default_code,
                },
                "DataHeader": [
                    {
                        "Description": rec.name,
                        "Facility": arx_facility,
                        "HSCode": rec.hs_code,
                        "SKU": rec.default_code,
                        "StorerKey": arx_storer_key,
                        "UPC": rec.barcode,
                        # "COLLECTION": rec.arx_collection,
                        # "COLOR": rec.arx_color,
                        # "COUNTRYOFORIGIN": rec.arx_country_origin,
                        # "Cost": rec.arx_cost,
                        # "Price": rec.arx_price,
                        # "SerialCount": rec.arx_serial_count,
                        # "SerialLength": rec.arx_serial_length,
                        # "ManufacturerSKU": rec.arx_manufacturer_sku,
                        # "UPC": rec.arx_upc,
                        # "UPC_UOM": rec.arx_upc_uom,
                    }
                ],
                "SSA": {
                    "SSA_Login": ssa_login,
                    "SSA_Password": ssa_password,
                },
            }

            headers = {"Content-Type": "application/json"}

            try:
                response = requests.post(url, json=payload, headers=headers, timeout=60)
                response.raise_for_status()

                rec.arx_sync_status = "success"
                rec.arx_last_response = response.text
                rec.arx_last_sync_date = fields.Datetime.now()

                rec.message_post(body="Successfully synced with Aramex.")

            except Exception as e:
                rec.arx_sync_status = "failed"
                rec.arx_last_response = str(e)
                rec.arx_last_sync_date = fields.Datetime.now()

                _logger.error("Aramex Sync Error: %s", str(e))
                raise ValidationError(f"API Error: {str(e)}")

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    aramex_url = fields.Char(
        string="Aramex API URL",
        config_parameter="aramex.url"
    )

    aramex_ssa_login = fields.Char(
        string="SSA Login",
        config_parameter="aramex.ssa_login"
    )

    aramex_ssa_password = fields.Char(
        string="SSA Password",
        config_parameter="aramex.ssa_password"
    )
    arx_facility = fields.Char(
        string="Facility",
        config_parameter="aramex.facility"
    )

    arx_storer_key = fields.Char(
        string="Storer Key",
        config_parameter="aramex.storer_key"
    )