from odoo import models, fields, api

class AutoValidatePickingWizard(models.TransientModel):
    _name = 'auto.validate.picking.wizard'
    _description = 'Auto Validate Picking Wizard'

    sample_order_ids = fields.Many2many('distribution.sample.order', string='Sample Orders')

    def action_auto_validate(self):
        active_ids = self.env.context.get('active_ids')
        pickings = self.env['stock.picking'].browse(active_ids)
        for picking in pickings:
            picking.action_confirm()
            picking.action_assign()
            picking.button_validate()
        return {'type': 'ir.actions.act_window_close'}
