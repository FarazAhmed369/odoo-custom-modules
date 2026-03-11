from odoo import http
from odoo.http import request, Response
import json
from datetime import datetime

# Ã°Å¸â€�Â¹ Set your secret API key here or store in ir.config_parameter
API_KEY = "MY_SECRET_KEY_123"

class POSSubscriptionAPI(http.Controller):

    # ------------------- GET API -------------------
    @http.route('/api/pos/info', type='http', auth='public', methods=['GET'], csrf=False)
    def get_subscription_info(self, **kwargs):
        """
        Unified GET API for trial or license info
        Returns a single payload for both types
        """
        # Ã°Å¸â€�Â¹ API Key Authentication
        key = request.httprequest.headers.get('X-API-KEY')
        if key != API_KEY:
            return Response(
                "Unauthorized: Invalid API Key",
                status=401,
                content_type='text/plain'
            )

        ICP = request.env['ir.config_parameter'].sudo()
        subscription_type = ICP.get_param('pos_subscription.subscription_type', 'trial')

        if subscription_type == 'trial':
            start_date = ICP.get_param('pos_subscription.trial_start_date', 'false')
            days = int(ICP.get_param('pos_subscription.trial_days', 0))
            is_active = ICP.get_param('pos_subscription.trial_used', 'false')
        else:  # license
            start_date = ICP.get_param('pos_subscription.license_start_date', None)
            days = int(ICP.get_param('pos_subscription.license_days', 0))
            is_active = ICP.get_param('pos_subscription.license_is_active', 'false')

        payload = {
            "subscription_type": subscription_type,
            "start_date": start_date,
            "days": days,
            "is_active": is_active
        }

        return Response(json.dumps(payload), status=200, content_type='application/json')

    # ------------------- POST API -------------------
    @http.route('/api/pos/update', type='http', auth='public', methods=['POST'], csrf=False)
    def post_subscription_info(self, **kwargs):
        """
        Unified POST API to update trial or license info
        Body format:
        {
            "subscription_type": "trial",  # or "license"
            "start_date": "YYYY-MM-DD",
            "days": 2,
            "is_active": "true"
        }
        """
        # Ã°Å¸â€�Â¹ API Key Authentication
        key = request.httprequest.headers.get('X-API-KEY')
        if key != API_KEY:
            return Response(
                "Unauthorized: Invalid API Key",
                status=401,
                content_type='text/plain'
            )

        ICP = request.env['ir.config_parameter'].sudo()
        body = request.httprequest.get_data(as_text=True)
        try:
            data = json.loads(body) if body else {}
        except Exception:
            return Response('HTTP 400 Bad Request: invalid JSON', status=400, content_type='text/plain; charset=utf-8')

        subscription_type = data.get('subscription_type', '').lower()
        start_date = data.get('start_date')
        days = data.get('days', 0)
        is_active = data.get('is_active', 'false')

        if subscription_type == 'trial':
            ICP.set_param('pos_subscription.subscription_type', 'trial')
            ICP.set_param('pos_subscription.trial_start_date', start_date)
            ICP.set_param('pos_subscription.trial_days', str(days))
            ICP.set_param('pos_subscription.trial_is_active', is_active)
        elif subscription_type == 'license':
            ICP.set_param('pos_subscription.subscription_type', 'license')
            ICP.set_param('pos_subscription.license_start_date', start_date)
            ICP.set_param('pos_subscription.license_days', str(days))
            ICP.set_param('pos_subscription.license_is_active', is_active)
        else:
            payload = {"status": "error", "message": "Invalid subscription_type. Use 'trial' or 'license'"}
            return Response(json.dumps(payload), status=400, content_type='application/json')

        payload = {
            "status": "success",
            "received": data,
            "message": f"{subscription_type.capitalize()} parameters updated successfully."
        }

        return Response(json.dumps(payload), status=200, content_type='application/json')
