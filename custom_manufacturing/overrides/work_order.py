import frappe
from frappe import _
from erpnext.manufacturing.doctype.work_order.work_order import WorkOrder

class CustomWorkOrder(WorkOrder):

    def before_validate(self):
        # 1. THE BYPASS: Tell Frappe to skip the database-level mandatory check
        if self.custom_allow_without_bom:
            self.flags.ignore_mandatory = True
            self.bom_no = None

        # Execute standard before_validate if ERPNext adds one in the future
        try:
            super().before_validate()
        except AttributeError:
            pass

    def validate(self):
        # CUSTOM FLOW WITHOUT BOM
        if self.custom_allow_without_bom:
            
            # 2. Because we told the backend to ignore ALL mandatory fields, 
            # we must manually verify the critical ones just to be safe.
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

            # Skip core BOM-based validations
            self.validate_qty()
            self.validate_required_items_custom()
            
            # Recalculate costs based on manually added items/operations
            if hasattr(self, "calculate_operating_cost"):
                self.calculate_operating_cost()
                
            return

        # STANDARD ERPNext FLOW
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