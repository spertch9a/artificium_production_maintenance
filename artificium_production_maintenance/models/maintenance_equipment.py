# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    workcenter_id = fields.Many2one(
        'mrp.workcenter',
        string='Poste de charge lié'
    )

    production_team_id = fields.Many2one(
        'mrp.workcenter',
        string='Équipe de production',
        related='workcenter_id',
        store=True,
        readonly=True
    )

    production_capacity = fields.Float(
        string='Capacité de production',
        help='Capacité horaire de production'
    )

    downtime_cost_per_hour = fields.Float(
        string='Coût d\'arrêt/heure',
        help='Coût estimé de l\'arrêt de production par heure'
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        default=lambda self: self.env.company.currency_id
    )

    total_downtime_hours = fields.Float(
        string='Total heures d\'arrêt',
        compute='_compute_total_downtime',
        store=True
    )

    availability_rate = fields.Float(
        string='Taux de disponibilité (%)',
        compute='_compute_availability',
        store=True
    )

    mtbf = fields.Float(
        string='MTBF (heures)',
        help='Mean Time Between Failures'
    )

    mttr = fields.Float(
        string='MTTR (heures)',
        help='Mean Time To Repair'
    )

    def _compute_total_downtime(self):
        for equipment in self:
            stops = self.env['production.stop'].search([
                ('equipment_id', '=', equipment.id),
                ('state', '=', 'done'),
            ])
            equipment.total_downtime_hours = sum(stops.mapped('actual_duration'))

    def _compute_availability(self):
        for equipment in self:
            # Simplified calculation
            if equipment.total_downtime_hours > 0:
                # Assume 8760 hours per year
                available_hours = 8760 - equipment.total_downtime_hours
                equipment.availability_rate = (available_hours / 8760) * 100
            else:
                equipment.availability_rate = 100.0

    def action_view_production_stops(self):
        self.ensure_one()
        return {
            'name': _('Arrêts de Production'),
            'type': 'ir.actions.act_window',
            'res_model': 'production.stop',
            'domain': [('equipment_id', '=', self.id)],
            'view_mode': 'list,form',
            'target': 'current',
        }
