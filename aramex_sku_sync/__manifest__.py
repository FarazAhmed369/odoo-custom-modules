{
    "name": "Aramex SKU Sync",
    "version": "1.0",
    "sequence": "1",
    "author": "Paz Technologies",
    "category": "Inventory",
    "summary": "Sync Products to Aramex Infor API",
    "depends": ["product", "mail", "stock"],
    "data": [
        # "security/ir.model.access.csv",
        "views/product_view.xml",
        "views/res_config_settings_view.xml",
        "views/stock_picking_views.xml",
    ],
    "installable": True,
    "application": False,
}