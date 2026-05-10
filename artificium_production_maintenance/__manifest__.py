# -*- coding: utf-8 -*-
{
    'name': "Production-Maintenance Integration",
    'summary': """
        Automatic notifications and seamless integration between Production and Maintenance modules.
    """,
    'description': """
Production-Maintenance Integration
===================================

Bridge the gap between your Production and Maintenance teams with automated workflows,
real-time notifications, and comprehensive KPI tracking.

Key Features
------------
* **Automatic notifications** to the production manager whenever a preventive maintenance
  is scheduled that requires a production stop.
* **Production Stop management** — full lifecycle (Draft → Scheduled → In Progress → Done)
  with planned vs. actual duration tracking.
* **Equipment KPIs** — total downtime hours, availability rate, MTBF, MTTR per equipment.
* **Manufacturing order integration** — link maintenance requests directly to production orders.
* **Stop reporting** — filter and group stops by team, reason, date, or impact level.
* **Email templates** — ready-to-use notification email sent automatically to the
  production responsible.

Models
------
* ``production.stop`` — New model tracking every production stop event.
* ``maintenance.request`` — Extended with production impact fields and notification actions.
* ``maintenance.equipment`` — Extended with workcenter link, availability, and downtime cost.
* ``mrp.production`` — Extended with linked maintenances and stop records.

Dependencies: ``mrp``, ``maintenance``, ``mail``, ``hr``
    """,
    'version': '18.0.1.0.0',
    'category': 'Manufacturing',
    'author': 'EURL ARTIFICIUM',
    'website': 'https://www.artificium.dz',
    'images': ['static/description/banner.png'],
    'depends': [
        'base',
        'mrp',
        'maintenance',
        'mail',
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security_rules.xml',
        'data/ir_sequence.xml',
        'data/email_templates.xml',
        'views/mrp_production_views.xml',
        'views/maintenance_request_views.xml',
        'views/production_stop_views.xml',
        'views/equipment_views.xml',
        'menu/menu_items.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 190.00,
    'currency': 'EUR',
    'license': 'LGPL-3',
}
