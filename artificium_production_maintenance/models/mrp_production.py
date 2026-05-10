# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    maintenance_request_ids = fields.Many2many(
        'maintenance.request',
        'maintenance_production_rel',
        'production_id',
        'maintenance_id',
        string='Maintenances liées'
    )

    pending_maintenance = fields.Boolean(
        string='Maintenance en attente',
        compute='_compute_pending_maintenance',
        store=True
    )

    next_maintenance_date = fields.Date(
        string='Prochaine maintenance',
        compute='_compute_next_maintenance',
        store=True
    )

    production_stop_ids = fields.One2many(
        'production.stop',
        'production_order_id',
        string='Arrêts de production'
    )

    @api.depends('maintenance_request_ids', 'maintenance_request_ids.stage_id')
    def _compute_pending_maintenance(self):
        for production in self:
            pending = production.maintenance_request_ids.filtered(
                lambda m: m.stage_id.name not in ['Done', 'Closed', 'Cancelled']
            )
            production.pending_maintenance = bool(pending)

    @api.depends('maintenance_request_ids', 'maintenance_request_ids.schedule_date')
    def _compute_next_maintenance(self):
        for production in self:
            future_maintenances = production.maintenance_request_ids.filtered(
                lambda m: m.schedule_date and m.schedule_date >= fields.Date.today()
            ).mapped('schedule_date')
            production.next_maintenance_date = min(future_maintenances) if future_maintenances else False

    def action_view_maintenances(self):
        self.ensure_one()
        return {
            'name': _('Maintenances'),
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.request',
            'domain': [('id', 'in', self.maintenance_request_ids.ids)],
            'view_mode': 'list,form',
            'target': 'current',
        }

    def action_schedule_maintenance_stop(self):
        """Schedule production stop for maintenance"""
        self.ensure_one()
        
        # Get equipment from workcenter
        equipment = self.workorder_ids.mapped('workcenter_id.equipment_id')
        
        if not equipment:
            raise UserError(_('Aucun équipement associé à cet ordre de fabrication.'))

        return {
            'name': _('Planifier Maintenance'),
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.request',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_affects_production': True,
                'default_production_orders_ids': [(6, 0, self.ids)],
                'default_equipment_id': equipment[0].id if equipment else False,
            },
        }

    def button_plan(self):
        """Override to check for pending maintenances"""
        for production in self:
            if production.pending_maintenance:
                # Optionally warn about pending maintenance
                pass
        return super(MrpProduction, self).button_plan()
