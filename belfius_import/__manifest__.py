{
    'name': "Belfius Import",

    'summary': """
    Create Invoice/Refund based on a csv from Belfius, a belgian bank.
    """,

    'description': """
        Create Invoice/Refund based on a csv from Belfius, a belgian bank.
    """,

    'author': "JDI",
    'website': "http://www.jdi.me",
    'category': 'Invoices & Payments',
    'version': '12.0.1.0.0',

    'depends': ['base','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/belfius_import_views.xml',
        'views/account_invoice_view.xml',
        'views/product_product_view.xml',
        'views/res_partner_view.xml',
        'wizard/belfius_import_line_set_view.xml',
        'data/belfius_import_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}