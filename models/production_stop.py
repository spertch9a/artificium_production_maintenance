# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductionStop(models.Model):
    _name = 'production.stop'
    _description = 'Arrêt de Production'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'scheduled_date desc'

    name = fields.Char(
        string='Référence',
        required=True,
        copy=False
    )

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('scheduled', 'Programmé'),
        ('in_progress', 'En cours'),
        ('done', 'Terminé'),
        ('cancel', 'Annulé'),
    ], string='État', default='draft', tracking=True)

    maintenance_request_id = fields.Many2one(
        'maintenance.request',
        string='Demande de maintenance'
    )

    equipment_id = fields.Many2one(
        'maintenance.equipment',
        string='Équipement',
        required=True
    )

    production_order_id = fields.Many2one(
        'mrp.production',
        string='Ordre de fabrication'
    )

    production_team_id = fields.Many2one(
        'mrp.workcenter',
        string='Équipe/Atelier'
    )

    scheduled_date = fields.Datetime(
        string='Date programmée',
        required=True,
        tracking=True
    )

    actual_start_date = fields.Datetime(
        string='Début réel'
    )

    actual_end_date = fields.Datetime(
        string='Fin réelle'
    )

    duration = fields.Float(
        string='Durée planifiée (heures)'
    )

    actual_duration = fields.Float(
        string='Durée réelle (heures)',
        compute='_compute_actual_duration',
        store=True
    )

    reason = fields.Selection([
        ('maintenance', 'Maintenance préventive'),
        ('curative', 'Maintenance curative'),
        ('failure', 'Panne'),
        ('changeover', 'Changement de série'),
        ('material', 'Manque matière'),
        ('quality', 'Problème qualité'),
        ('other', 'Autre'),
    ], string='Motif', required=True, default='maintenance')

    reason_description = fields.Text(
        string='Description du motif'
    )

    impact_production = fields.Selection([
        ('none', 'Aucun'),
        ('minor', 'Mineur'),
        ('major', 'Majeur'),
        ('critical', 'Critique'),
    ], string='Impact sur la production', default='minor')

    responsible_id = fields.Many2one(
        'res.users',
        string='Responsable',
        default=lambda self: self.env.user
    )

    maintenance_team_id = fields.Many2one(
        'maintenance.team',
        string='Équipe maintenance'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Société',
        default=lambda self: self.env.company
    )

    notes = fields.Text(
        string='Notes'
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code('production.stop') or _('Nouveau')
        return super(ProductionStop, self).create(vals_list)

    @api.depends('actual_start_date', 'actual_end_date')
    def _compute_actual_duration(self):
        for stop in self:
            if stop.actual_start_date and stop.actual_end_date:
                delta = stop.actual_end_date - stop.actual_start_date
                stop.actual_duration = delta.total_seconds() / 3600
            else:
                stop.actual_duration = 0.0

    def action_schedule(self):
        self.write({'state': 'scheduled'})

    def action_start(self):
        self.write({
            'state': 'in_progress',
            'actual_start_date': fields.Datetime.now(),
        })

    def action_done(self):
        self.write({
            'state': 'done',
            'actual_end_date': fields.Datetime.now(),
        })

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_draft(self):
        self.write({'state': 'draft'})
