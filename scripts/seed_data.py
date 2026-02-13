"""Comprehensive seed data – 500+ records for demo / testing."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from app.database import SessionLocal, Base, engine
from app.auth.dependencies import hash_password

# Import ALL models so tables get created
from app.modules.properties.models import *
from app.modules.leasing.models import *
from app.modules.billing.models import *
from app.modules.accounting.models import *
from app.modules.maintenance.models import *
from app.modules.crm.models import *
from app.modules.marketing.models import *
from app.modules.compliance.models import *
from app.modules.workflow.models import *
from app.auth.models import *


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Skip if data already exists
        if db.query(Property).count() > 0:
            print("Database already seeded. Use --force to reseed.")
            return

        # ═══════════════════════════════════════
        # 1. Tenant Org
        # ═══════════════════════════════════════
        org = TenantOrg(org_name="Apex Property Management", org_code="APEX", country="US",
                        subscription_plan="Enterprise", is_active=True)
        db.add(org)
        db.flush()

        # ═══════════════════════════════════════
        # 2. Roles + Users
        # ═══════════════════════════════════════
        roles_data = [
            {"id": 1, "role_name": "admin", "description": "Full system access", "is_system": True},
            {"id": 2, "role_name": "manager", "description": "Property manager", "is_system": True},
            {"id": 3, "role_name": "owner", "description": "Property owner portal", "is_system": True},
            {"id": 4, "role_name": "tenant", "description": "Tenant portal", "is_system": True},
            {"id": 5, "role_name": "vendor", "description": "Vendor portal", "is_system": True},
            {"id": 6, "role_name": "accountant", "description": "Finance portal", "is_system": True},
        ]
        for r in roles_data:
            if not db.query(Role).filter(Role.id == r["id"]).first():
                db.add(Role(**r))
        db.flush()

        users = [
            UserAccount(username="admin", email="admin@apex.com", password_hash=hash_password("admin123"),
                        full_name="System Admin", role_id=1, tenant_org_id=org.id, is_active=True),
            UserAccount(username="manager1", email="mgr@apex.com", password_hash=hash_password("manager123"),
                        full_name="Jane Manager", role_id=2, tenant_org_id=org.id, is_active=True),
            UserAccount(username="owner1", email="owner@apex.com", password_hash=hash_password("owner123"),
                        full_name="Bob Owner", role_id=3, tenant_org_id=org.id, is_active=True),
            UserAccount(username="tenant1", email="tenant@apex.com", password_hash=hash_password("tenant123"),
                        full_name="Alice Tenant", role_id=4, tenant_org_id=org.id, is_active=True),
            UserAccount(username="vendor1", email="vendor@apex.com", password_hash=hash_password("vendor123"),
                        full_name="Fix-It Services", role_id=5, tenant_org_id=org.id, is_active=True),
            UserAccount(username="acct1", email="acct@apex.com", password_hash=hash_password("acct123"),
                        full_name="Carol Accountant", role_id=6, tenant_org_id=org.id, is_active=True),
        ]
        for u in users:
            if not db.query(UserAccount).filter(UserAccount.username == u.username).first():
                db.add(u)
        db.flush()

        # ═══════════════════════════════════════
        # 3. Regions
        # ═══════════════════════════════════════
        regions = []
        for name, code in [("Downtown", "DT"), ("Suburbs", "SUB"), ("Business District", "BD"),
                           ("Waterfront", "WF"), ("Industrial Zone", "IZ")]:
            r = Region(region_name=name, region_code=code, city="Metro City", state="CA", country="US")
            db.add(r)
            regions.append(r)
        db.flush()

        # ═══════════════════════════════════════
        # 4. Properties (10)
        # ═══════════════════════════════════════
        properties_data = [
            ("Sunrise Tower", "SR-001", "Commercial", regions[2].id),
            ("Lakeside Apartments", "LK-002", "Residential", regions[3].id),
            ("Metro Mall", "MM-003", "Retail", regions[0].id),
            ("Industrial Park A", "IP-004", "Industrial", regions[4].id),
            ("Green Valley Homes", "GV-005", "Residential", regions[1].id),
            ("Downtown Lofts", "DL-006", "Residential", regions[0].id),
            ("Tech Hub Office", "TH-007", "Commercial", regions[2].id),
            ("Harbor View", "HV-008", "Mixed-Use", regions[3].id),
            ("Parkside Villas", "PV-009", "Residential", regions[1].id),
            ("Central Warehouse", "CW-010", "Industrial", regions[4].id),
        ]
        properties = []
        for i, (name, code, ptype, rid) in enumerate(properties_data):
            p = Property(property_name=name, property_code=code, property_type=ptype,
                         region_id=rid, tenant_org_id=org.id, status="Active",
                         address_line1=f"{100+i*10} Main Street", city="Metro City",
                         state="CA", country="US", zip_code=f"9{1000+i}",
                         total_area_sqft=5000 + i * 2000, year_built=2000 + i)
            db.add(p)
            properties.append(p)
        db.flush()

        # ═══════════════════════════════════════
        # 5. Buildings + Floors + Units (100 units total)
        # ═══════════════════════════════════════
        units = []
        unit_no = 0
        for pi, prop in enumerate(properties):
            for bi in range(2):  # 2 buildings per property
                bldg = Building(property_id=prop.id, building_name=f"Block {chr(65+bi)}",
                                building_code=f"B{pi*2+bi+1}", total_floors=5, total_units=5,
                                tenant_org_id=org.id, status="Active")
                db.add(bldg)
                db.flush()
                for fi in range(5):  # 5 floors per building
                    floor = Floor(building_id=bldg.id, floor_name=f"Floor {fi+1}",
                                  floor_number=fi+1, total_units=1)
                    db.add(floor)
                    db.flush()
                    unit_no += 1
                    u = Unit(property_id=prop.id, building_id=bldg.id, floor_id=floor.id,
                             unit_number=f"U-{unit_no:03d}", unit_type="Apartment" if prop.property_type == "Residential" else "Office",
                             tenant_org_id=org.id, current_status="Vacant",
                             area_sqft=500 + (unit_no % 5) * 200, bedrooms=1 + unit_no % 3,
                             bathrooms=1 + unit_no % 2, market_rent=1000 + unit_no * 50)
                    db.add(u)
                    units.append(u)
        db.flush()

        # ═══════════════════════════════════════
        # 6. Owners (10)
        # ═══════════════════════════════════════
        owners = []
        for i, (fn, ln) in enumerate([("Robert", "Smith"), ("Emily", "Johnson"), ("Michael", "Lee"),
                                       ("Sarah", "Chen"), ("David", "Patel"), ("Linda", "Garcia"),
                                       ("James", "Wilson"), ("Maria", "Rodriguez"), ("John", "Kim"),
                                       ("Karen", "Brown")]):
            o = Owner(first_name=fn, last_name=ln, email=f"{fn.lower()}.{ln.lower()}@email.com",
                      phone=f"555-{1000+i}", owner_type="Individual", tenant_org_id=org.id)
            db.add(o)
            owners.append(o)
        db.flush()

        # ═══════════════════════════════════════
        # 7. Tenants (30)
        # ═══════════════════════════════════════
        tenants = []
        tenant_names = [
            ("Alice", "Martin"), ("Bob", "Taylor"), ("Carol", "Anderson"), ("Dan", "Thomas"),
            ("Eve", "Jackson"), ("Frank", "White"), ("Grace", "Harris"), ("Henry", "Clark"),
            ("Irene", "Lewis"), ("Jack", "Robinson"), ("Kate", "Walker"), ("Leo", "Hall"),
            ("Mia", "Allen"), ("Noah", "Young"), ("Olivia", "King"), ("Paul", "Wright"),
            ("Quinn", "Scott"), ("Rachel", "Green"), ("Sam", "Baker"), ("Tina", "Adams"),
            ("Uma", "Nelson"), ("Vic", "Hill"), ("Wendy", "Moore"), ("Xavier", "López"),
            ("Yara", "Gonzalez"), ("Zach", "Martinez"), ("Amy", "Hernandez"), ("Brian", "Cook"),
            ("Clara", "Rivera"), ("Dennis", "Campbell"),
        ]
        for i, (fn, ln) in enumerate(tenant_names):
            t = Tenant(first_name=fn, last_name=ln, tenant_code=f"T-{i+1:03d}",
                       email=f"{fn.lower()}.{ln.lower()}@tenants.com", phone=f"555-{2000+i}",
                       tenant_org_id=org.id)
            db.add(t)
            tenants.append(t)
        db.flush()

        # ═══════════════════════════════════════
        # 8. Vendors (15)
        # ═══════════════════════════════════════
        vendors = []
        vendor_data = [
            ("Quick Plumbing", "Plumbing"), ("Spark Electric", "Electrical"), ("Cool Air HVAC", "HVAC"),
            ("Green Lawn Care", "Landscaping"), ("Clear View Cleaning", "Cleaning"),
            ("Shield Security", "Security"), ("Smart Paint Pros", "Painting"),
            ("AquaPure Water", "Plumbing"), ("SafeStep Flooring", "Flooring"),
            ("BrightLight Electric", "Electrical"), ("AllFix Handyman", "General"),
            ("TechWire IT", "IT"), ("SkyRoof Solutions", "Roofing"),
            ("GlassWorks Inc", "Glazing"), ("PestAway Services", "Pest Control"),
        ]
        for i, (name, cat) in enumerate(vendor_data):
            v = Vendor(vendor_name=name, vendor_code=f"V-{i+1:03d}", category=cat,
                       email=f"info@{name.lower().replace(' ', '')}.com", phone=f"555-{3000+i}",
                       tenant_org_id=org.id)
            db.add(v)
            vendors.append(v)
        db.flush()

        # ═══════════════════════════════════════
        # 9. Leases (30) — one per tenant, use first 30 units
        # ═══════════════════════════════════════
        leases = []
        today = date.today()
        for i, tenant in enumerate(tenants[:30]):
            unit = units[i]
            start = today - timedelta(days=180 + i * 10)
            end = start + relativedelta(years=1)
            rent = float(unit.market_rent or 1500)
            lease = Lease(
                lease_number=f"LS-{i+1:04d}", tenant_org_id=org.id,
                property_id=unit.property_id, tenant_id=tenant.id,
                start_date=start, end_date=end,
                base_rent_amount=rent, base_rent_currency="USD",
                rent_frequency="Monthly", lease_type="Fixed",
                lease_status="Active"
            )
            db.add(lease)
            db.flush()

            # LeaseUnitLink
            link = LeaseUnitLink(lease_id=lease.id, unit_id=unit.id)
            db.add(link)
            unit.current_status = "Occupied"
            leases.append(lease)

            # Rent schedules (12 months)
            for m in range(12):
                due = start + relativedelta(months=m)
                sched_status = "Paid" if due < today else "Scheduled"
                rs = RentSchedule(lease_id=lease.id, tenant_org_id=org.id,
                                  due_date=due, amount_due=rent, currency="USD", status=sched_status)
                db.add(rs)
        db.flush()

        # ═══════════════════════════════════════
        # 10. Payment Methods
        # ═══════════════════════════════════════
        pm1 = PaymentMethod(method_name="Bank Transfer", method_code="BT", is_active=True,
                            tenant_org_id=org.id)
        pm2 = PaymentMethod(method_name="Credit Card", method_code="CC", is_active=True,
                            tenant_org_id=org.id)
        pm3 = PaymentMethod(method_name="Cash", method_code="CASH", is_active=True,
                            tenant_org_id=org.id)
        db.add_all([pm1, pm2, pm3])
        db.flush()

        # ═══════════════════════════════════════
        # 11. Invoices + Payments (past months)
        # ═══════════════════════════════════════
        for i, lease in enumerate(leases[:20]):
            for m in range(3):  # 3 past invoices
                inv_date = today - timedelta(days=90 - m * 30)
                inv = Invoice(
                    tenant_org_id=org.id, tenant_id=lease.tenant_id,
                    property_id=lease.property_id, lease_id=lease.id,
                    invoice_number=f"INV-{i+1:04d}-{m+1:02d}",
                    invoice_date=inv_date, due_date=inv_date + timedelta(days=15),
                    total_amount=float(lease.base_rent_amount),
                    currency="USD", invoice_status="Paid" if m < 2 else "Posted"
                )
                db.add(inv)
                db.flush()

                il = InvoiceLine(invoice_id=inv.id, description=f"Rent – Month {m+1}",
                                 quantity=1, unit_price=float(lease.base_rent_amount),
                                 line_total=float(lease.base_rent_amount))
                db.add(il)

                if m < 2:  # First 2 months paid
                    pmt = Payment(tenant_org_id=org.id, tenant_id=lease.tenant_id,
                                  amount=float(lease.base_rent_amount), currency="USD",
                                  payment_date=inv_date + timedelta(days=5),
                                  payment_method_id=pm1.id, status="Completed")
                    db.add(pmt)
                    db.flush()
                    alloc = PaymentAllocation(payment_id=pmt.id, invoice_id=inv.id,
                                             allocated_amount=float(lease.base_rent_amount),
                                             currency="USD")
                    db.add(alloc)
        db.flush()

        # ═══════════════════════════════════════
        # 12. Late Fee Rule
        # ═══════════════════════════════════════
        lfr = LateFeeRule(rule_name="Standard Late Fee", tenant_org_id=org.id,
                          fee_type="Flat", flat_fee=50, grace_period_days=5,
                          max_fee=200, is_active=True)
        db.add(lfr)

        # ═══════════════════════════════════════
        # 13. Maintenance Requests (20) + Work Orders (10)
        # ═══════════════════════════════════════
        categories = ["Plumbing", "Electrical", "HVAC", "General", "Appliance"]
        priorities = ["Low", "Medium", "High", "Critical"]
        statuses = ["Open", "InProgress", "Completed", "Pending"]
        for i in range(20):
            mr = MaintenanceRequest(
                tenant_org_id=org.id, property_id=properties[i % 10].id,
                unit_id=units[i].id, tenant_id=tenants[i % 30].id,
                category=categories[i % 5], priority=priorities[i % 4],
                title=f"Maintenance Issue #{i+1}",
                description=f"Sample maintenance request for unit {units[i].unit_number}",
                status=statuses[i % 4],
                reported_date=today - timedelta(days=i * 3)
            )
            db.add(mr)
            db.flush()

            if i < 10:  # Work orders for first 10
                wo = WorkOrder(
                    request_id=mr.id, tenant_org_id=org.id,
                    assigned_vendor_id=vendors[i % 15].id,
                    status="Open" if i % 2 == 0 else "Completed",
                    estimated_cost=150 + i * 25
                )
                db.add(wo)
        db.flush()

        # ═══════════════════════════════════════
        # 14. Chart of Accounts (20)
        # ═══════════════════════════════════════
        accounts_data = [
            ("1000", "Cash and Equivalents", "Asset"),
            ("1100", "Accounts Receivable", "Asset"),
            ("1200", "Prepaid Expenses", "Asset"),
            ("1500", "Property & Equipment", "Asset"),
            ("1600", "Accumulated Depreciation", "Asset"),
            ("2000", "Accounts Payable", "Liability"),
            ("2100", "Accrued Liabilities", "Liability"),
            ("2200", "Security Deposits Held", "Liability"),
            ("2500", "Mortgage Payable", "Liability"),
            ("3000", "Owner's Equity", "Equity"),
            ("3100", "Retained Earnings", "Equity"),
            ("4000", "Rental Revenue", "Revenue"),
            ("4100", "Late Fee Revenue", "Revenue"),
            ("4200", "Other Revenue", "Revenue"),
            ("5000", "Property Maintenance", "Expense"),
            ("5100", "Utilities", "Expense"),
            ("5200", "Insurance", "Expense"),
            ("5300", "Property Tax", "Expense"),
            ("5400", "Management Fees", "Expense"),
            ("5500", "Administrative Expenses", "Expense"),
        ]
        coa_map = {}
        for code, name, atype in accounts_data:
            a = ChartOfAccount(account_code=code, account_name=name, account_type=atype,
                               tenant_org_id=org.id, status="Active")
            db.add(a)
            coa_map[code] = a
        db.flush()

        # ═══════════════════════════════════════
        # 15. Journal Entries (10)
        # ═══════════════════════════════════════
        for i in range(10):
            je_date = today - timedelta(days=30 * (10 - i))
            je = JournalEntry(entry_date=je_date, reference=f"JE-{i+1:04d}",
                              description=f"Monthly rent entry #{i+1}",
                              tenant_org_id=org.id, total_debit=5000 + i * 100,
                              total_credit=5000 + i * 100)
            db.add(je)
            db.flush()
            # Debit: Cash, Credit: Rental Revenue
            db.add(JournalEntryLine(journal_entry_id=je.id, account_id=coa_map["1000"].id,
                                    debit_amount=5000 + i * 100, credit_amount=0))
            db.add(JournalEntryLine(journal_entry_id=je.id, account_id=coa_map["4000"].id,
                                    debit_amount=0, credit_amount=5000 + i * 100))
        db.flush()

        # ═══════════════════════════════════════
        # 16. CRM: Contacts + Threads
        # ═══════════════════════════════════════
        from app.modules.crm.models import Contact, CommunicationThread, CRMTask
        for i in range(10):
            c = Contact(first_name=f"Contact{i+1}", last_name=f"Person{i+1}",
                        email=f"contact{i+1}@email.com", contact_type="Prospect",
                        tenant_org_id=org.id)
            db.add(c)
            db.flush()
            t = CommunicationThread(contact_id=c.id, subject=f"Inquiry #{i+1}",
                                    channel="Email", status="Open", tenant_org_id=org.id)
            db.add(t)
        db.flush()

        # ═══════════════════════════════════════
        # 17. Marketing: Listings + Leads
        # ═══════════════════════════════════════
        for i in range(10):
            unit = units[50 + i]  # Vacant units
            ls = Listing(unit_id=unit.id, property_id=unit.property_id,
                         listing_title=f"Beautiful {unit.unit_type} – {unit.unit_number}",
                         listing_description="Spacious, modern, great location.",
                         rent_from=float(unit.market_rent or 1500) * 0.9,
                         rent_to=float(unit.market_rent or 1500),
                         status="Active", is_published=True, tenant_org_id=org.id)
            db.add(ls)
        db.flush()

        for i in range(15):
            lead = Lead(first_name=f"Lead{i+1}", last_name=f"Prospect{i+1}",
                        email=f"lead{i+1}@email.com", phone=f"555-{5000+i}",
                        lead_status="New" if i < 5 else "Qualified" if i < 10 else "Contacted",
                        tenant_org_id=org.id)
            db.add(lead)
        db.flush()

        # ═══════════════════════════════════════
        # 18. Compliance
        # ═══════════════════════════════════════
        from app.modules.compliance.models import (
            DocumentType, ComplianceRequirement, ComplianceItem, Inspection
        )
        dt1 = DocumentType(type_name="Fire Safety Certificate", category="Safety", is_required=True)
        dt2 = DocumentType(type_name="Insurance Policy", category="Insurance", is_required=True)
        dt3 = DocumentType(type_name="Elevator Inspection", category="Safety", is_required=True)
        db.add_all([dt1, dt2, dt3])
        db.flush()

        for i, prop in enumerate(properties[:5]):
            cr = ComplianceRequirement(requirement_name=f"Annual Fire Inspection – {prop.property_name}",
                                       entity_type="Property", document_type_id=dt1.id,
                                       frequency="Annual", tenant_org_id=org.id)
            db.add(cr)
            insp = Inspection(property_id=prop.id, inspection_type="Fire Safety",
                              scheduled_date=today + timedelta(days=30 + i * 15),
                              status="Scheduled", tenant_org_id=org.id)
            db.add(insp)
        db.flush()

        # ═══════════════════════════════════════
        # 19. SLA Rules
        # ═══════════════════════════════════════
        for prio, resp, res in [("Critical", 2, 24), ("High", 4, 48), ("Medium", 8, 72), ("Low", 24, 168)]:
            sla = MaintenanceSLA(sla_name=f"{prio} SLA", priority=prio,
                                 response_hours=resp, resolution_hours=res,
                                 tenant_org_id=org.id, is_active=True)
            db.add(sla)
        db.flush()

        db.commit()
        total = sum([
            db.query(Property).count(), db.query(Building).count(), db.query(Unit).count(),
            db.query(Owner).count(), db.query(Tenant).count(), db.query(Vendor).count(),
            db.query(Lease).count(), db.query(Invoice).count(), db.query(Payment).count(),
            db.query(MaintenanceRequest).count(), db.query(ChartOfAccount).count(),
        ])
        print(f"✅ Seed complete! {total}+ records created across all modules.")
        print(f"   Login: admin / admin123")
    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    if "--force" in sys.argv:
        # Drop and recreate
        Base.metadata.drop_all(bind=engine)
        print("Dropped all tables. Re-seeding...")
    seed()
