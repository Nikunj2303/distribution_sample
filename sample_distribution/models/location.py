from odoo import models, fields, api, exceptions

class StockLocation(models.Model):
    _inherit = 'stock.location'

    is_sample_location = fields.Boolean(string="Sample Location")
    user_id = fields.Many2one('res.users', string="User", required=True)
    company_id = fields.Many2one('res.company', string="Company", required=True)

    @api.model
    def create_sample_location(self):
        user = self.env.user
        company = self.env.company

        # Check if a sample location already exists for this user and company
        existing_sample_location = self.env['stock.location'].search([
            ('is_sample_location', '=', True),
            ('user_id', '=', user.id),
            ('company_id', '=', company.id)
        ])

        if existing_sample_location:
            raise exceptions.UserError("A sample location already exists for this user and company.")

        # Create a new sample location
        sample_location = self.env['stock.location'].create({
            'name': "Sample Location for {}".format(user.name),
            'usage': 'internal',
            'is_sample_location': True,
            'user_id': user.id,
            'company_id': company.id
        })

        return {
            'name': "Sample Location Created",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.location',
            'res_id': sample_location.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }
