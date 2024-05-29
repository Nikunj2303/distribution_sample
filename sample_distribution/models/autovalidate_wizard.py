from odoo import models, fields, api, exceptions

class AutoValidatePickingWizard(models.TransientModel):
    _name = 'auto.validate.picking.wizard'
    _description = 'Auto Validate Picking Wizard'

    sample_order_ids = fields.Many2many('distribution.sample.order', string='Sample Orders')

    def action_auto_validate(self):
        for order in self.sample_order_ids:
            pickings = order.mapped('picking_ids')
            for picking in pickings:
                if picking.state == 'draft':
                    picking.action_confirm()
                if picking.state in ['confirmed', 'partially_available']:
                    picking.action_assign()
                if picking.state == 'assigned':
                    picking.button_validate()
        return {'type': 'ir.actions.act_window_close'}
