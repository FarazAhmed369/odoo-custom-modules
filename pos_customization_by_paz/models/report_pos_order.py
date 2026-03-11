# -*- coding: utf-8 -*-
from odoo import models, fields, tools

class ReportPosOrderInherit(models.Model):
    _inherit = 'report.pos.order'

    parent_product_categ_id = fields.Many2one(
        'product.category',
        string='Parent Product Category',
        readonly=True
    )
    parent_product_categ_name = fields.Char(
        string='Parent Category Name',
        readonly=True
    )

    def _select(self):
        return """
            SELECT
                MIN(l.id) AS id,
                COUNT(*) AS nbr_lines,
                s.date_order AS date,
                SUM(l.qty) AS product_qty,
                SUM(l.qty * l.price_unit / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) AS price_sub_total,
                SUM(ROUND((l.price_subtotal_incl) / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END, cu.decimal_places)) AS price_total,
                SUM((l.qty * l.price_unit) * (l.discount / 100) / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) AS total_discount,
                CASE
                    WHEN SUM(l.qty * u.factor) = 0 THEN NULL
                    ELSE (SUM(l.qty*l.price_unit / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END)/SUM(l.qty * u.factor))::decimal
                END AS average_price,
                SUM(cast(to_char(date_trunc('day',s.date_order) - date_trunc('day',s.create_date),'DD') AS INT)) AS delay_validation,
                s.id as order_id,
                s.partner_id AS partner_id,
                s.state AS state,
                s.user_id AS user_id,
                s.company_id AS company_id,
                s.sale_journal AS journal_id,
                l.product_id AS product_id,
                pt.categ_id AS product_categ_id,
                pc.parent_id AS parent_product_categ_id,
                pc2.name AS parent_product_categ_name,
                p.product_tmpl_id,
                ps.config_id,
                s.pricelist_id,
                s.session_id,
                s.account_move IS NOT NULL AS invoiced,
                SUM(l.price_subtotal - COALESCE(l.total_cost,0) / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) AS margin
        """

    def _from(self):
        return """
            FROM pos_order_line AS l
                INNER JOIN pos_order s ON (s.id=l.order_id)
                LEFT JOIN product_product p ON (l.product_id=p.id)
                LEFT JOIN product_template pt ON (p.product_tmpl_id=pt.id)
                LEFT JOIN product_category pc ON (pt.categ_id = pc.id)
                LEFT JOIN product_category pc2 ON (pc.parent_id = pc2.id)
                LEFT JOIN uom_uom u ON (u.id=pt.uom_id)
                LEFT JOIN pos_session ps ON (s.session_id=ps.id)
                LEFT JOIN res_company co ON (s.company_id=co.id)
                LEFT JOIN res_currency cu ON (co.currency_id=cu.id)
        """

    def _group_by(self):
        return """
            GROUP BY
                s.id, s.date_order, s.partner_id, s.state, pt.categ_id,
                pc.parent_id,
                pc2.name,
                s.user_id, s.company_id, s.sale_journal,
                s.pricelist_id, s.account_move, s.create_date, s.session_id,
                l.product_id,
                pt.categ_id,
                p.product_tmpl_id,
                ps.config_id
        """

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
                %s
                %s
            )
        """ % (self._table, self._select(), self._from(), self._group_by())
        )
