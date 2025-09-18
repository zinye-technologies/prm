# Copyright (c) 2024, Zinye Technologies and contributors
# For license information, please see license.txt

import unittest
import frappe
from frappe.utils import today
from frappe.test_runner import make_test_records


class TestPartnerAPI(unittest.TestCase):
    """Test cases for Partner API endpoints"""

    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        make_test_records("Country")
        make_test_records("Territory")

    def setUp(self):
        """Set up before each test"""
        # Clean up existing test data
        frappe.db.delete("CRM Partner", {"email": ["like", "%apitest.com"]})
        frappe.db.commit()

    def tearDown(self):
        """Clean up after each test"""
        frappe.db.delete("CRM Partner", {"email": ["like", "%apitest.com"]})
        frappe.db.commit()

    def test_get_partner_list_api(self):
        """Test get_partner_list API function"""
        from prm.api.partner import get_partner_list

        # Create test partners
        for i in range(3):
            partner = frappe.get_doc({
                "doctype": "CRM Partner",
                "partner_name": f"API Test Partner {i+1}",
                "partner_type": "Reseller",
                "partner_tier": "Gold",
                "email": f"api{i+1}@apitest.com",
                "status": "Active"
            })
            partner.insert()

        # Test basic list
        result = get_partner_list()
        self.assertIn("partners", result)
        self.assertIn("total_count", result)
        self.assertIn("has_more", result)
        self.assertGreaterEqual(len(result["partners"]), 3)

        # Test with filters
        result_filtered = get_partner_list(
            filters={"partner_type": "Reseller"}
        )
        for partner in result_filtered["partners"]:
            self.assertEqual(partner["partner_type"], "Reseller")

        # Test with search
        result_search = get_partner_list(search_term="API Test")
        self.assertGreaterEqual(len(result_search["partners"]), 3)

        # Test pagination
        result_page = get_partner_list(limit=2, start=0)
        self.assertLessEqual(len(result_page["partners"]), 2)

    def test_get_partner_details_api(self):
        """Test get_partner_details API function"""
        from prm.api.partner import get_partner_details

        # Create test partner
        partner = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "Details Test Partner",
            "partner_type": "Distributor",
            "partner_tier": "Silver",
            "email": "details@apitest.com",
            "primary_contact": "John Doe",
            "phone": "+1-555-0123"
        })
        partner.insert()

        # Test API
        result = get_partner_details(partner.name)
        self.assertIn("partner", result)
        self.assertIn("performance", result)
        self.assertIn("recent_deals", result)
        self.assertIn("recent_leads", result)

        partner_data = result["partner"]
        self.assertEqual(partner_data["partner_name"], "Details Test Partner")
        self.assertEqual(partner_data["email"], "details@apitest.com")

        # Test with non-existent partner
        with self.assertRaises(frappe.DoesNotExistError):
            get_partner_details("NON_EXISTENT_PARTNER")

    def test_create_partner_api(self):
        """Test create_partner API function"""
        from prm.api.partner import create_partner

        partner_data = {
            "partner_name": "Created Test Partner",
            "partner_type": "Affiliate",
            "partner_tier": "Bronze",
            "email": "created@apitest.com",
            "primary_contact": "Jane Smith",
            "phone": "+1-555-0456",
            "commission_rate": 12.5
        }

        # Test successful creation
        result = create_partner(partner_data)
        self.assertTrue(result["success"])
        self.assertIn("partner", result)
        self.assertIn("message", result)

        created_partner = result["partner"]
        self.assertEqual(created_partner["partner_name"], "Created Test Partner")
        self.assertEqual(created_partner["partner_type"], "Affiliate")

        # Verify in database
        db_partner = frappe.get_doc("CRM Partner", created_partner["name"])
        self.assertEqual(db_partner.email, "created@apitest.com")

        # Test validation errors
        invalid_data = {
            "partner_name": "",  # Missing required field
            "partner_type": "Reseller",
            "partner_tier": "Gold",
            "email": "invalid@apitest.com"
        }

        with self.assertRaises(frappe.ValidationError):
            create_partner(invalid_data)

        # Test duplicate email
        duplicate_data = {
            "partner_name": "Duplicate Partner",
            "partner_type": "Reseller",
            "partner_tier": "Gold",
            "email": "created@apitest.com"  # Same email as above
        }

        with self.assertRaises(frappe.ValidationError):
            create_partner(duplicate_data)

    def test_update_partner_api(self):
        """Test update_partner API function"""
        from prm.api.partner import update_partner

        # Create test partner
        partner = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "Update Test Partner",
            "partner_type": "Reseller",
            "partner_tier": "Gold",
            "email": "update@apitest.com"
        })
        partner.insert()

        # Test update
        update_data = {
            "partner_tier": "Platinum",
            "commission_rate": 20.0,
            "primary_contact": "Updated Contact"
        }

        result = update_partner(partner.name, update_data)
        self.assertTrue(result["success"])
        self.assertIn("partner", result)

        # Verify update
        updated_partner = frappe.get_doc("CRM Partner", partner.name)
        self.assertEqual(updated_partner.partner_tier, "Platinum")
        self.assertEqual(updated_partner.commission_rate, 20.0)
        self.assertEqual(updated_partner.primary_contact, "Updated Contact")

        # Test update non-existent partner
        with self.assertRaises(frappe.DoesNotExistError):
            update_partner("NON_EXISTENT", {"partner_tier": "Silver"})

    def test_assign_lead_to_partner_api(self):
        """Test assign_lead_to_partner API function"""
        from prm.api.partner import assign_lead_to_partner

        # Create test partner
        partner = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "Lead Assignment Partner",
            "partner_type": "Reseller",
            "partner_tier": "Gold",
            "email": "leadassign@apitest.com",
            "status": "Active"
        })
        partner.insert()

        # Create test lead
        lead = frappe.get_doc({
            "doctype": "CRM Lead",
            "lead_name": "Assignment Test Lead",
            "email": "testlead@apitest.com"
        })
        lead.insert()

        # Test assignment
        result = assign_lead_to_partner(
            lead.name,
            partner.name,
            "API test assignment"
        )

        self.assertTrue(result["success"])
        self.assertIn("message", result)
        self.assertIn("lead", result)

        # Verify assignment
        updated_lead = frappe.get_doc("CRM Lead", lead.name)
        self.assertEqual(updated_lead.partner, partner.name)

        # Test assignment to inactive partner
        inactive_partner = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "Inactive Partner",
            "partner_type": "Reseller",
            "partner_tier": "Gold",
            "email": "inactive@apitest.com",
            "status": "Inactive"
        })
        inactive_partner.insert()

        lead2 = frappe.get_doc({
            "doctype": "CRM Lead",
            "lead_name": "Test Lead 2",
            "email": "testlead2@apitest.com"
        })
        lead2.insert()

        with self.assertRaises(frappe.ValidationError):
            assign_lead_to_partner(lead2.name, inactive_partner.name)

    def test_search_partners_api(self):
        """Test search_partners API function"""
        from prm.api.partner import search_partners

        # Create test partners
        partners_data = [
            {
                "partner_name": "Alpha Search Partner",
                "partner_type": "Reseller",
                "partner_tier": "Gold",
                "email": "alpha@apitest.com",
                "territory": "North America"
            },
            {
                "partner_name": "Beta Search Partner",
                "partner_type": "Distributor",
                "partner_tier": "Silver",
                "email": "beta@apitest.com",
                "territory": "Europe"
            },
            {
                "partner_name": "Gamma Technologies",
                "partner_type": "Technology Partner",
                "partner_tier": "Gold",
                "email": "gamma@apitest.com",
                "territory": "Asia"
            }
        ]

        for data in partners_data:
            partner = frappe.get_doc({
                "doctype": "CRM Partner",
                **data
            })
            partner.insert()

        # Test search by name
        results = search_partners("Alpha")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["partner_name"], "Alpha Search Partner")

        # Test search by partial name
        results = search_partners("Search")
        self.assertGreaterEqual(len(results), 2)

        # Test search with partner type filter
        results = search_partners("Partner", partner_type="Reseller")
        reseller_results = [r for r in results if r["partner_type"] == "Reseller"]
        self.assertGreaterEqual(len(reseller_results), 1)

        # Test search with territory filter
        results = search_partners("", territory="North America")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["territory"], "North America")

        # Test search by email
        results = search_partners("gamma@apitest.com")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["email"], "gamma@apitest.com")

    def test_partner_dashboard_stats_api(self):
        """Test partner_dashboard_stats API function"""
        from prm.api.partner import partner_dashboard_stats

        # Create test partners with different statuses
        statuses = ["Active", "Pending Approval", "Inactive"]
        for i, status in enumerate(statuses):
            partner = frappe.get_doc({
                "doctype": "CRM Partner",
                "partner_name": f"Stats Partner {i+1}",
                "partner_type": "Reseller",
                "partner_tier": "Gold",
                "email": f"stats{i+1}@apitest.com",
                "status": status
            })
            partner.insert()

        # Test stats API
        stats = partner_dashboard_stats()
        self.assertIn("partners_by_status", stats)
        self.assertIn("top_partners_this_month", stats)
        self.assertIn("onboarding_status", stats)

        # Check partners by status
        status_counts = {item["status"]: item["count"] for item in stats["partners_by_status"]}
        self.assertGreaterEqual(status_counts.get("Active", 0), 1)
        self.assertGreaterEqual(status_counts.get("Pending Approval", 0), 1)

    def test_calculate_partner_commission_api(self):
        """Test calculate_partner_commission API function"""
        from prm.api.partner import calculate_partner_commission

        # Create partner with commission rate
        partner = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "Commission Test Partner",
            "partner_type": "Reseller",
            "partner_tier": "Gold",
            "email": "commission@apitest.com",
            "commission_rate": 15.0
        })
        partner.insert()

        # Test commission calculation
        commission = calculate_partner_commission(partner.name, 10000)
        self.assertEqual(commission, 1500.0)

        # Test with zero deal value
        commission_zero = calculate_partner_commission(partner.name, 0)
        self.assertEqual(commission_zero, 0)

        # Test partner without commission rate
        partner_no_rate = frappe.get_doc({
            "doctype": "CRM Partner",
            "partner_name": "No Rate Partner",
            "partner_type": "Reseller",
            "partner_tier": "Gold",
            "email": "norate@apitest.com"
        })
        partner_no_rate.insert()

        commission_no_rate = calculate_partner_commission(partner_no_rate.name, 10000)
        self.assertEqual(commission_no_rate, 0)


if __name__ == "__main__":
    unittest.main()