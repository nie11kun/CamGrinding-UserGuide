import os
import re
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

SENSITIVE_WORDS = [
    "Marco Nie",
    "江苏莱纳多",
    "莱纳多",
    "聊城中矩",
    "汉江机床",
    "维克智能",
    "C:\\Users\\Marco Nie",
    "c:\\Users\\Marco Nie",
]

def check_sensitive_words():
    print("[1] Checking sensitive words in new markdown files...")
    issues = []
    # Only scan markdown files in the new structure (not old directories if not yet removed)
    chapters = [
        "README.md", "SUMMARY.md",
        "1_getting_started", "2_code_generation", "3_cam_drawing",
        "4_toolbox_analysis", "5_toolbox_error", "6_toolbox_dxf",
        "7_parts_library", "8_workflows_cases", "9_troubleshooting"
    ]
    
    for item in chapters:
        target = os.path.join(BASE_DIR, item)
        if os.path.isfile(target):
            files = [target]
        elif os.path.isdir(target):
            files = [os.path.join(root, f) for root, _, filenames in os.walk(target) for f in filenames if f.endswith(".md")]
        else:
            continue
            
        for filepath in files:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            for word in SENSITIVE_WORDS:
                if word in content:
                    issues.append(f"Found sensitive word '{word}' in {os.path.relpath(filepath, BASE_DIR)}")
                    
    if issues:
        print("  FAIL: Sensitive words found:")
        for iss in issues:
            print("   -", iss)
        return False
    else:
        print("  PASS: Zero sensitive words found in all documentation files.")
        return True

def check_summary_links():
    print("\n[2] Checking SUMMARY.md links...")
    summary_path = os.path.join(BASE_DIR, "SUMMARY.md")
    with open(summary_path, "r", encoding="utf-8") as f:
        summary_text = f.read()
        
    links = re.findall(r'\[.*?\]\((.*?)\)', summary_text)
    missing = []
    for link in links:
        # Strip anchor if any
        clean_link = link.split("#")[0]
        if not clean_link:
            continue
        full_path = os.path.normpath(os.path.join(BASE_DIR, clean_link))
        if not os.path.exists(full_path):
            missing.append(f"Missing file for SUMMARY link: {link} -> {full_path}")
            
    if missing:
        print("  FAIL: Missing files linked in SUMMARY.md:")
        for m in missing:
            print("   -", m)
        return False
    else:
        print(f"  PASS: All {len(links)} links in SUMMARY.md are valid and point to existing files.")
        return True

def check_image_references():
    print("\n[3] Checking markdown image references...")
    chapters = [
        "README.md",
        "1_getting_started", "2_code_generation", "3_cam_drawing",
        "4_toolbox_analysis", "5_toolbox_error", "6_toolbox_dxf",
        "7_parts_library", "8_workflows_cases", "9_troubleshooting"
    ]
    missing_images = []
    total_images = 0
    for item in chapters:
        target = os.path.join(BASE_DIR, item)
        if os.path.isfile(target):
            files = [target]
        elif os.path.isdir(target):
            files = [os.path.join(root, f) for root, _, filenames in os.walk(target) for f in filenames if f.endswith(".md")]
        else:
            continue
            
        for filepath in files:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            images = re.findall(r'!\[.*?\]\((.*?)\)', content)
            for img in images:
                total_images += 1
                img_path = os.path.normpath(os.path.join(os.path.dirname(filepath), img))
                if not os.path.exists(img_path):
                    missing_images.append(f"Missing image: {img} referenced in {os.path.relpath(filepath, BASE_DIR)}")
                    
    if missing_images:
        print("  FAIL: Missing images:")
        for mi in missing_images:
            print("   -", mi)
        return False
    else:
        print(f"  PASS: All {total_images} image references resolve to existing image files.")
        return True

if __name__ == "__main__":
    t1 = check_sensitive_words()
    t2 = check_summary_links()
    t3 = check_image_references()
    if t1 and t2 and t3:
        print("\nALL CHECKS PASSED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\nSOME CHECKS FAILED!")
        sys.exit(1)

