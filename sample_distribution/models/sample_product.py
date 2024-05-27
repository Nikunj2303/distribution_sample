from odoo import models, fields

class DistributionSampleProduct(models.Model):
    _name = 'distribution.sample.product'
    _description = 'Sample Product'

    name = fields.Char(string='Product Name', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    order_id = fields.Many2one('distribution.sample.order', string='Sample Order', ondelete='cascade')