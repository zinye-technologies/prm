# Copyright (c) 2024, Zinye Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.permissions import add_permission, update_permission_property


def setup_partner_permissions():
    """
    Set up permissions for Partner Management System.
    This should be called during app installation or migration.
    """

    # Create Partner-specific roles if they don't exist
    create_partner_roles()

    # Set up DocType permissions
    setup_partner_doctype_permissions()
    setup_lead_partner_permissions()
    setup_deal_partner_permissions()

    # Set up user permissions for partner isolation
    setup_partner_user_permissions()


def create_partner_roles():
    """Create Partner-specific roles"""

    partner_roles = [
        {
            "role_name": "Partner Manager",
            "description": "Manages partner relationships and oversees partner operations"
        },
        {
            "role_name": "Partner",
            "description": "External partner with limited access to their own data"
        },
        {
            "role_name": "Partner Admin",
            "description": "Administrative access to partner management system"
        }
    ]

    for role_data in partner_roles:
        if not frappe.db.exists("Role", role_data["role_name"]):
            role_doc = frappe.get_doc({
                "doctype": "Role",
                "role_name": role_data["role_name"],
                "desk_access": 1 if role_data["role_name"] != "Partner" else 0,
                "description": role_data["description"]
            })
            role_doc.insert(ignore_permissions=True)


def setup_partner_doctype_permissions():
    """Set up permissions for CRM Partner DocType"""

    # Clear existing permissions
    frappe.db.delete("Custom DocPerm", {
        "parent": "CRM Partner",
        "parenttype": "DocType"
    })

    # Partner Manager permissions - Full access
    add_permission("CRM Partner", "Partner Manager", 0)
    update_permission_property("CRM Partner", "Partner Manager", 0, "read", 1)
    update_permission_property("CRM Partner", "Partner Manager", 0, "write", 1)
    update_permission_property("CRM Partner", "Partner Manager", 0, "create", 1)
    update_permission_property("CRM Partner", "Partner Manager", 0, "delete", 1)
    update_permission_property("CRM Partner", "Partner Manager", 0, "submit", 0)
    update_permission_property("CRM Partner", "Partner Manager", 0, "cancel", 0)
    update_permission_property("CRM Partner", "Partner Manager", 0, "amend", 0)
    update_permission_property("CRM Partner", "Partner Manager", 0, "report", 1)
    update_permission_property("CRM Partner", "Partner Manager", 0, "export", 1)
    update_permission_property("CRM Partner", "Partner Manager", 0, "import", 1)
    update_permission_property("CRM Partner", "Partner Manager", 0, "share", 1)
    update_permission_property("CRM Partner", "Partner Manager", 0, "print", 1)
    update_permission_property("CRM Partner", "Partner Manager", 0, "email", 1)

    # Partner Admin permissions - Full access
    add_permission("CRM Partner", "Partner Admin", 0)
    update_permission_property("CRM Partner", "Partner Admin", 0, "read", 1)
    update_permission_property("CRM Partner", "Partner Admin", 0, "write", 1)
    update_permission_property("CRM Partner", "Partner Admin", 0, "create", 1)
    update_permission_property("CRM Partner", "Partner Admin", 0, "delete", 1)
    update_permission_property("CRM Partner", "Partner Admin", 0, "report", 1)
    update_permission_property("CRM Partner", "Partner Admin", 0, "export", 1)
    update_permission_property("CRM Partner", "Partner Admin", 0, "import", 1)
    update_permission_property("CRM Partner", "Partner Admin", 0, "share", 1)
    update_permission_property("CRM Partner", "Partner Admin", 0, "print", 1)
    update_permission_property("CRM Partner", "Partner Admin", 0, "email", 1)

    # CRM Manager permissions - Full access
    add_permission("CRM Partner", "CRM Manager", 0)
    update_permission_property("CRM Partner", "CRM Manager", 0, "read", 1)
    update_permission_property("CRM Partner", "CRM Manager", 0, "write", 1)
    update_permission_property("CRM Partner", "CRM Manager", 0, "create", 1)
    update_permission_property("CRM Partner", "CRM Manager", 0, "delete", 1)
    update_permission_property("CRM Partner", "CRM Manager", 0, "report", 1)
    update_permission_property("CRM Partner", "CRM Manager", 0, "export", 1)
    update_permission_property("CRM Partner", "CRM Manager", 0, "print", 1)
    update_permission_property("CRM Partner", "CRM Manager", 0, "email", 1)

    # CRM User permissions - Read and Write
    add_permission("CRM Partner", "CRM User", 0)
    update_permission_property("CRM Partner", "CRM User", 0, "read", 1)
    update_permission_property("CRM Partner", "CRM User", 0, "write", 1)
    update_permission_property("CRM Partner", "CRM User", 0, "report", 1)
    update_permission_property("CRM Partner", "CRM User", 0, "export", 1)
    update_permission_property("CRM Partner", "CRM User", 0, "print", 1)
    update_permission_property("CRM Partner", "CRM User", 0, "email", 1)

    # Partner permissions - Read only their own record
    add_permission("CRM Partner", "Partner", 0)
    update_permission_property("CRM Partner", "Partner", 0, "read", 1)
    update_permission_property("CRM Partner", "Partner", 0, "if_owner", 1)
    update_permission_property("CRM Partner", "Partner", 0, "print", 1)


def setup_lead_partner_permissions():
    """Set up partner-specific permissions for CRM Lead"""

    # Partner Manager permissions - Full access to partner leads
    if not frappe.db.exists("Custom DocPerm", {
        "parent": "CRM Lead",
        "role": "Partner Manager"
    }):
        add_permission("CRM Lead", "Partner Manager", 0)
        update_permission_property("CRM Lead", "Partner Manager", 0, "read", 1)
        update_permission_property("CRM Lead", "Partner Manager", 0, "write", 1)
        update_permission_property("CRM Lead", "Partner Manager", 0, "create", 1)
        update_permission_property("CRM Lead", "Partner Manager", 0, "report", 1)
        update_permission_property("CRM Lead", "Partner Manager", 0, "export", 1)
        update_permission_property("CRM Lead", "Partner Manager", 0, "print", 1)
        update_permission_property("CRM Lead", "Partner Manager", 0, "email", 1)

    # Partner permissions - Read leads assigned to them
    if not frappe.db.exists("Custom DocPerm", {
        "parent": "CRM Lead",
        "role": "Partner"
    }):
        add_permission("CRM Lead", "Partner", 0)
        update_permission_property("CRM Lead", "Partner", 0, "read", 1)
        update_permission_property("CRM Lead", "Partner", 0, "write", 1)
        update_permission_property("CRM Lead", "Partner", 0, "user_permission_doctypes", '["CRM Partner"]')


def setup_deal_partner_permissions():
    """Set up partner-specific permissions for CRM Deal"""

    # Partner Manager permissions
    if not frappe.db.exists("Custom DocPerm", {
        "parent": "CRM Deal",
        "role": "Partner Manager"
    }):
        add_permission("CRM Deal", "Partner Manager", 0)
        update_permission_property("CRM Deal", "Partner Manager", 0, "read", 1)
        update_permission_property("CRM Deal", "Partner Manager", 0, "write", 1)
        update_permission_property("CRM Deal", "Partner Manager", 0, "create", 1)
        update_permission_property("CRM Deal", "Partner Manager", 0, "report", 1)
        update_permission_property("CRM Deal", "Partner Manager", 0, "export", 1)
        update_permission_property("CRM Deal", "Partner Manager", 0, "print", 1)
        update_permission_property("CRM Deal", "Partner Manager", 0, "email", 1)

    # Partner permissions - Read/Write deals assigned to them
    if not frappe.db.exists("Custom DocPerm", {
        "parent": "CRM Deal",
        "role": "Partner"
    }):
        add_permission("CRM Deal", "Partner", 0)
        update_permission_property("CRM Deal", "Partner", 0, "read", 1)
        update_permission_property("CRM Deal", "Partner", 0, "write", 1)
        update_permission_property("CRM Deal", "Partner", 0, "user_permission_doctypes", '["CRM Partner"]')


def setup_partner_user_permissions():
    """Set up user permissions to isolate partner data"""

    # This will be called when a partner user is created
    # to ensure they only see their own partner data
    pass


def apply_partner_user_permission(user_email, partner_name):
    """
    Apply user permissions to a partner user to restrict access
    to their own partner record only.

    Args:
        user_email (str): Email of the partner user
        partner_name (str): Name of the partner document
    """

    # Remove existing user permissions for this user and partner
    frappe.db.delete("User Permission", {
        "user": user_email,
        "allow": "CRM Partner"
    })

    # Add new user permission
    user_permission = frappe.get_doc({
        "doctype": "User Permission",
        "user": user_email,
        "allow": "CRM Partner",
        "for_value": partner_name,
        "applicable_for": "CRM Lead,CRM Deal,CRM Activity"
    })
    user_permission.insert(ignore_permissions=True)


def remove_partner_user_permission(user_email, partner_name):
    """
    Remove user permissions when partner access is revoked.

    Args:
        user_email (str): Email of the partner user
        partner_name (str): Name of the partner document
    """

    frappe.db.delete("User Permission", {
        "user": user_email,
        "allow": "CRM Partner",
        "for_value": partner_name
    })


def get_partner_permission_query_conditions(user=None):
    """
    Get permission query conditions for partners.
    This function is called by Frappe's permission system.

    Args:
        user (str): User email

    Returns:
        str: SQL conditions for filtering records
    """

    if not user:
        user = frappe.session.user

    # System Manager and Administrator have full access
    if "System Manager" in frappe.get_roles(user) or user == "Administrator":
        return ""

    # CRM Manager and Partner Manager have full access
    user_roles = frappe.get_roles(user)
    if "CRM Manager" in user_roles or "Partner Manager" in user_roles or "Partner Admin" in user_roles:
        return ""

    # Partner users only see their own partner record
    if "Partner" in user_roles:
        partner = frappe.db.get_value("CRM Partner", {"email": user}, "name")
        if partner:
            return f"`tabCRM Partner`.name = '{partner}'"
        else:
            return "1=0"  # No access if no partner record found

    # CRM Users see active partners only
    if "CRM User" in user_roles:
        return "`tabCRM Partner`.status != 'Terminated'"

    # Default: no access
    return "1=0"


def has_partner_permission(doc, user=None, permission_type="read"):
    """
    Check if user has permission for a specific partner document.

    Args:
        doc: Partner document
        user (str): User email
        permission_type (str): Type of permission to check

    Returns:
        bool: True if user has permission
    """

    if not user:
        user = frappe.session.user

    # System Manager and Administrator have full access
    if "System Manager" in frappe.get_roles(user) or user == "Administrator":
        return True

    # CRM Manager and Partner Manager have full access
    user_roles = frappe.get_roles(user)
    if "CRM Manager" in user_roles or "Partner Manager" in user_roles or "Partner Admin" in user_roles:
        return True

    # Partner users only access their own record
    if "Partner" in user_roles:
        return doc.email == user

    # CRM Users have read access to active partners
    if "CRM User" in user_roles:
        if permission_type == "read":
            return doc.status != "Terminated"
        elif permission_type == "write":
            return doc.status == "Active"

    return False


# Permission query hooks for doctypes
def get_crm_lead_permission_query_conditions(user=None):
    """Permission query for CRM Lead based on partner assignment"""

    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)

    # Partner users only see leads assigned to their partner
    if "Partner" in user_roles:
        partner = frappe.db.get_value("CRM Partner", {"email": user}, "name")
        if partner:
            return f"`tabCRM Lead`.partner = '{partner}'"
        else:
            return "1=0"

    return ""


def get_crm_deal_permission_query_conditions(user=None):
    """Permission query for CRM Deal based on partner assignment"""

    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)

    # Partner users only see deals assigned to their partner
    if "Partner" in user_roles:
        partner = frappe.db.get_value("CRM Partner", {"email": user}, "name")
        if partner:
            return f"`tabCRM Deal`.partner = '{partner}'"
        else:
            return "1=0"

    return ""