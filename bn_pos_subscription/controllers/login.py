# -*- coding: utf-8 -*-
import logging
from odoo import http, _
from odoo.http import request
from odoo.addons.web.controllers.home import Home
from odoo.addons.web.controllers.utils import ensure_db
from odoo.exceptions import AccessDenied
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class CustomHome(Home):

    @http.route('/web/login', type='http', auth='none', readonly=False)
    def web_login(self, redirect=None, **kw):
        ensure_db()
        ICP = request.env['ir.config_parameter'].sudo()
        today = datetime.today()

        if request.httprequest.method == 'POST':

            _logger.info("========== LOGIN ATTEMPT START ==========")

            # Load unified subscription info
            subscription_type = ICP.get_param('pos_subscription.subscription_type', 'trial')
            _logger.info(f"Subscription Type: {subscription_type}")

            if subscription_type == 'trial':
                start_date_str = ICP.get_param('pos_subscription.trial_start_date', None)
                days = int(ICP.get_param('pos_subscription.trial_days', 0))
                is_active = ICP.get_param('pos_subscription.trial_is_active', 'false')
            else:  # license
                start_date_str = ICP.get_param('pos_subscription.license_start_date', None)
                days = int(ICP.get_param('pos_subscription.license_days', 0))
                is_active = ICP.get_param('pos_subscription.license_is_active', 'false')

            _logger.info(f"Start Date (raw): {start_date_str}")
            _logger.info(f"Days: {days}")
            _logger.info(f"Is Active (raw): {is_active}")

            message_type = "Trial" if subscription_type == 'trial' else "Subscription"

            # Validate start_date
            if not start_date_str or str(start_date_str).lower() == 'false':
                _logger.warning("Start date missing or invalid.")
                raise AccessDenied(_(f"{message_type} not activated. Please contact administrator."))

            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                _logger.info(f"Parsed Start Date: {start_date}")
            except Exception as e:
                _logger.error(f"Date parsing error: {e}")
                raise AccessDenied(_(f"Invalid {message_type.lower()} start date."))

            # Compute expiry
            if subscription_type == 'trial':
                expiry_date = start_date + timedelta(days=days)
                active = str(is_active).lower() == 'true'
            else:
                expiry_date = start_date + timedelta(days=days)
                active = str(is_active).lower() == 'true'

            _logger.info(f"Computed Expiry Date: {expiry_date}")
            _logger.info(f"Active Status (bool): {active}")
            _logger.info(f"Today Date: {today}")

            # Block condition
            if (today.date() > expiry_date.date()) or (not active):
                _logger.warning("LOGIN BLOCKED - Expired or Inactive")
                _logger.info("========== LOGIN ATTEMPT END ==========")
                raise AccessDenied(_(f"Your {message_type.lower()} has expired. Please contact administrator."))

            _logger.info("LOGIN ALLOWED")
            _logger.info("========== LOGIN ATTEMPT END ==========")

        return super().web_login(redirect=redirect, **kw)
