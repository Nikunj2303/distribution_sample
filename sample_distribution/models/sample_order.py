from odoo import api, models, fields,exceptions

class DistributionSampleOrder(models.Model):
    _name = 'distribution.sample.order'
    _description = 'Sample Order Distribution'

    name = fields.Char(string='Order Reference', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required=True)
    source_location_id = fields.Many2one('stock.location', string='Source Location', required=True)
    destination_location_id = fields.Many2one('stock.location', string='Destination Location', required=True)
    user_id = fields.Many2one('res.users', string='Assigned to', default=lambda self: self.env.user)
    distribution_sample_product_ids = fields.One2many('distribution.sample.product', 'order_id',
                                                      string='Sample Products')

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

    # @api.onchange('user_id')
    # def _onchange_user_id(self):
    #     if self.user_id:
    #         sample_location = self.env['stock.location'].search([
    #             ('user_id', '=', self.user_id.id),
    #             ('is_sample_location', '=', True),
    #             ('company_id', '=', self.env.company.id)
    #         ], limit=1)
    #         self.destination_location_id = sample_location.id if sample_location else False

    # def action_create_picking(self):
    #     for order in self:
    #         if not order.source_location_id or not order.destination_location_id:
    #             raise exceptions.UserError('Source and Destination locations must be set.')
    #
    #         picking_vals = {
    #             'location_id': order.source_location_id.id,
    #             'location_dest_id': order.destination_location_id.id,
    #             'move_lines': [(0, 0, {
    #                 'name': product.product_id.name,
    #                 'product_id': product.product_id.id,
    #                 'product_uom_qty': product.quantity,
    #                 'product_uom': product.product_id.uom_id.id,
    #             }) for product in order.distribution_sample_product_ids],
    #         }
    #         picking = self.env['stock.picking'].create(picking_vals)
    #         picking.action_confirm()
    #         picking.action_assign()
    #         if order.auto_picking and picking.state == 'assigned':
    #             picking.action_done()

    def action_create_picking(self):
        for order in self:
            if not order.source_location_id or not order.destination_location_id:
                raise exceptions.UserError('Source and Destination locations must be set.')

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
                    'move_ids_without_package': [(0, 0, move) for move in move_lines],
                }
                picking = self.env['stock.picking'].create(picking_vals)
                picking.action_confirm()
                picking.action_assign()
                if order.auto_picking and picking.state == 'assigned':
                    picking.action_done()
            else:
                # Handle case when there are no move lines
                pass

    def action_auto_create_picking(self):
        for order in self:
            pass

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