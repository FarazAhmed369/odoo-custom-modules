{
    'name': 'Product Variant Excel Importer',
    'version': '1.0',
    'summary': 'Import and Update Products/Variants via Excel Wizard',
    'category': 'Inventory',
    'author': 'Faraz Ahmed',
    'depends': ['base', 'stock', 'product', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_import_wizard_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}