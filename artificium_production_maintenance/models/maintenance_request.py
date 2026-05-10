# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    affects_production = fields.Boolean(
        string='Affecte la production',
        default=False,
        help='Cette maintenance nécessite un arrêt de la production'
    )

    production_manager_id = fields.Many2one(
        'res.users',
        string='Responsable Production',
        help='Personne à notifier en cas de maintenance affectant la production'
    )

    production_team_id = fields.Many2one(
        'mrp.workcenter',
        string='Équipe/Atelier concerné'
    )

    scheduled_production_stop = fields.Boolean(
        string='Arrêt programmé',
        default=False
    )

    production_stop_duration = fields.Float(
        string='Durée d\'arrêt (heures)',
        help='Durée estimée de l\'arrêt de production'
    )

    production_orders_ids = fields.Many2many(
        'mrp.production',
        'maintenance_production_rel',
        'maintenance_id',
        'production_id',
        string='Ordres de fabrication affectés'
    )

    production_stop_id = fields.Many2one(
        'production.stop',
        string='Arrêt de production lié'
    )

    notification_sent = fields.Boolean(
        string='Notification envoyée',
        default=False
    )

    priority_level = fields.Selection([
        ('low', 'Faible'),
        ('medium', 'Moyenne'),
        ('high', 'Haute'),
        ('critical', 'Critique'),
    ], string='Niveau de priorité', default='medium')

    @api.onchange('affects_production')
    def _onchange_affects_production(self):
        if self.affects_production:
            # Auto-detect production manager
            production_manager = self.env['res.users'].search([
                ('groups_id', 'in', self.env.ref('mrp.group_mrp_manager').id)
            ], limit=1)
            if production_manager:
                self.production_manager_id = production_manager.id

    def action_notify_production(self):
        """Send notification to production manager"""
        self.ensure_one()
        
        if not self.affects_production:
            raise UserError(_('Cette maintenance n\'est pas marquée comme affectant la production.'))
        
        if not self.production_manager_id:
            raise UserError(_('Veuillez définir un responsable production.'))

        # Send email notification
        template = self.env.ref(
            'artificium_production_maintenance.email_template_maintenance_notification',
            raise_if_not_found=False
        )
        
        if template:
            template.send_mail(self.id, force_send=True)
            self.notification_sent = True
            self.message_post(
                body=_('Notification envoyée au responsable production: %s') % 
                     self.production_manager_id.name
            )

        # Create activity for production manager
        self.env['mail.activity'].create({
            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            'summary': _('Maintenance planifiée - Arrêt production requis'),
            'note': _(
                'Maintenance %(maintenance)s programmée le %(date)s sur l\'équipement %(equipment)s. '
                'Durée estimée: %(duration)s heures.'
            ) % {
                'maintenance': self.name,
                'date': self.schedule_date,
                'equipment': self.equipment_id.name,
                'duration': self.production_stop_duration or 'Non définie'
            },
            'user_id': self.production_manager_id.id,
            'res_id': self.id,
            'res_model_id': self.env['ir.model']._get('maintenance.request').id,
        })

    def action_schedule_production_stop(self):
        """Schedule a production stop linked to this maintenance"""
        self.ensure_one()
        
        if not self.affects_production:
            raise UserError(_('Cette maintenance n\'affecte pas la production.'))

        # Create production stop
        stop = self.env['production.stop'].create({
            'name': _('Arrêt maintenance - %s') % self.name,
            'maintenance_request_id': self.id,
            'equipment_id': self.equipment_id.id,
            'production_team_id': self.production_team_id.id,
            'scheduled_date': self.schedule_date,
            'duration': self.production_stop_duration,
            'reason': 'maintenance',
        })

        self.production_stop_id = stop.id
        self.scheduled_production_stop = True

        # Notify production manager
        self.action_notify_production()

        return {
            'name': _('Arrêt de Production'),
            'type': 'ir.actions.act_window',
            'res_model': 'production.stop',
            'res_id': stop.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def write(self, vals):
        """Override to send notification when maintenance date is scheduled"""
        res = super(MaintenanceRequest, self).write(vals)
        
        # If schedule_date is set and affects_production, notify production
        if 'schedule_date' in vals and self.affects_production and not self.notification_sent:
            self.action_notify_production()
        
        return res
