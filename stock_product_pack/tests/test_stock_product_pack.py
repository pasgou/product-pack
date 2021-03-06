# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import SavepointCase
import logging

_logger = logging.getLogger(__name__)


class TestSaleProductPack(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        category_all_id = cls.env.ref('product.product_category_all').id
        product_obj = cls.env['product.product']
        cls.pack_dc = cls.env['product.product'].create({
            'name': 'Pack',
            'type': 'product',
            'pack_ok': True,
            'pack_type': 'detailed',
            'pack_component_price': 'detailed',
            'categ_id': category_all_id,
            'pack_line_ids': [
                (0, 0, {
                    'product_id': product_obj.create({
                        'name': 'Component 1',
                        'type': 'product',
                        'categ_id': category_all_id,
                    }).id,
                    'quantity': 1,
                }),
                (0, 0, {
                    'product_id': product_obj.create({
                        'name': 'Component 2',
                        'type': 'product',
                        'categ_id': category_all_id,
                    }).id,
                    'quantity': 1,
                }),
                (0, 0, {
                    'product_id': product_obj.create({
                        'name': 'Component 3',
                        'type': 'service',
                        'categ_id': category_all_id,
                    }).id,
                    'quantity': 1,
                }),
                (0, 0, {
                    'product_id': product_obj.create({
                        'name': 'Component 4',
                        'type': 'consu',
                        'categ_id': category_all_id,
                    }).id,
                    'quantity': 1,
                }),
            ]
        })

    def test_compute_quantities_dict(self):
        location_id = self.env.ref('stock.stock_location_suppliers').id,
        location_dest_id = self.env.ref('stock.stock_location_stock').id,
        components = self.pack_dc.pack_line_ids.mapped('product_id')
        picking = self.env['stock.picking'].create({
            'partner_id': self.env.ref('base.res_partner_4').id,
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'move_lines': [
                (0, 0, {
                    'name': 'incoming_move_test_01',
                    'product_id': components[0].id,
                    'product_uom_qty': 5,
                    'product_uom': components[0].uom_id.id,
                    'location_id': location_id,
                    'location_dest_id': location_dest_id,
                }),
                (0, 0, {
                    'name': 'incoming_move_test_02',
                    'product_id': components[1].id,
                    'product_uom_qty': 7,
                    'product_uom': components[1].uom_id.id,
                    'location_id': location_id,
                    'location_dest_id': location_dest_id,
                }),
            ]
        })
        picking.action_confirm()
        self.assertEqual(self.pack_dc.virtual_available, 5)
        self.assertEqual(self.pack_dc.qty_available, 0)
        wizard_dict = picking.button_validate()
        wizard = self.env[wizard_dict['res_model']].browse(
            wizard_dict['res_id'])
        wizard.process()
        self.assertEqual(self.pack_dc.virtual_available, 5)
        self.assertEqual(self.pack_dc.qty_available, 5)
