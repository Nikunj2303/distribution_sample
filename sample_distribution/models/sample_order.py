from odoo import api, models, fields, exceptions
from odoo.exceptions import ValidationError

class DistributionSampleOrder(models.Model):
    _name = 'distribution.sample.order'
    _description = 'Sample Order Distribution'

    name = fields.Char(string='Order Reference', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required=True)
    source_location_id = fields.Many2one('stock.location', string='Source Location', required=True)
    destination_location_id = fields.Many2one('stock.location', string='Destination Location', required=True)
    user_id = fields.Many2one('res.users', string='Assigned to', default=lambda self: self.env.user)
    distribution_sample_product_ids = fields.One2many('distribution.sample.product', 'order_id', string='Sample Products')
    auto_picking = fields.Boolean(string='Auto Picking')

    @api.model
    def default_get(self, fields_list):
        res = super(DistributionSampleOrder, self).default_get(fields_list)
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)
        if warehouse:
            res['warehouse_id'] = warehouse.id
            res['source_location_id'] = warehouse.lot_stock_id.id
        return res

    @api.onchange('warehouse_id')
    def _onchange_warehouse_id(self):
        if self.warehouse_id:
            self.source_location_id = self.warehouse_id.lot_stock_id

    @api.onchange('user_id')
    def _onchange_user_id(self):
        if self.user_id:
            sample_location = self.env['stock.location'].search([
                ('user_id', '=', self.user_id.id),
                ('is_sample_location', '=', True),
                ('company_id', '=', self.env.company.id)
            ], limit=1)
            self.destination_location_id = sample_location.id if sample_location else False

    @api.constrains('distribution_sample_product_ids')
    def _check_order_lines(self):
        if not self.distribution_sample_product_ids:
            raise ValidationError('Cannot create picking without order lines.')

    @api.constrains('destination_location_id')
    def _check_destination_location(self):
        if not self.destination_location_id:
            raise ValidationError('Destination location must be set.')

    @api.constrains('user_id', 'destination_location_id', 'warehouse_id')
    def _check_duplicate_sample_location(self):
        if self.search([
            ('user_id', '=', self.user_id.id),
            ('destination_location_id', '=', self.destination_location_id.id),
            ('warehouse_id', '=', self.warehouse_id.id),
            ('id', '!=', self.id)
        ]):
            raise ValidationError('A sample location with the same user, destination location, and warehouse already exists.')

    def action_create_picking(self):
        for order in self:
            if not order.source_location_id or not order.destination_location_id:
                raise ValidationError('Source and Destination locations must be set.')
            if not order.distribution_sample_product_ids:
                raise ValidationError('Cannot create picking without order lines.')

            move_lines = [{
                'name': product.product_id.name,
                'product_id': product.product_id.id,
                'product_uom_qty': product.quantity,
                'product_uom': product.product_id.uom_id.id,
                'location_id': order.source_location_id.id,
                'location_dest_id': order.destination_location_id.id,
            } for product in order.distribution_sample_product_ids]

            if move_lines:
                picking_vals = {
                    'location_id': order.source_location_id.id,
                    'location_dest_id': order.destination_location_id.id,
                    'move_ids_without_package': [(0, 0, move) for move in move_lines],
                    'picking_type_id': self.env['stock.picking.type'].search([('code', '=', 'outgoing')], limit=1).id,
                    'origin': order.name,
                }
                picking = self.env['stock.picking'].create(picking_vals)
                picking.action_confirm()
                picking.action_assign()
                if order.auto_picking and picking.state == 'assigned':
                    picking.action_done()

    def action_view_picking(self):
        self.ensure_one()
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        pickings = self.env['stock.picking'].search([('origin', '=', self.name)])
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            action['views'] = form_view + [(action['views'][0][0], 'tree')]
            action['res_id'] = pickings.id
        return action

    def _check_stock_availability(self, products):
        for product in products:
            if product.product_id.qty_available < product.quantity:
                raise ValidationError(f'Insufficient stock for product {product.product_id.name}.')

    @api.model
    def create(self, vals):
        record = super(DistributionSampleOrder, self).create(vals)
        record._check_order_lines()
        record._check_destination_location()
        record._check_duplicate_sample_location()
        return record
