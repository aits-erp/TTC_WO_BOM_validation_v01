frappe.ui.form.on("Work Order", {

    refresh(frm) {

        toggle_bom_behavior(frm);
    },

    custom_allow_without_bom(frm) {

        toggle_bom_behavior(frm);

        // CUSTOM FLOW
        if (frm.doc.custom_allow_without_bom) {

            // Clear BOM field
            frm.set_value("bom_no", "");

            frappe.msgprint(
                __("BOM is now optional. Please add Required Items manually.")
            );
        }
    }
});


function toggle_bom_behavior(frm) {

    // CUSTOM FLOW
    if (frm.doc.custom_allow_without_bom) {

        // Make BOM non-mandatory
        frm.toggle_reqd("bom_no", false);

    }

    // STANDARD ERPNext FLOW
    else {

        // Restore BOM mandatory behavior
        frm.toggle_reqd("bom_no", true);
    }
}