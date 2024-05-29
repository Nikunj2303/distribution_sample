from odoo import models, fields,api

class DistributionSampleProduct(models.Model):
    _name = 'distribution.sample.product'
    _description = 'Sample Product'

    name = fields.Char(string='Product Name', compute='_compute_product_name', store=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    order_id = fields.Many2one('distribution.sample.order', string='Sample Order', ondelete='cascade')

    @api.depends('product_id')
    def _compute_product_name(self):
        for product in self:
            product.name = product.product_id.name