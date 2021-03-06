# Python bytecode 2.7 (62211)
# Embedded file name: /Users/anuragmishra/frappe-develop/apps/verp/verp/buying/report/subcontracted_raw_materials_to_be_transferred/test_subcontracted_raw_materials_to_be_transferred.py
# Compiled at: 2019-05-06 10:24:35
# Decompiled by https://python-decompiler.com
from __future__ import unicode_literals
from verp.buying.doctype.purchase_order.test_purchase_order import create_purchase_order
from verp.buying.doctype.purchase_order.purchase_order import make_rm_stock_entry
from verp.stock.doctype.stock_entry.test_stock_entry import make_stock_entry
from verp.buying.report.subcontracted_raw_materials_to_be_transferred.subcontracted_raw_materials_to_be_transferred import execute
import json, frappe, unittest

class TestSubcontractedItemToBeTransferred(unittest.TestCase):

	def test_pending_and_transferred_qty(self):
		po = create_purchase_order(item_code='_Test FG Item', is_subcontracted='Yes', supplier_warehouse="_Test Warehouse 1 - _TC")

		# Material Receipt of RMs
		make_stock_entry(item_code='_Test Item', target='_Test Warehouse - _TC', qty=100, basic_rate=100)
		make_stock_entry(item_code='_Test Item Home Desktop 100', target='_Test Warehouse - _TC', qty=100, basic_rate=100)

		se = transfer_subcontracted_raw_materials(po)

		col, data = execute(filters=frappe._dict(
			{
				'supplier': po.supplier,
				'from_date': frappe.utils.get_datetime(frappe.utils.add_to_date(po.transaction_date, days=-10)),
				'to_date': frappe.utils.get_datetime(frappe.utils.add_to_date(po.transaction_date, days=10))
			}
		))
		po.reload()

		po_data = [row for row in data if row.get('purchase_order') == po.name]
		# Alphabetically sort to be certain of order
		po_data = sorted(po_data, key = lambda i: i['rm_item_code'])

		self.assertEqual(len(po_data), 2)
		self.assertEqual(po_data[0]['purchase_order'], po.name)

		self.assertEqual(po_data[0]['rm_item_code'], '_Test Item')
		self.assertEqual(po_data[0]['p_qty'], 8)
		self.assertEqual(po_data[0]['transferred_qty'], 2)

		self.assertEqual(po_data[1]['rm_item_code'], '_Test Item Home Desktop 100')
		self.assertEqual(po_data[1]['p_qty'], 19)
		self.assertEqual(po_data[1]['transferred_qty'], 1)

		se.cancel()
		po.cancel()

def transfer_subcontracted_raw_materials(po):
	# Order of supplied items fetched in PO is flaky
	transfer_qty_map = {
		'_Test Item': 2,
		'_Test Item Home Desktop 100': 1
	}

	item_1 = po.supplied_items[0].rm_item_code
	item_2 = po.supplied_items[1].rm_item_code

	rm_item = [
		{
			'name': po.supplied_items[0].name,
			'item_code': item_1,
			'rm_item_code': item_1,
			'item_name': item_1,
			'qty': transfer_qty_map[item_1],
			'warehouse': '_Test Warehouse - _TC',
			'rate': 100,
			'amount': 100 * transfer_qty_map[item_1],
			'stock_uom': 'Nos'
		},
		{
			'name': po.supplied_items[1].name,
			'item_code': item_2,
			'rm_item_code': item_2,
			'item_name': item_2,
			'qty': transfer_qty_map[item_2],
			'warehouse': '_Test Warehouse - _TC',
			'rate': 100,
			'amount': 100 * transfer_qty_map[item_2],
			'stock_uom': 'Nos'
		}
	]
	rm_item_string = json.dumps(rm_item)
	se = frappe.get_doc(make_rm_stock_entry(po.name, rm_item_string))
	se.from_warehouse = '_Test Warehouse - _TC'
	se.to_warehouse = '_Test Warehouse - _TC'
	se.stock_entry_type = 'Send to Subcontractor'
	se.save()
	se.submit()
	return se
