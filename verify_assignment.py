"""
Quick verification script to ensure all assignment components are functional.
Run this before submitting to verify everything works correctly.
"""

import os
import sys
import json
from pathlib import Path

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_status(check, status, details=""):
    symbol = "✅" if status else "❌"
    print(f"{symbol} {check}")
    if details:
        print(f"   └─ {details}")

def verify_project_structure():
    print_header("1. Verifying Project Structure")
    
    required_files = {
        "bms/ontology.py": "Ontology definition",
        "bms/agents.py": "Agent implementations",
        "bms/model.py": "Mesa model",
        "bms/rules.py": "SWRL rules",
        "bms/messaging.py": "Message bus",
        "bms/run.py": "CLI entrypoint",
        "bms/data/seed_books.json": "Book seed data",
        "requirements.txt": "Python dependencies",
        "README.md": "Project documentation",
        "report/report_template.md": "Report template",
        "report/video_script.md": "Video script",
    }
    
    all_exist = True
    for file, desc in required_files.items():
        exists = os.path.exists(file)
        all_exist &= exists
        print_status(f"{desc} ({file})", exists)
    
    return all_exist

def verify_ontology_classes():
    print_header("2. Verifying Ontology Classes")
    
    try:
        from bms import ontology
        onto = ontology.build_ontology()
        
        required_classes = ["Book", "Customer", "Employee", "Order", "Inventory"]
        all_present = True
        
        for cls_name in required_classes:
            has_class = hasattr(onto, cls_name)
            all_present &= has_class
            print_status(f"Class: {cls_name}", has_class)
        
        return all_present
    except Exception as e:
        print_status("Ontology import", False, str(e))
        return False

def verify_ontology_properties():
    print_header("3. Verifying Ontology Properties")
    
    try:
        from bms import ontology
        onto = ontology.build_ontology()
        
        required_properties = {
            "Object Properties": ["purchases", "worksAt", "hasBook", "orderedBy", "forBook"],
            "Data Properties": ["hasAuthor", "hasGenre", "hasPrice", "availableQuantity", 
                               "thresholdQuantity", "restockAmount", "quantity", "needsRestock"]
        }
        
        all_present = True
        for prop_type, props in required_properties.items():
            print(f"\n{prop_type}:")
            for prop in props:
                has_prop = hasattr(onto, prop)
                all_present &= has_prop
                print_status(f"  {prop}", has_prop)
        
        return all_present
    except Exception as e:
        print_status("Property verification", False, str(e))
        return False

def verify_agents():
    print_header("4. Verifying Agent Classes")
    
    try:
        from bms import agents
        
        required_agents = {
            "CustomerAgent": "Customer browsing and purchasing",
            "EmployeeAgent": "Inventory management and restocking",
            "BookAgent": "Book metadata holder"
        }
        
        all_present = True
        for agent_name, desc in required_agents.items():
            has_agent = hasattr(agents, agent_name)
            all_present &= has_agent
            print_status(f"{agent_name}: {desc}", has_agent)
        
        return all_present
    except Exception as e:
        print_status("Agent import", False, str(e))
        return False

def verify_swrl_rules():
    print_header("5. Verifying SWRL Rules")
    
    try:
        from bms import rules
        
        checks = {
            "attach_rules function": hasattr(rules, "attach_rules"),
            "run_reasoner function": hasattr(rules, "run_reasoner"),
        }
        
        all_present = True
        for check, status in checks.items():
            all_present &= status
            print_status(check, status)
        
        # Try to read the file and check for rule definitions
        rules_file = Path("bms/rules.py")
        if rules_file.exists():
            content = rules_file.read_text()
            has_low_stock_rule = "swrlb:lessThan" in content
            has_purchase_rule = "purchases(?c, ?b)" in content
            
            print_status("Low stock SWRL rule defined", has_low_stock_rule)
            print_status("Purchase audit SWRL rule defined", has_purchase_rule)
            all_present &= has_low_stock_rule and has_purchase_rule
        
        return all_present
    except Exception as e:
        print_status("SWRL rules verification", False, str(e))
        return False

def verify_message_bus():
    print_header("6. Verifying Message Bus")
    
    try:
        from bms.messaging import MessageBus, Message
        
        bus = MessageBus()
        
        # Test publish/drain
        test_msg = Message(topic="test", sender="verifier", payload={"test": True})
        bus.publish("test", test_msg)
        messages = bus.drain("test")
        
        checks = {
            "MessageBus class imported": True,
            "Message class imported": True,
            "Publish functionality": len(messages) == 1,
            "Drain functionality": bus.drain("test") == []
        }
        
        all_passed = True
        for check, status in checks.items():
            all_passed &= status
            print_status(check, status)
        
        return all_passed
    except Exception as e:
        print_status("Message bus verification", False, str(e))
        return False

def verify_model_execution():
    print_header("7. Verifying Model Execution")
    
    try:
        from bms.model import BMSModel
        import os
        
        seed_path = os.path.join("bms", "data", "seed_books.json")
        
        # Create a small test model
        print("Creating test model with 5 customers for 3 steps...")
        model = BMSModel(
            seed_path=seed_path,
            N_customers=5,
            restock_threshold=5,
            restock_amount=10,
            seed=42
        )
        
        # Run 3 steps
        for i in range(3):
            model.step()
            print(f"  Step {i+1} completed")
        
        checks = {
            "Model initialization": True,
            "Model execution (3 steps)": model.current_step == 3,
            "Ontology attached": hasattr(model, "onto"),
            "Agents scheduled": len(list(model.schedule.agents)) > 0,
            "Data collection": model.datacollector is not None
        }
        
        all_passed = True
        for check, status in checks.items():
            all_passed &= status
            print_status(check, status)
        
        print(f"\n  Test Results:")
        print(f"  - Total sales: ${model.total_sales:.2f}")
        print(f"  - Books sold: {model.sold_count}")
        print(f"  - Restocks: {model.restocks}")
        print(f"  - Stockouts: {model.stockouts}")
        
        return all_passed
    except Exception as e:
        print_status("Model execution", False, str(e))
        return False

def verify_outputs():
    print_header("8. Verifying Output Files")
    
    output_files = {
        "report/run_summary.json": "Run summary (from previous execution)",
        "report/figures/metrics.png": "Metrics plot (from previous execution)",
        "report/bookstore.owl": "Ontology snapshot (from previous execution)"
    }
    
    any_exist = False
    for file, desc in output_files.items():
        exists = os.path.exists(file)
        any_exist |= exists
        status_text = "exists" if exists else "not generated yet"
        print_status(f"{desc}", exists, status_text)
    
    if not any_exist:
        print("\n  Note: Run 'python -m bms.run' to generate output files")
    
    return True  # Not critical for verification

def verify_documentation():
    print_header("9. Verifying Documentation")
    
    docs = {
        "README.md": "Main documentation",
        "report/report_template.md": "Report template",
        "report/assignment_summary.md": "Assignment mapping",
        "report/video_script.md": "Video script outline"
    }
    
    all_exist = True
    for file, desc in docs.items():
        exists = os.path.exists(file)
        all_exist &= exists
        print_status(f"{desc}", exists)
    
    return all_exist

def main():
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  BMS ASSIGNMENT VERIFICATION SCRIPT".center(68) + "█")
    print("█" + "  Bookstore Management System - Ontology + MAS".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    results = {}
    
    # Run all verifications
    results["Project Structure"] = verify_project_structure()
    results["Ontology Classes"] = verify_ontology_classes()
    results["Ontology Properties"] = verify_ontology_properties()
    results["Agent Classes"] = verify_agents()
    results["SWRL Rules"] = verify_swrl_rules()
    results["Message Bus"] = verify_message_bus()
    results["Model Execution"] = verify_model_execution()
    results["Output Files"] = verify_outputs()
    results["Documentation"] = verify_documentation()
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    passed = sum(results.values())
    total = len(results)
    
    for check, status in results.items():
        print_status(check, status)
    
    print("\n" + "="*70)
    percentage = (passed / total) * 100
    print(f"  TOTAL: {passed}/{total} checks passed ({percentage:.1f}%)")
    print("="*70 + "\n")
    
    if passed == total:
        print("🎉 ALL CHECKS PASSED! Your implementation is complete and ready.")
        print("\n📝 Next steps:")
        print("   1. Fill the report template: report/report_template.md")
        print("   2. Export report to PDF (≤20 pages)")
        print("   3. Record video demonstration (5-10 minutes)")
        print("   4. Run full simulation: python -m bms.run --steps 40")
        return 0
    else:
        print("⚠️  Some checks failed. Please review the errors above.")
        print("   Fix the issues and run this script again.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ Verification interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
