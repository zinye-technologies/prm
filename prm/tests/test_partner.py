# Copyright (c) 2024, Zinye Technologies and contributors
# For license information, please see license.txt

import unittest
import frappe
from frappe.utils import today, add_days, add_months
from frappe.test_runner import make_test_records

from prm.fcrm.doctype.crm_partner.crm_partner import CRMPartner


class TestCRMPartner(unittest.TestCase):
    """Test cases for CRM Partner DocType"""

    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        make_test_records("Country")
        make_test_records("Territory")
        make_test_records("CRM Industry")

    def setUp(self):
        """Set up before each test"""
        # Clean up existing test partners
        frappe.db.delete("CRM Partner", {"partner_name": ["like", "Test Partner%"]})
        frappe.db.commit()

    def tearDown(self):
        """Clean up after each test"""
        # Clean up test data
        frappe.db.delete("CRM Partner", {"partner_name": ["like", "Test Partner%"]})
        frappe.db.commit()

    def test_partner_creation(self):
        """Test creating a new partner"""
        partner = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "Test Partner Corp",
            "partner_type": "Reseller",
            "partner_tier": "Gold",
            "email": "test@testpartner.com",
            "primary_contact": "John Doe",
            "phone": "+1-555-0123",
            "territory": "All Territories",
            "commission_rate": 15.0,
            "discount_level": 10.0
        })

        partner.insert()
        self.assertTrue(partner.name)
        self.assertEqual(partner.status, "Pending Approval")
        self.assertTrue(partner.partner_code)  # Should be auto-generated

        # Check that partner code is unique
        partner2 = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "Test Partner Corp 2",
            "partner_type": "Distributor",
            "partner_tier": "Silver",
            "email": "test2@testpartner.com"
        })
        partner2.insert()
        self.assertNotEqual(partner.partner_code, partner2.partner_code)

    def test_partner_validation(self):
        """Test partner validation rules"""

        # Test duplicate email validation
        partner1 = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "Test Partner 1",
            "partner_type": "Reseller",
            "partner_tier": "Gold",
            "email": "duplicate@test.com"
        })
        partner1.insert()

        partner2 = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "Test Partner 2",
            "partner_type": "Distributor",
            "partner_tier": "Silver",
            "email": "duplicate@test.com"
        })

        with self.assertRaises(frappe.ValidationError):
            partner2.insert()

        # Test commission rate validation
        partner3 = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "Test Partner 3",
            "partner_type": "Reseller",
            "partner_tier": "Gold",
            "email": "test3@test.com",
            "commission_rate": 150.0  # Invalid: > 100
        })

        with self.assertRaises(frappe.ValidationError):
            partner3.insert()

        # Test agreement date validation
        partner4 = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "Test Partner 4",
            "partner_type": "Reseller",
            "partner_tier": "Gold",
            "email": "test4@test.com",
            "agreement_start_date": today(),
            "agreement_end_date": add_days(today(), -1)  # Invalid: end before start
        })

        with self.assertRaises(frappe.ValidationError):
            partner4.insert()

    def test_partner_code_generation(self):
        """Test automatic partner code generation"""
        partner = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "Test Partner for Code Gen",
            "partner_type": "Reseller",
            "partner_tier": "Gold",
            "email": "codetest@test.com"
        })
        partner.insert()

        # Should have auto-generated code
        self.assertTrue(partner.partner_code)
        self.assertIn("RES", partner.partner_code)  # Should contain partner type code

        # Test custom partner code
        partner2 = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "Test Partner Custom Code",
            "partner_type": "Distributor",
            "partner_tier": "Silver",
            "email": "custom@test.com",
            "partner_code": "CUSTOM001"
        })
        partner2.insert()
        self.assertEqual(partner2.partner_code, "CUSTOM001")

    def test_performance_metrics_calculation(self):
        """Test performance metrics calculation"""
        # Create a partner
        partner = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "Test Performance Partner",
            "partner_type": "Reseller",
            "partner_tier": "Gold",
            "email": "performance@test.com"
        })
        partner.insert()

        # Create test deals
        for i in range(3):
            deal = frappe.get_doc({
                "doctype": "CRM Deal",
                "organization": f"Test Org {i+1}",
                "deal_value": 10000 * (i + 1),
                "status": "Won",
                "partner": partner.name,
                "closed_date": today()
            })
            deal.insert()

        # Create test leads
        for i in range(5):
            lead = frappe.get_doc({
                "doctype": "CRM Lead",
                "lead_name": f"Test Lead {i+1}",
                "email": f"lead{i+1}@test.com",
                "partner": partner.name,
                "status": "Converted" if i < 3 else "Open"
            })
            lead.insert()

        # Reload partner to trigger metric calculation
        partner.reload()
        partner.save()

        self.assertEqual(partner.total_deals_closed, 3)
        self.assertEqual(partner.total_revenue_generated, 60000)
        self.assertEqual(partner.average_deal_size, 20000)
        self.assertEqual(partner.lead_conversion_rate, 60.0)

    def test_partner_score_calculation(self):
        """Test partner score calculation"""
        partner = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "Test Score Partner",
            "partner_type": "Reseller",
            "partner_tier": "Gold",
            "email": "score@test.com",
            "total_revenue_generated": 500000,
            "lead_conversion_rate": 75.0,
            "training_completed": 1,
            "certification_obtained": 1,
            "status": "Active",
            "agreement_end_date": add_months(today(), 12)
        })
        partner.insert()

        # Check that partner score is calculated
        self.assertGreater(partner.partner_score, 0)
        self.assertLessEqual(partner.partner_score, 100)

    def test_onboarding_status_update(self):
        """Test onboarding status automatic updates"""
        partner = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "Test Onboarding Partner",
            "partner_type": "Reseller",
            "partner_tier": "Gold",
            "email": "onboarding@test.com",
            "training_completed": 1,
            "certification_obtained": 1,
            "portal_access_enabled": 1
        })
        partner.insert()

        self.assertEqual(partner.onboarding_status, "Completed")
        self.assertEqual(partner.onboarding_completion_date, today())

    def test_partner_user_creation(self):
        """Test partner user creation"""
        partner = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "Test User Partner",
            "partner_type": "Reseller",
            "partner_tier": "Gold",
            "email": "usertest@testpartner.com",
            "primary_contact": "Jane Smith"
        })
        partner.insert()

        # Check if user was created
        user_exists = frappe.db.exists("User", "usertest@testpartner.com")
        self.assertTrue(user_exists)

        user = frappe.get_doc("User", "usertest@testpartner.com")
        self.assertEqual(user.first_name, "Jane Smith")
        self.assertEqual(user.user_type, "Website User")

    def test_partner_status_workflow(self):
        """Test partner status changes and workflows"""
        partner = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "Test Workflow Partner",
            "partner_type": "Reseller",
            "partner_tier": "Gold",
            "email": "workflow@test.com"
        })
        partner.insert()

        # Initial status should be Pending Approval
        self.assertEqual(partner.status, "Pending Approval")

        # Activate partner
        partner.status = "Active"
        partner.save()

        # Check user is enabled
        user = frappe.get_doc("User", "workflow@test.com")
        self.assertEqual(user.enabled, 1)

        # Suspend partner
        partner.status = "Suspended"
        partner.save()

        # Check user is disabled
        user.reload()
        self.assertEqual(user.enabled, 0)

    def test_api_partner_list(self):
        """Test partner list API"""
        # Create test partners
        for i in range(5):
            partner = frappe.get_doc({
                "doctype": "CRM Partner",
                "partner_name": f"Test API Partner {i+1}",
                "partner_type": "Reseller" if i % 2 == 0 else "Distributor",
                "partner_tier": "Gold",
                "email": f"api{i+1}@test.com",
                "status": "Active"
            })
            partner.insert()

        # Test API call
        from prm.api.partner import get_partner_list

        result = get_partner_list(limit=10)
        self.assertIn("partners", result)
        self.assertIn("total_count", result)
        self.assertGreaterEqual(len(result["partners"]), 5)

        # Test filtering
        result_filtered = get_partner_list(
            filters={"partner_type": "Reseller"},
            limit=10
        )
        for partner in result_filtered["partners"]:
            self.assertEqual(partner["partner_type"], "Reseller")

    def test_api_partner_details(self):
        """Test partner details API"""
        partner = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "Test Details Partner",
            "partner_type": "Reseller",
            "partner_tier": "Gold",
            "email": "details@test.com"
        })
        partner.insert()

        from prm.api.partner import get_partner_details

        result = get_partner_details(partner.name)
        self.assertIn("partner", result)
        self.assertIn("performance", result)
        self.assertEqual(result["partner"]["partner_name"], "Test Details Partner")

    def test_api_create_partner(self):
        """Test partner creation API"""
        from prm.api.partner import create_partner

        partner_data = {
            "partner_name": "API Created Partner",
            "partner_type": "Distributor",
            "partner_tier": "Silver",
            "email": "apicreated@test.com",
            "primary_contact": "API User"
        }

        result = create_partner(partner_data)
        self.assertTrue(result["success"])
        self.assertIn("partner", result)

        # Verify partner was created
        partner_exists = frappe.db.exists("CRM Partner", {
            "partner_name": "API Created Partner"
        })
        self.assertTrue(partner_exists)

    def test_lead_assignment_to_partner(self):
        """Test lead assignment to partner"""
        # Create partner
        partner = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "Test Lead Assignment Partner",
            "partner_type": "Reseller",
            "partner_tier": "Gold",
            "email": "leadassign@test.com",
            "status": "Active"
        })
        partner.insert()

        # Create lead
        lead = frappe.get_doc({
            "doctype": "CRM Lead",
            "lead_name": "Test Assignment Lead",
            "email": "testlead@test.com"
        })
        lead.insert()

        from prm.api.partner import assign_lead_to_partner

        result = assign_lead_to_partner(
            lead.name,
            partner.name,
            "Test assignment"
        )

        self.assertTrue(result["success"])

        # Verify assignment
        lead.reload()
        self.assertEqual(lead.partner, partner.name)

    def test_commission_calculation(self):
        """Test commission calculation"""
        partner = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "Test Commission Partner",
            "partner_type": "Reseller",
            "partner_tier": "Gold",
            "email": "commission@test.com",
            "commission_rate": 15.0
        })
        partner.insert()

        from prm.api.partner import calculate_partner_commission

        commission = calculate_partner_commission(partner.name, 10000)
        self.assertEqual(commission, 1500.0)

    def test_performance_report(self):
        """Test performance report generation"""
        partner = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "Test Report Partner",
            "partner_type": "Reseller",
            "partner_tier": "Gold",
            "email": "report@test.com"
        })
        partner.insert()

        from prm.api.partner import get_partner_performance_report

        report = get_partner_performance_report(partner.name)
        self.assertIn("partner", report)
        self.assertIn("period", report)
        self.assertIn("summary", report)


class TestPartnerPermissions(unittest.TestCase):
    """Test cases for Partner permission system"""

    def setUp(self):
        """Set up test users and permissions"""
        # Create test users with different roles
        self.create_test_user("partner.manager@test.com", ["Partner Manager"])
        self.create_test_user("partner.user@test.com", ["Partner"])
        self.create_test_user("crm.user@test.com", ["CRM User"])

    def create_test_user(self, email, roles):
        """Create a test user with specified roles"""
        if not frappe.db.exists("User", email):
            user = frappe.get_doc({
                "doctype": "User",
                "email": email,
                "first_name": "Test",
                "user_type": "System User",
                "send_welcome_email": 0
            })
            user.insert(ignore_permissions=True)

            for role in roles:
                user.add_roles(role)

    def test_partner_manager_permissions(self):
        """Test Partner Manager permissions"""
        # Switch to partner manager user
        frappe.set_user("partner.manager@test.com")

        # Should be able to create partners
        partner = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "Manager Test Partner",
            "partner_type": "Reseller",
            "partner_tier": "Gold",
            "email": "managertest@test.com"
        })
        partner.insert()
        self.assertTrue(partner.name)

        # Should be able to read all partners
        partners = frappe.get_list("CRM Partner")
        self.assertGreaterEqual(len(partners), 1)

        frappe.set_user("Administrator")

    def test_partner_user_permissions(self):
        """Test Partner user permissions"""
        # Create a partner for the test user
        partner = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "User Test Partner",
            "partner_type": "Reseller",
            "partner_tier": "Gold",
            "email": "partner.user@test.com"
        })
        partner.insert()

        # Switch to partner user
        frappe.set_user("partner.user@test.com")

        # Should be able to read their own partner record
        own_partner = frappe.get_doc("CRM Partner", partner.name)
        self.assertEqual(own_partner.email, "partner.user@test.com")

        frappe.set_user("Administrator")

    def tearDown(self):
        """Clean up test users"""
        frappe.set_user("Administrator")
        test_emails = [
            "partner.manager@test.com",
            "partner.user@test.com",
            "crm.user@test.com"
        ]
        for email in test_emails:
            if frappe.db.exists("User", email):
                frappe.delete_doc("User", email, ignore_permissions=True)


class TestPartnerIntegration(unittest.TestCase):
    """Test cases for Partner integration with other modules"""

    def test_partner_lead_integration(self):
        """Test partner integration with leads"""
        # Create partner
        partner = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "Integration Test Partner",
            "partner_type": "Reseller",
            "partner_tier": "Gold",
            "email": "integration@test.com"
        })
        partner.insert()

        # Create lead assigned to partner
        lead = frappe.get_doc({
            "doctype": "CRM Lead",
            "lead_name": "Integration Test Lead",
            "email": "intlead@test.com",
            "partner": partner.name
        })
        lead.insert()

        # Update partner metrics
        partner.reload()
        partner.save()

        # Check that metrics are updated
        self.assertGreaterEqual(partner.lead_conversion_rate, 0)

    def test_partner_deal_integration(self):
        """Test partner integration with deals"""
        # Create partner
        partner = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "Deal Integration Partner",
            "partner_type": "Reseller",
            "partner_tier": "Gold",
            "email": "dealintegration@test.com"
        })
        partner.insert()

        # Create deal for partner
        deal = frappe.get_doc({
            "doctype": "CRM Deal",
            "organization": "Deal Test Org",
            "deal_value": 25000,
            "status": "Won",
            "partner": partner.name,
            "closed_date": today()
        })
        deal.insert()

        # Update partner metrics
        partner.reload()
        partner.save()

        # Check metrics update
        self.assertEqual(partner.total_deals_closed, 1)
        self.assertEqual(partner.total_revenue_generated, 25000)


if __name__ == "__main__":
    unittest.main()