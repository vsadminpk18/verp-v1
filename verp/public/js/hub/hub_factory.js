frappe.provide('verp.hub');

frappe.views.MarketplaceFactory = class MarketplaceFactory extends frappe.views.Factory {
	show() {
		is_marketplace_disabled()
			.then(disabled => {
				if (disabled) {
					frappe.show_not_found('Marketplace');
					return;
				}

				if (frappe.pages.marketplace) {
					frappe.container.change_to('marketplace');
					verp.hub.marketplace.refresh();
				} else {
					this.make('marketplace');
				}
			});
	}

	make(page_name) {
		frappe.require('marketplace.bundle.js', () => {
			verp.hub.marketplace = new verp.hub.Marketplace({
				parent: this.make_page(true, page_name)
			});
		});
	}
};

function is_marketplace_disabled() {
	return frappe.call({
		method: "verp.hub_node.doctype.marketplace_settings.marketplace_settings.is_marketplace_enabled"
	}).then(r => r.message)
}
