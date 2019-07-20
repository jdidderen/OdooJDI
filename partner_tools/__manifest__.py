{
    'name': "Partner Tools",

    'summary': """
    Various tools for partners.
    """,

    'description': """
        Various tools for partners.
    """,

    'author': "JDI",
    'website': "http://www.jdi.me",
    'category': 'CRM',
    'version': '12.0.1.0.0',

    'depends': ['base','crm',],

    # always loaded
    'data': [
        'wizard/res_partner_mass_set_view.xml',
        'wizard/res_partner_reset_images_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}