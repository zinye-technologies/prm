# Copyright (c) 2024, Zinye Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, today, flt, cint
from frappe.model.document import Document


@frappe.whitelist()
def get_partner_list(filters=None, limit=20, start=0, search_term=None):
    """
    Get list of partners with filtering and pagination support.

    Args:
        filters (dict): Filter criteria for partners
        limit (int): Number of records to return
        start (int): Starting offset for pagination
        search_term (str): Search term for partner name/email

    Returns:
        dict: List of partners with metadata
    """
    if not filters:
        filters = {}

    # Build search conditions
    conditions = []
    if search_term:
        conditions.append([
            "CRM Partner", "partner_name", "like", f"%{search_term}%"
        ])

    # Add status filter if not specified
    if "status" not in filters:
        filters["status"] = ["!=", "Terminated"]

    partners = frappe.get_list(
        "CRM Partner",
        filters=filters,
        fields=[
            "name", "partner_name", "partner_type", "partner_tier",
            "status", "email", "territory", "partner_score",
            "total_deals_closed", "total_revenue_generated", "modified"
        ],
        limit_start=start,
        limit_page_length=limit,
        order_by="partner_score desc, modified desc"
    )

    # Get total count for pagination
    total_count = frappe.db.count("CRM Partner", filters)

    return {
        "partners": partners,
        "total_count": total_count,
        "has_more": (start + limit) < total_count
    }


@frappe.whitelist()
def get_partner_details(partner_name):
    """
    Get detailed information about a specific partner.

    Args:
        partner_name (str): Name of the partner document

    Returns:
        dict: Complete partner information with performance data
    """
    try:
        partner = frappe.get_doc("CRM Partner", partner_name)

        # Check permissions
        if not partner.has_permission("read"):
            frappe.throw(_("Not permitted to view this partner"))

        # Get additional performance data
        performance_data = get_partner_performance_summary(partner_name)

        return {
            "partner": partner.as_dict(),
            "performance": performance_data,
            "recent_deals": get_partner_recent_deals(partner_name),
            "recent_leads": get_partner_recent_leads(partner_name)
        }

    except frappe.DoesNotExistError:
        frappe.throw(_("Partner not found"))


@frappe.whitelist()
def create_partner(partner_data):
    """
    Create a new partner record.

    Args:
        partner_data (dict): Partner information

    Returns:
        dict: Created partner record
    """
    try:
        # Validate required fields
        required_fields = ["partner_name", "partner_type", "partner_tier", "email"]
        for field in required_fields:
            if not partner_data.get(field):
                frappe.throw(_(f"Missing required field: {field}"))

        # Create partner document
        partner = frappe.get_doc({
            "doctype": "CRM Partner",
            **partner_data
        })

        partner.insert()
        frappe.db.commit()

        return {
            "success": True,
            "partner": partner.as_dict(),
            "message": _("Partner created successfully")
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.throw(_("Failed to create partner: {0}").format(str(e)))


@frappe.whitelist()
def update_partner(partner_name, partner_data):
    """
    Update an existing partner record.

    Args:
        partner_name (str): Name of the partner document
        partner_data (dict): Updated partner information

    Returns:
        dict: Updated partner record
    """
    try:
        partner = frappe.get_doc("CRM Partner", partner_name)

        # Check permissions
        if not partner.has_permission("write"):
            frappe.throw(_("Not permitted to update this partner"))

        # Update fields
        for field, value in partner_data.items():
            if hasattr(partner, field):
                setattr(partner, field, value)

        partner.save()
        frappe.db.commit()

        return {
            "success": True,
            "partner": partner.as_dict(),
            "message": _("Partner updated successfully")
        }

    except frappe.DoesNotExistError:
        frappe.throw(_("Partner not found"))
    except Exception as e:
        frappe.db.rollback()
        frappe.throw(_("Failed to update partner: {0}").format(str(e)))


@frappe.whitelist()
def get_partner_performance_summary(partner_name):
    """
    Get performance summary for a partner.

    Args:
        partner_name (str): Name of the partner document

    Returns:
        dict: Performance metrics and trends
    """
    # Monthly performance for the last 12 months
    from frappe.utils import add_months

    end_date = today()
    start_date = add_months(end_date, -12)

    # Get monthly deal closures
    monthly_deals = frappe.db.sql("""
        SELECT
            DATE_FORMAT(closed_date, '%Y-%m') as month,
            COUNT(*) as deals_count,
            SUM(deal_value) as revenue
        FROM `tabCRM Deal`
        WHERE partner = %s
            AND status = 'Won'
            AND closed_date BETWEEN %s AND %s
        GROUP BY DATE_FORMAT(closed_date, '%Y-%m')
        ORDER BY month
    """, (partner_name, start_date, end_date), as_dict=True)

    # Get lead conversion trends
    monthly_leads = frappe.db.sql("""
        SELECT
            DATE_FORMAT(creation, '%Y-%m') as month,
            COUNT(*) as total_leads,
            SUM(CASE WHEN status = 'Converted' THEN 1 ELSE 0 END) as converted_leads
        FROM `tabCRM Lead`
        WHERE partner = %s
            AND creation BETWEEN %s AND %s
        GROUP BY DATE_FORMAT(creation, '%Y-%m')
        ORDER BY month
    """, (partner_name, start_date, end_date), as_dict=True)

    # Current quarter performance
    current_quarter_start = frappe.utils.get_quarter_start(today())
    current_quarter_deals = frappe.db.sql("""
        SELECT COUNT(*) as deals, SUM(deal_value) as revenue
        FROM `tabCRM Deal`
        WHERE partner = %s
            AND status = 'Won'
            AND closed_date >= %s
    """, (partner_name, current_quarter_start), as_dict=True)[0]

    return {
        "monthly_trends": {
            "deals": monthly_deals,
            "leads": monthly_leads
        },
        "current_quarter": current_quarter_deals,
        "summary_period": f"{start_date} to {end_date}"
    }


@frappe.whitelist()
def get_partner_recent_deals(partner_name, limit=10):
    """Get recent deals for a partner"""
    return frappe.get_list(
        "CRM Deal",
        filters={"partner": partner_name},
        fields=[
            "name", "organization", "deal_value", "status",
            "expected_closure_date", "closed_date", "modified"
        ],
        order_by="modified desc",
        limit_page_length=limit
    )


@frappe.whitelist()
def get_partner_recent_leads(partner_name, limit=10):
    """Get recent leads for a partner"""
    return frappe.get_list(
        "CRM Lead",
        filters={"partner": partner_name},
        fields=[
            "name", "lead_name", "organization", "email",
            "status", "source", "modified"
        ],
        order_by="modified desc",
        limit_page_length=limit
    )


@frappe.whitelist()
def assign_lead_to_partner(lead_name, partner_name, reason=None):
    """
    Assign a lead to a partner.

    Args:
        lead_name (str): Name of the lead document
        partner_name (str): Name of the partner document
        reason (str): Reason for assignment

    Returns:
        dict: Assignment result
    """
    try:
        # Get and validate lead
        lead = frappe.get_doc("CRM Lead", lead_name)
        if not lead.has_permission("write"):
            frappe.throw(_("Not permitted to assign this lead"))

        # Get and validate partner
        partner = frappe.get_doc("CRM Partner", partner_name)
        if partner.status != "Active":
            frappe.throw(_("Cannot assign lead to inactive partner"))

        # Update lead
        lead.partner = partner_name
        lead.lead_owner = partner.assigned_partner_manager or frappe.session.user
        lead.save()

        # Create activity log
        frappe.get_doc({
            "doctype": "CRM Activity",
            "activity_type": "Lead Assignment",
            "subject": f"Lead assigned to partner {partner.partner_name}",
            "description": reason or f"Lead {lead.lead_name} assigned to partner {partner.partner_name}",
            "reference_doctype": "CRM Lead",
            "reference_name": lead_name,
            "assigned_to": partner.assigned_partner_manager,
            "status": "Completed"
        }).insert()

        frappe.db.commit()

        return {
            "success": True,
            "message": _("Lead assigned to partner successfully"),
            "lead": lead.as_dict(),
            "partner": partner.partner_name
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.throw(_("Failed to assign lead to partner: {0}").format(str(e)))


@frappe.whitelist()
def get_partner_territories():
    """Get list of territories with partner counts"""
    territories = frappe.db.sql("""
        SELECT
            territory,
            COUNT(*) as partner_count,
            AVG(partner_score) as avg_score
        FROM `tabCRM Partner`
        WHERE status = 'Active'
            AND territory IS NOT NULL
        GROUP BY territory
        ORDER BY partner_count DESC
    """, as_dict=True)

    return territories


@frappe.whitelist()
def get_partner_types_summary():
    """Get summary of partners by type"""
    summary = frappe.db.sql("""
        SELECT
            partner_type,
            COUNT(*) as count,
            AVG(partner_score) as avg_score,
            SUM(total_revenue_generated) as total_revenue
        FROM `tabCRM Partner`
        WHERE status = 'Active'
        GROUP BY partner_type
        ORDER BY total_revenue DESC
    """, as_dict=True)

    return summary


@frappe.whitelist()
def partner_dashboard_stats():
    """Get overall partner dashboard statistics"""
    stats = {}

    # Total partners by status
    stats["partners_by_status"] = frappe.db.sql("""
        SELECT status, COUNT(*) as count
        FROM `tabCRM Partner`
        GROUP BY status
    """, as_dict=True)

    # Top performing partners this month
    current_month = frappe.utils.get_first_day_of_week(today())
    stats["top_partners_this_month"] = frappe.db.sql("""
        SELECT
            p.partner_name,
            p.partner_tier,
            COUNT(d.name) as deals_closed,
            SUM(d.deal_value) as revenue
        FROM `tabCRM Partner` p
        LEFT JOIN `tabCRM Deal` d ON d.partner = p.name
            AND d.status = 'Won'
            AND d.closed_date >= %s
        WHERE p.status = 'Active'
        GROUP BY p.name
        ORDER BY revenue DESC
        LIMIT 5
    """, (current_month,), as_dict=True)

    # Partner onboarding status
    stats["onboarding_status"] = frappe.db.sql("""
        SELECT onboarding_status, COUNT(*) as count
        FROM `tabCRM Partner`
        WHERE status = 'Active'
        GROUP BY onboarding_status
    """, as_dict=True)

    return stats


@frappe.whitelist()
def search_partners(search_term, partner_type=None, territory=None, limit=10):
    """
    Search partners by name, email, or other criteria.

    Args:
        search_term (str): Search term
        partner_type (str): Filter by partner type
        territory (str): Filter by territory
        limit (int): Number of results to return

    Returns:
        list: Matching partner records
    """
    filters = {"status": ["!=", "Terminated"]}

    if partner_type:
        filters["partner_type"] = partner_type

    if territory:
        filters["territory"] = territory

    # Search in multiple fields
    or_filters = []
    if search_term:
        or_filters = [
            ["partner_name", "like", f"%{search_term}%"],
            ["email", "like", f"%{search_term}%"],
            ["partner_code", "like", f"%{search_term}%"],
            ["primary_contact", "like", f"%{search_term}%"]
        ]

    partners = frappe.get_list(
        "CRM Partner",
        filters=filters,
        or_filters=or_filters,
        fields=[
            "name", "partner_name", "partner_type", "partner_tier",
            "email", "partner_score", "status"
        ],
        limit_page_length=limit,
        order_by="partner_score desc"
    )

    return partners