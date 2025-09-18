# Copyright (c) 2024, Zinye Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today, flt, cint
from datetime import datetime, timedelta


class CRMPartner(Document):
    """
    CRM Partner DocType for managing business partners in the PRM system.

    This class handles partner lifecycle management including:
    - Partner validation and data integrity
    - Performance metrics calculation
    - Status management and workflows
    - Integration with leads and deals
    """

    def validate(self):
        """Validate partner data before saving"""
        self.validate_partner_code()
        self.validate_agreement_dates()
        self.validate_commission_and_discount()
        self.set_partner_code_if_empty()
        self.validate_email_uniqueness()

    def before_save(self):
        """Execute before saving the document"""
        self.calculate_performance_metrics()
        self.update_partner_score()
        self.set_onboarding_status()

    def after_insert(self):
        """Execute after inserting new partner"""
        self.create_partner_user()
        self.send_welcome_notification()
        self.create_onboarding_tasks()

    def on_update(self):
        """Execute when partner is updated"""
        self.sync_partner_permissions()
        if self.has_value_changed('status'):
            self.handle_status_change()

    def validate_partner_code(self):
        """Validate partner code format and uniqueness"""
        if self.partner_code:
            # Check if partner code already exists
            existing = frappe.db.exists("CRM Partner", {
                "partner_code": self.partner_code,
                "name": ["!=", self.name]
            })
            if existing:
                frappe.throw(_("Partner Code {0} already exists").format(self.partner_code))

    def validate_agreement_dates(self):
        """Validate agreement start and end dates"""
        if self.agreement_start_date and self.agreement_end_date:
            if getdate(self.agreement_start_date) >= getdate(self.agreement_end_date):
                frappe.throw(_("Agreement End Date must be after Agreement Start Date"))

    def validate_commission_and_discount(self):
        """Validate commission rate and discount level"""
        if self.commission_rate and (self.commission_rate < 0 or self.commission_rate > 100):
            frappe.throw(_("Commission Rate must be between 0 and 100"))

        if self.discount_level and (self.discount_level < 0 or self.discount_level > 100):
            frappe.throw(_("Discount Level must be between 0 and 100"))

    def set_partner_code_if_empty(self):
        """Auto-generate partner code if not provided"""
        if not self.partner_code:
            # Generate code based on partner name and type
            code_base = "".join([c.upper() for c in self.partner_name.split() if c])[:6]
            type_code = self.partner_type[:3].upper() if self.partner_type else "GEN"

            counter = 1
            while True:
                proposed_code = f"{code_base}{type_code}{counter:03d}"
                if not frappe.db.exists("CRM Partner", {"partner_code": proposed_code}):
                    self.partner_code = proposed_code
                    break
                counter += 1

    def validate_email_uniqueness(self):
        """Ensure email is unique across partners"""
        if self.email:
            existing = frappe.db.exists("CRM Partner", {
                "email": self.email,
                "name": ["!=", self.name]
            })
            if existing:
                frappe.throw(_("Email {0} is already registered with another partner").format(self.email))

    def calculate_performance_metrics(self):
        """Calculate and update performance metrics"""
        # Get deals closed by this partner
        deals = frappe.get_all("CRM Deal",
            filters={
                "partner": self.name,
                "status": "Won"
            },
            fields=["deal_value", "closed_date"]
        )

        if deals:
            self.total_deals_closed = len(deals)
            self.total_revenue_generated = sum([flt(deal.deal_value) for deal in deals])
            self.average_deal_size = self.total_revenue_generated / self.total_deals_closed

            # Get latest deal date
            latest_deal = max(deals, key=lambda x: x.closed_date) if deals else None
            if latest_deal:
                self.last_deal_date = latest_deal.closed_date

            # Calculate YTD revenue
            current_year = datetime.now().year
            ytd_deals = [deal for deal in deals if getdate(deal.closed_date).year == current_year]
            self.ytd_revenue = sum([flt(deal.deal_value) for deal in ytd_deals])
        else:
            self.total_deals_closed = 0
            self.total_revenue_generated = 0
            self.average_deal_size = 0
            self.ytd_revenue = 0

        # Calculate lead conversion rate
        total_leads = frappe.db.count("CRM Lead", {"partner": self.name})
        converted_leads = frappe.db.count("CRM Lead", {
            "partner": self.name,
            "status": "Converted"
        })

        if total_leads > 0:
            self.lead_conversion_rate = (converted_leads / total_leads) * 100
        else:
            self.lead_conversion_rate = 0

    def update_partner_score(self):
        """Calculate overall partner score based on multiple factors"""
        score = 0

        # Revenue performance (40% of score)
        if self.total_revenue_generated:
            # Normalize revenue to 40 points (assuming 1M = 40 points)
            revenue_score = min(40, (self.total_revenue_generated / 1000000) * 40)
            score += revenue_score

        # Conversion rate performance (30% of score)
        if self.lead_conversion_rate:
            # Normalize conversion rate to 30 points
            conversion_score = min(30, (self.lead_conversion_rate / 100) * 30)
            score += conversion_score

        # Training and certification (20% of score)
        training_score = 0
        if self.training_completed:
            training_score += 10
        if self.certification_obtained:
            training_score += 10
        score += training_score

        # Agreement compliance (10% of score)
        compliance_score = 0
        if self.status == "Active":
            compliance_score += 5
        if self.agreement_end_date and getdate(self.agreement_end_date) > getdate(today()):
            compliance_score += 5
        score += compliance_score

        self.partner_score = min(100, int(score))

    def set_onboarding_status(self):
        """Update onboarding status based on completion criteria"""
        if (self.training_completed and
            self.certification_obtained and
            self.portal_access_enabled and
            self.onboarding_status != "Completed"):

            self.onboarding_status = "Completed"
            self.onboarding_completion_date = today()

    def create_partner_user(self):
        """Create user account for partner portal access"""
        if self.email and not frappe.db.exists("User", self.email):
            user_doc = frappe.get_doc({
                "doctype": "User",
                "email": self.email,
                "first_name": self.primary_contact or self.partner_name,
                "user_type": "Website User",
                "role_profile_name": "Partner",
                "send_welcome_email": 0  # We'll send custom welcome
            })
            user_doc.insert(ignore_permissions=True)

            # Link user to partner
            frappe.db.set_value("CRM Partner", self.name, "user", user_doc.name)

    def send_welcome_notification(self):
        """Send welcome notification to new partner"""
        if self.email:
            # Create notification or email
            frappe.sendmail(
                recipients=[self.email],
                subject=_("Welcome to Zinye Partner Program"),
                template="partner_welcome",
                args={
                    "partner_name": self.partner_name,
                    "partner_tier": self.partner_tier,
                    "partner_manager": self.assigned_partner_manager
                }
            )

    def create_onboarding_tasks(self):
        """Create onboarding tasks for new partner"""
        tasks = [
            {
                "subject": _("Complete Partner Agreement"),
                "description": _("Review and sign the partner agreement"),
                "priority": "High"
            },
            {
                "subject": _("Product Training"),
                "description": _("Complete mandatory product training modules"),
                "priority": "High"
            },
            {
                "subject": _("Portal Setup"),
                "description": _("Set up partner portal access and preferences"),
                "priority": "Medium"
            },
            {
                "subject": _("Initial Business Review"),
                "description": _("Conduct initial business review with partner manager"),
                "priority": "Medium"
            }
        ]

        for task in tasks:
            todo = frappe.get_doc({
                "doctype": "ToDo",
                "subject": task["subject"],
                "description": task["description"],
                "priority": task["priority"],
                "reference_type": "CRM Partner",
                "reference_name": self.name,
                "assigned_by": frappe.session.user
            })

            if self.assigned_partner_manager:
                todo.allocated_to = self.assigned_partner_manager

            todo.insert(ignore_permissions=True)

    def sync_partner_permissions(self):
        """Sync partner permissions based on tier and status"""
        if self.status == "Active" and self.portal_access_enabled:
            # Enable specific permissions based on partner tier
            # This would integrate with Frappe's role and permission system
            pass

    def handle_status_change(self):
        """Handle partner status changes"""
        if self.status == "Active":
            self.enable_partner_access()
        elif self.status in ["Inactive", "Suspended", "Terminated"]:
            self.disable_partner_access()

    def enable_partner_access(self):
        """Enable partner portal access"""
        if self.email:
            user = frappe.get_doc("User", self.email)
            user.enabled = 1
            user.save(ignore_permissions=True)

    def disable_partner_access(self):
        """Disable partner portal access"""
        if self.email:
            user = frappe.get_doc("User", self.email)
            user.enabled = 0
            user.save(ignore_permissions=True)

    @frappe.whitelist()
    def get_partner_dashboard_data(self):
        """Get dashboard data for partner portal"""
        return {
            "partner_info": {
                "name": self.partner_name,
                "tier": self.partner_tier,
                "score": self.partner_score,
                "status": self.status
            },
            "performance": {
                "total_deals": self.total_deals_closed,
                "total_revenue": self.total_revenue_generated,
                "ytd_revenue": self.ytd_revenue,
                "conversion_rate": self.lead_conversion_rate
            },
            "recent_activity": self.get_recent_activity()
        }

    def get_recent_activity(self):
        """Get recent partner activity"""
        # This would return recent leads, deals, tasks, etc.
        return frappe.get_all("CRM Deal",
            filters={"partner": self.name},
            fields=["name", "organization", "deal_value", "status", "modified"],
            order_by="modified desc",
            limit=5
        )


# Utility functions for partner management

@frappe.whitelist()
def get_partner_by_email(email):
    """Get partner record by email"""
    return frappe.db.get_value("CRM Partner", {"email": email}, "*", as_dict=True)


@frappe.whitelist()
def get_partners_by_territory(territory):
    """Get all active partners in a territory"""
    return frappe.get_all("CRM Partner",
        filters={
            "territory": territory,
            "status": "Active"
        },
        fields=["name", "partner_name", "partner_tier", "partner_score"]
    )


@frappe.whitelist()
def calculate_partner_commission(partner, deal_value):
    """Calculate commission for a partner based on deal value"""
    partner_doc = frappe.get_doc("CRM Partner", partner)
    if partner_doc.commission_rate:
        return (flt(deal_value) * flt(partner_doc.commission_rate)) / 100
    return 0


@frappe.whitelist()
def get_partner_performance_report(partner, from_date=None, to_date=None):
    """Generate performance report for a partner"""
    if not from_date:
        from_date = frappe.utils.add_months(today(), -12)
    if not to_date:
        to_date = today()

    partner_doc = frappe.get_doc("CRM Partner", partner)

    # Get deals in date range
    deals = frappe.get_all("CRM Deal",
        filters={
            "partner": partner,
            "status": "Won",
            "closed_date": ["between", [from_date, to_date]]
        },
        fields=["deal_value", "closed_date", "organization"]
    )

    # Get leads in date range
    leads = frappe.get_all("CRM Lead",
        filters={
            "partner": partner,
            "creation": ["between", [from_date, to_date]]
        },
        fields=["status", "creation", "lead_name"]
    )

    return {
        "partner": partner_doc.partner_name,
        "period": f"{from_date} to {to_date}",
        "deals": deals,
        "leads": leads,
        "summary": {
            "total_deals": len(deals),
            "total_revenue": sum([flt(deal.deal_value) for deal in deals]),
            "total_leads": len(leads),
            "converted_leads": len([lead for lead in leads if lead.status == "Converted"])
        }
    }