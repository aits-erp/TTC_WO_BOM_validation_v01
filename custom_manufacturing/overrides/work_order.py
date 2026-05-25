import frappe
from frappe import _
from erpnext.manufacturing.doctype.work_order.work_order import WorkOrder

class CustomWorkOrder(WorkOrder):

    def before_validate(self):
        if self.custom_allow_without_bom:
            self.flags.ignore_mandatory = True
            self.bom_no = None
        try:
            super().before_validate()
        except AttributeError:
            pass

    def validate(self):
        if self.custom_allow_without_bom:
            critical_fields = {
                "production_item": "Item To Manufacture",
                "qty": "Qty To Manufacture",
                "company": "Company",
                "wip_warehouse": "Work-in-Progress Warehouse",
                "fg_warehouse": "Target Warehouse"
            }
            
            for field, label in critical_fields.items():
                if not getattr(self, field):
                    frappe.throw(_("{0} is a mandatory field").format(label))

            self.validate_qty()
            self.validate_required_items_custom()
            
            if hasattr(self, "calculate_operating_cost"):
                self.calculate_operating_cost()
                
            return

        if not self.bom_no:
            frappe.throw(_("BOM No is mandatory when 'Allow Without BOM' is unchecked."))
            
        super().validate()

    def validate_required_items_custom(self):
        if not self.required_items:
            frappe.throw(_("Required Items table cannot be empty. Please add raw materials manually."))

    def set_required_items(self, reset_only_qty=False):
        if self.custom_allow_without_bom:
            return
        super().set_required_items(reset_only_qty)

    def set_operations(self):
        if self.custom_allow_without_bom:
            return
        super().set_operations()

    # ====================================================================
    # THE FIX: Explicitly set the status to "Not Started" on Submit
    # ====================================================================
    def on_submit(self):
        if self.custom_allow_without_bom:
            self.status = "Not Started"
            self.db_set("status", "Not Started")
            
        # Run the standard Job Card creation and submit logic
        super().on_submit()