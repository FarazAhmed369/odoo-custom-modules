from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    arx_transfer_status = fields.Selection([
        ("draft", "Draft"),
        ("success", "Success"),
        ("failed", "Failed"),
    ], default="draft")

    arx_last_response = fields.Text("Last API Response", readonly=True)
    arx_last_sync_date = fields.Datetime("Last Sync Date", readonly=True)

    def action_sync_aramex_transfer(self):

        config = self.env['ir.config_parameter'].sudo()

        ssa_login = config.get_param("aramex.ssa_login")
        ssa_password = config.get_param("aramex.ssa_password")
        facility = config.get_param("aramex.facility")
        storer_key = config.get_param("aramex.storer_key")
        base_url = config.get_param("aramex.url")

        endpoint = "/WS_EDI_TEST_V02/RestService_API/InBound/ImportASN"
        url = f"{base_url}{endpoint}"

        if not ssa_login or not ssa_password:
            raise ValidationError("Aramex credentials not configured.")

        for rec in self:

            # CONDITION CHECK
            if rec.location_id.name != "MWH" or rec.location_dest_id.name != "OWH":
                raise ValidationError(
                    "API can only be triggered when Source = MWH and Destination = OWH"
                )

            if not rec.move_ids_without_package:
                raise ValidationError("No products found in transfer.")

            datalines = []

            for line in rec.move_ids_without_package:

                if not line.product_id.default_code:
                    raise ValidationError(
                        f"SKU missing on product {line.product_id.name}"
                    )

                datalines.append({
                    "ExternLineNo": rec.name,
                    "Qty": line.product_uom_qty,
                    "SKU": line.product_id.default_code,
                    "UnitCost": line.product_id.standard_price or 0
                })

            payload = {
                "ApplicationHeader": {
                    "RequestedDate": datetime.now().strftime("%Y-%m-%d"),
                    "RequestedSystem": "Odoo",
                    "TransactionID": rec.id,
                },
                "DataHeader": {
                    "ClinetSystemRef": rec.name,
                    "Currency": rec.company_id.currency_id.name,
                    "Facility": facility,
                    "StorerKey": storer_key,
                    "Type": "transfer",
                },
                "DataLines": datalines,
                "SSA": {
                    "SSA_Login": ssa_login,
                    "SSA_Password": ssa_password,
                },
            }

            headers = {"Content-Type": "application/json"}

            try:

                _logger.info("Aramex Transfer Payload: %s", payload)

                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=60
                )

                response.raise_for_status()

                rec.arx_transfer_status = "success"
                rec.arx_last_response = response.text
                rec.arx_last_sync_date = fields.Datetime.now()

                rec.message_post(body="Transfer successfully synced with Aramex.")

                _logger.info("Aramex Transfer Response: %s", response.text)

            except Exception as e:

                rec.arx_transfer_status = "failed"
                rec.arx_last_response = str(e)
                rec.arx_last_sync_date = fields.Datetime.now()

                _logger.error("Aramex Transfer Error: %s", str(e))

                raise ValidationError(f"API Error: {str(e)}")

    def action_sync_multi_aramex_transfer(self):

        _logger.info("===== START Aramex Multi Transfer Sync =====")
    
        config = self.env['ir.config_parameter'].sudo()
        _logger.info("Fetching Aramex configuration parameters")
    
        ssa_login = config.get_param("aramex.ssa_login")
        ssa_password = config.get_param("aramex.ssa_password")
        facility = config.get_param("aramex.facility")
        storer_key = config.get_param("aramex.storer_key")
        base_url = config.get_param("aramex.url")
    
        _logger.info("Config Values -> login:%s facility:%s storer:%s base_url:%s",
                     ssa_login, facility, storer_key, base_url)
    
        endpoint = "/WS_EDI_TEST_V02/RestService_API/InBound/ImportASN"
        url = f"{base_url}{endpoint}"
    
        _logger.info("Final API URL: %s", url)
    
        if not ssa_login or not ssa_password or not url:
            _logger.error("Aramex credentials missing")
            raise ValidationError("Aramex API credentials or URL not configured.")
    
        headers = {"Content-Type": "application/json"}
    
        _logger.info("Total Transfers Selected: %s", len(self))
    
        for rec in self:
    
            _logger.info("---- Processing Transfer: %s ----", rec.name)
    
            try:
    
                _logger.info("Source Location: %s | Destination Location: %s",
                             rec.location_id.name, rec.location_dest_id.name)
    
                # LOCATION VALIDATION
                if rec.location_id.name != "MWH" or rec.location_dest_id.name != "OWH":
                    _logger.warning(
                        "Location validation failed for %s", rec.name
                    )
                    raise ValidationError(
                        "Transfer must be from MWH to OWH for %s" % rec.name
                    )
    
                _logger.info("Location validation passed for %s", rec.name)
    
                if not rec.move_ids_without_package:
                    _logger.warning("No product lines in transfer %s", rec.name)
                    raise ValidationError("No product lines found in %s" % rec.name)
    
                datalines = []
    
                _logger.info("Reading transfer lines for %s", rec.name)
    
                for line in rec.move_ids_without_package:
    
                    _logger.info("Processing product line -> Product: %s Qty: %s",
                                 line.product_id.display_name,
                                 line.product_uom_qty)
    
                    if not line.product_id.default_code:
                        _logger.error(
                            "SKU missing on product %s", line.product_id.display_name
                        )
                        raise ValidationError(
                            "SKU missing on product %s" % line.product_id.name
                        )
    
                    dataline = {
                        "ExternLineNo": rec.name,
                        "Qty": line.product_uom_qty,
                        "SKU": line.product_id.default_code,
                        "UnitCost": line.product_id.standard_price or 0,
                    }
    
                    _logger.info("Generated DataLine: %s", dataline)
    
                    datalines.append(dataline)
    
                _logger.info("Total datalines created: %s", len(datalines))
    
                payload = {
                    "ApplicationHeader": {
                        "RequestedDate": datetime.now().strftime("%Y-%m-%d"),
                        "RequestedSystem": "Odoo",
                        "TransactionID": rec.name,
                    },
                    "DataHeader": {
                        "ClinetSystemRef": rec.name,
                        "Currency": rec.company_id.currency_id.name,
                        "Facility": facility,
                        "StorerKey": storer_key,
                        "Type": "transfer",
                    },
                    "DataLines": datalines,
                    "SSA": {
                        "SSA_Login": ssa_login,
                        "SSA_Password": ssa_password,
                    },
                }
    
                _logger.info("Final Payload for %s -> %s", rec.name, payload)
    
                _logger.info("Sending API request to Aramex")
    
                response = requests.post(url, json=payload, headers=headers, timeout=60)
    
                _logger.info("HTTP Status Code: %s", response.status_code)
    
                response.raise_for_status()
    
                _logger.info("API Response Text: %s", response.text)
    
                rec.arx_transfer_status = "success"
                rec.arx_last_response = response.text
                rec.arx_last_sync_date = fields.Datetime.now()
    
                _logger.info("Transfer Sync SUCCESS for %s", rec.name)
    
            except Exception as e:
    
                rec.arx_transfer_status = "failed"
                rec.arx_last_response = str(e)
                rec.arx_last_sync_date = fields.Datetime.now()
    
                _logger.error(
                    "Transfer Sync FAILED for %s | Error: %s", rec.name, str(e)
                )
    
        _logger.info("===== END Aramex Multi Transfer Sync =====")
    
        return True