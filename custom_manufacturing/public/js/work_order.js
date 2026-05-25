// --- THE GLOBAL API INTERCEPTOR ---
// This sits outside the form events to catch the rogue global frappe.call
if (!window.frappe_call_intercepted_for_bom) {
	const original_frappe_call = frappe.call;

	frappe.call = function(opts) {
		let method = typeof opts === "string" ? opts : opts.method;

		// If the system tries to fetch BOM details AND we are on a Work Order AND the checkbox is ticked
		if (
			method === "erpnext.manufacturing.doctype.work_order.work_order.get_item_details"
			&& cur_frm
			&& cur_frm.doctype === "Work Order"
			&& cur_frm.doc.custom_allow_without_bom
		) {

			// Silently fetch only basic item info without touching the backend BOM API
			if (cur_frm.doc.production_item) {
				frappe.db.get_value(
					"Item",
					cur_frm.doc.production_item,
					["item_name", "stock_uom", "description"]
				).then(r => {

					if (r && r.message) {
						cur_frm.set_value("item_name", r.message.item_name || "");
						cur_frm.set_value("stock_uom", r.message.stock_uom || "");
						cur_frm.set_value("description", r.message.description || "");
						cur_frm.set_value("bom_no", "");
					}

					// Fake a successful response so the core ERPNext script doesn't crash or throw a popup
					if (opts.callback) opts.callback({ message: {} });
					if (opts.always) opts.always();
				});

			} else {
				if (opts.callback) opts.callback({ message: {} });
				if (opts.always) opts.always();
			}

			// Return a resolved promise to KILL the server network request entirely
			return Promise.resolve();
		}

		// For every other API call in the system, proceed normally
		return original_frappe_call.apply(frappe, arguments);
	};

	// Mark as patched so we don't duplicate it on page reload
	window.frappe_call_intercepted_for_bom = true;
}

// --- STANDARD FORM EVENTS ---
frappe.ui.form.on("Work Order", {

	onload: function(frm) {
		if (frm.doc.custom_allow_without_bom) {
			frm.trigger("custom_allow_without_bom");
		}
	},

	refresh: function(frm) {
		frm.trigger("custom_allow_without_bom");
	},

	custom_allow_without_bom: function(frm) {

		let skip_bom = frm.doc.custom_allow_without_bom ? 1 : 0;

		// Toggle mandatory state
		frm.toggle_reqd("bom_no", !skip_bom);

		// Unlock standard child tables so the UI lets you add rows
		frm.set_df_property("required_items", "read_only", skip_bom ? 0 : 1);
		frm.set_df_property("operations", "read_only", skip_bom ? 0 : 1);

		// ====================================================================
		// RAW MATERIALS GRID FIELD UNLOCKS
		// ====================================================================
		if (frm.fields_dict.required_items && frm.fields_dict.required_items.grid) {

			let required_grid = frm.fields_dict.required_items.grid;

			// Existing working field
			required_grid.update_docfield_property(
				'item_code',
				'read_only',
				skip_bom ? 0 : 1
			);

			// NEW FIELDS
			required_grid.update_docfield_property(
				'required_qty',
				'read_only',
				skip_bom ? 0 : 1
			);

			required_grid.update_docfield_property(
				'transferred_qty',
				'read_only',
				skip_bom ? 0 : 1
			);

			required_grid.update_docfield_property(
				'consumed_qty',
				'read_only',
				skip_bom ? 0 : 1
			);

			required_grid.update_docfield_property(
				'returned_qty',
				'read_only',
				skip_bom ? 0 : 1
			);
		}
		// ====================================================================

		// ====================================================================
		// OPERATIONS GRID UNLOCK
		// ====================================================================
		if (frm.fields_dict.operations && frm.fields_dict.operations.grid) {

			let operations_grid = frm.fields_dict.operations.grid;

			operations_grid.update_docfield_property(
				'operation',
				'read_only',
				skip_bom ? 0 : 1
			);

			operations_grid.update_docfield_property(
				'workstation',
				'read_only',
				skip_bom ? 0 : 1
			);

			operations_grid.update_docfield_property(
				'time_in_mins',
				'read_only',
				skip_bom ? 0 : 1
			);

			operations_grid.update_docfield_property(
				'hour_rate',
				'read_only',
				skip_bom ? 0 : 1
			);
		}
		// ====================================================================

		if (skip_bom) {

			frm.set_value("bom_no", "");

			if (frm.doc.docstatus === 0) {

				// Prevent duplicate buttons on refresh
				frm.remove_custom_button(__("Add Raw Material"));
				frm.remove_custom_button(__("Add Operation"));

				// Add Raw Material Button
				frm.add_custom_button(__("Add Raw Material"), function() {

					let row = frm.add_child("required_items");

					frm.refresh_field("required_items");

					// Tiny timeout ensures the DOM has rendered the new row before editing
					setTimeout(() => {
						frm.get_field("required_items").grid.edit_row(row.name);
					}, 100);

				}).removeClass('btn-default').addClass('btn-primary');

				// ====================================================================
				// FIXED ADD OPERATION BUTTON
				// ====================================================================
				frm.add_custom_button(__("Add Operation"), function() {

					let row = frm.add_child("operations", {});

					frm.refresh_field("operations");

					setTimeout(() => {
						frm.get_field("operations").grid.edit_row(row.name);
					}, 100);

				});
				// ====================================================================
			}

		} else {

			// Clean up buttons if checkbox is unticked
			frm.remove_custom_button(__("Add Raw Material"));
			frm.remove_custom_button(__("Add Operation"));
		}
	}
});