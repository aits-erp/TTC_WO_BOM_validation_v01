import frappe
from frappe import _
from erpnext.manufacturing.doctype.work_order.work_order import WorkOrder


class CustomWorkOrder(WorkOrder):

    def validate(self):

        # CUSTOM FLOW WITHOUT BOM
        if self.custom_allow_without_bom:

            # Temporary fake BOM bypass
            original_bom = self.bom_no

            # Put dummy value so ERPNext internal validations continue
            self.bom_no = None

            # Run standard ERPNext validations
            try:
                super().validate()

            except Exception as e:

                # Ignore only BOM mandatory errors
                if "BOM" not in str(e):
                    raise

            # Restore BOM
            self.bom_no = original_bom

            # Ensure manual raw materials exist
            self.validate_required_items()

            return

        # STANDARD ERPNext FLOW
        super().validate()


    def validate_required_items(self):

        if not self.required_items:
            frappe.throw(
                _("Required Items table cannot be empty when BOM is not used.")
            )


    def set_required_items(self, reset_only_qty=False):

        if self.custom_allow_without_bom:
            return

        super().set_required_items(reset_only_qty)


    def set_operations(self):

        if self.custom_allow_without_bom:
            return

        super().set_operations()