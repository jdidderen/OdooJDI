{
    'name': "Energy Management",

    'summary': """
    Manage your meters and receive reminders to read your meters.
    """,

    'description': """
        Manage your meters and receive reminders to read your meters.
    """,

    'author': "JDI",
    'website': "http://www.jdi.me",
    'category': 'Administration',
    'version': '12.0.1.0.0',

    'depends': ['base','mail'],

    # always loaded
    'data': [
        'views/energy_views.xml',
        'views/energy_type_views.xml',
        'views/energy_meter_reading_views.xml',
        'views/energy_meter_views.xml',
        'views/res_config_settings_views.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}