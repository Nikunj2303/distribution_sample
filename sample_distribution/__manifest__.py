{
    'name': 'Distribution',
    'version': '17.0',
    'license': 'LGPL-3',
    'sequence': -500,
    'summary': 'Module for managing sample orders distribution',
    'depends': ['base','stock','sale','product','crm'],
    'data': [
        'security\ir.model.access.csv',
        'views\sample_order_menu.xml',
        'views\sample_order_views.xml',
        'views\location_view.xml',
        'views/autovalidate_wizard.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
