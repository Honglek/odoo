{
    'name': 'Sale & Activities',
    'version': '14.0',
    'depends': ['base','sale','contacts'],
    'data'  : [
        'views/sale_views.xml',
        'views/sale_activities_view.xml', 
        'security/sale_security.xml',
        'security/ir.model.access.csv',
    ],
    'test': [],
    'installable': True,
    'auto_install': True, 
    'license': 'LGPL-3',
}
