import base64
import io
import pandas as pd
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductImportWizard(models.TransientModel):
    _name = 'product.import.wizard'
    _description = 'Comma Separated Variant Importer'

    import_file = fields.Binary(string="Select Excel File", required=True)
    file_name = fields.Char(string="File Name")

    def action_import_file(self):
        if not self.import_file:
            raise UserError(_("Please upload a file."))

        file_content = base64.b64decode(self.import_file)
        # Using pandas to read the excel
        df = pd.read_excel(io.BytesIO(file_content))

        for index, row in df.iterrows():
            p_name = str(row.get('Product Name', '')).strip()
            categ_name = str(row.get('Category', 'All')).strip()
            attr_string = str(row.get('Attributes', '')).strip() 
            val_string = str(row.get('Values', '')).strip()      
            sku = str(row.get('Internal Reference', '')).strip()
            barcode = str(row.get('Barcode', '')).strip()
            
            # --- NEW FIELDS ---
            # list_price is Sales Price, standard_price is Cost
            sales_price = row.get('Price', 0.0)
            cost_price = row.get('Cost', 0.0)

            if not p_name or p_name == 'nan':
                continue

            # 1. Handle Template
            template = self.env['product.template'].search([('name', '=', p_name)], limit=1)
            if not template:
                template = self.env['product.template'].create({
                    'name': p_name,
                    'type': 'product',
                    'list_price': float(sales_price) if not pd.isna(sales_price) else 0.0,
                    'categ_id': self.env['product.category'].search([('name', '=', categ_name)], limit=1).id or 1
                })
            else:
                # Update price on existing template if provided
                if not pd.isna(sales_price):
                    template.write({'list_price': float(sales_price)})

            # 2. Process Comma-Separated Attributes
            attr_names = [a.strip() for a in attr_string.split(',') if a.strip()]
            val_names = [v.strip() for v in val_string.split(',') if v.strip()]

            if len(attr_names) == len(val_names):
                for i in range(len(attr_names)):
                    attr_obj = self.env['product.attribute'].search([('name', '=', attr_names[i])], limit=1)
                    if not attr_obj:
                        attr_obj = self.env['product.attribute'].create({'name': attr_names[i], 'create_variant': 'always'})

                    val_obj = self.env['product.attribute.value'].search([
                        ('name', '=', val_names[i]), ('attribute_id', '=', attr_obj.id)], limit=1)
                    if not val_obj:
                        val_obj = self.env['product.attribute.value'].create({'name': val_names[i], 'attribute_id': attr_obj.id})

                    line = template.attribute_line_ids.filtered(lambda l: l.attribute_id.id == attr_obj.id)
                    if not line:
                        template.write({'attribute_line_ids': [(0, 0, {'attribute_id': attr_obj.id, 'value_ids': [(4, val_obj.id)]})]})
                    elif val_obj not in line.value_ids:
                        line.write({'value_ids': [(4, val_obj.id)]})

            # 3. Find specific Variant to update Barcode, SKU, and Cost
            variant = self.env['product.product'].search([('product_tmpl_id', '=', template.id)])
            for v_name in val_names:
                variant = variant.filtered(lambda p: v_name in p.product_template_attribute_value_ids.mapped('name'))
            
            if variant:
                variant_vals = {
                    'default_code': sku if sku != 'nan' else False,
                    'barcode': barcode if barcode != 'nan' else False,
                }
                
                # Update Cost (standard_price) on the variant
                if not pd.isna(cost_price):
                    variant_vals['standard_price'] = float(cost_price)
                
                variant[0].write(variant_vals)

        return {
            'type': 'ir.actions.client', 
            'tag': 'display_notification', 
            'params': {
                'title': _('Import Complete'), 
                'message': _('Products, Variants, Prices, and Costs updated.'), 
                'type': 'success'
            }
        }