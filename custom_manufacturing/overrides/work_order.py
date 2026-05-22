import frappe
from frappe import _
from erpnext.manufacturing.doctype.work_order.work_order import WorkOrder


class CustomWorkOrder(WorkOrder):
    """
    Custom Work Order override
    Allows Work Orders without BOM.
    Preserves standard ERPNext behavior when checkbox is unchecked.
    """

    def validate(self):
        """
        Main validation override.

        STANDARD FLOW:
        If checkbox is NOT enabled:
        -> Run normal ERPNext validation

        CUSTOM FLOW:
        If checkbox IS enabled:
        -> Skip BOM validation
        -> Allow manual raw materials
        -> Allow manual operations
        """

        # STANDARD ERPNext FLOW
        if not self.custom_allow_without_bom:
            super().validate()
            return

        # CUSTOM FLOW WITHOUT BOM

        # Keep standard quantity validation
        self.validate_qty()

        # Validate manually entered items
        self.validate_required_items()

        # Validate manually entered operations
        self.validate_operations()


    def validate_required_items(self):
        """
        Ensure Required Items table is not empty
        when BOM is bypassed.
        """

        if not self.required_items:
            frappe.throw(
                _("Required Items table cannot be empty when BOM is not used.")
            )


    def validate_operations(self):
        """
        Optional validation for operations.

        Uncomment if operations should be mandatory.
        """

        """
        if not self.operations:
            frappe.throw(
                _("Operations table cannot be empty.")
            )
        """

        pass


    def set_required_items(self, reset_only_qty=False):
        """
        Prevent ERPNext from auto-fetching BOM items
        when custom checkbox is enabled.
        """

        if self.custom_allow_without_bom:
            return

        # STANDARD ERPNext BEHAVIOR
        super().set_required_items(reset_only_qty)


    def set_operations(self):
        """
        Prevent ERPNext from auto-fetching operations
        from BOM when checkbox enabled.
        """

        if self.custom_allow_without_bom:
            return

        # STANDARD ERPNext BEHAVIOR
        super().set_operations()


    def validate_bom_no(self):
        """
        Skip BOM validation when custom checkbox enabled.
        """

        if self.custom_allow_without_bom:
            return

        # STANDARD ERPNext BEHAVIOR
        super().validate_bom_no()