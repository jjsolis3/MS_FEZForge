"""
ProBuildIQ Easy Runner - Interactive Menu
===========================================

Just double-click this file (or run: python easy_runner.py)
No parameters needed - it will ask you what to do!

This is the EASIEST way to use the tools.
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter  import filedialog

# Add current directory to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def pick_file_dialog(title, filetypes, initialdir=None):
    """Open a Windows file picker and return the selected file path or None."""
    root = tk.Tk()
    root.withdraw()  # hide the root window

    path = filedialog.askopenfilename(
        title=title,
        initialdir=initialdir or os.getcwd(),
        filetypes=filetypes,
    )

    root.destroy()
    return path or None


def pick_folder_dialog(title, initialdir=None):
    """Open a Windows folder picker and return the selected folder path or None."""
    root = tk.Tk()
    root.withdraw()

    folder = filedialog.askdirectory(
        title=title,
        initialdir=initialdir or os.getcwd(),
    )

    root.destroy()
    return folder or None

def load_config():
    """Load configuration from config.json"""
    config_path = Path("config.json")
    
    if not config_path.exists():
        print("Creating config.json template...")
        create_config_template()
        print("Please edit config.json with your credentials and run again.")
        return None
    
    with open(config_path) as f:
        return json.load(f)
    
def create_config_template():
    """Create a template configuration file"""
    template = {
        "api": {
            "api_key": "your_api_key_from_measuresquare",
            "x_application": "get_from_measuresquare_support",
            "secret_key": "get_from_measuresquare_support",
            "m2_id": "your.email@company.com"
        },
        "local": {
            "fez_file_path": "/path/to/your/project.fez"
        },
        "output": {
            "images_dir": "./output/images",
            "reports_dir": "./output/reports",
            "json_export": "./output/project_data.json"
        }
    }
    
    with open("config.json", 'w') as f:
        json.dump(template, f, indent=2)

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """Print the program header"""
    print("=" * 70)
    print("  ProBuildIQ MeasureSquare Tools - Easy Runner")
    print("=" * 70)
    print()


def get_file_path(prompt="Enter FEZ file path: "):
    """
    Get file path from user with helpful hints
    
    Why this helps: Users can drag-and-drop files into the console!
    """
    print(prompt)
    print("  (Tip: You can drag and drop the file into this window)")
    print("  Or paste the full path like: G:\\Folder\\file.fez")
    print()
    
    path = input("  Path: ").strip()
    
    # Remove quotes if user copied path with quotes
    path = path.strip('"').strip("'")
    
    # Check if file exists
    if not Path(path).exists():
        print(f"\n  ❌ File not found: {path}")
        print("  Please check the path and try again.")
        input("\n  Press Enter to continue...")
        return None
    
    return path

def generate_pdf_from_fez():
    """Option 1: Generate PDF from local FEZ file"""
    clear_screen()
    print_header()
    print("📄 GENERATE PDF FROM LOCAL FEZ FILE")
    print("-" * 70)
    print()
    
    # Use Windows file dialog to pick FEZ file
    print("A file browser window will open to select your FEZ file.")
    fez_path = pick_file_dialog(
        title="Select FEZ file",
        filetypes=[("FEZ Files", "*.fez"), ("All files", "*.*")],
    )

    if not fez_path:
        print("\n⚠️ No file selected. Cancelling.")
        input("\nPress Enter to continue...")
        return
    
    # Get output path
    print("\nWhere should I save the PDF?")
    print("  (Press Enter to save in same folder as FEZ file)")
    print("  Or enter a folder path, or full path with filename")
    output = input("  PDF path: ").strip().strip('"').strip("'")
    
    if not output:
        # Save in same location as FEZ
        output = str(Path(fez_path).with_suffix('.pdf'))
    else:
        # Check if user provided a folder instead of a file
        output_path = Path(output)
        if output_path.exists() and output_path.is_dir():
            # User gave us a folder - add filename automatically
            fez_name = Path(fez_path).stem
            output = str(output_path / f"{fez_name}.pdf")
            print(f"  → Saving as: {Path(output).name}")
        elif not output.lower().endswith('.pdf'):
            # User didn't include .pdf extension
            output = output + '.pdf'
    
    # Ask about sections to include
    print("\nWhat should be included in the PDF?")
    print("  1. Everything (summary, rooms, products, estimation)")
    print("  2. Installer view (summary, rooms, estimation only)")
    print("  3. Client view (summary and rooms only)")
    print("  4. Custom (choose sections)")
    
    choice = input("\n  Choose (1-4): ").strip()
    
    if choice == '1':
        sections = ['summary', 'rooms', 'products', 'estimation']
    elif choice == '2':
        sections = ['summary', 'rooms', 'estimation']
    elif choice == '3':
        sections = ['summary', 'rooms']
    elif choice == '4':
        sections = []
        print("\n  Include summary? (y/n): ", end='')
        if input().lower().startswith('y'):
            sections.append('summary')
        print("  Include rooms? (y/n): ", end='')
        if input().lower().startswith('y'):
            sections.append('rooms')
        print("  Include products? (y/n): ", end='')
        if input().lower().startswith('y'):
            sections.append('products')
        print("  Include estimation? (y/n): ", end='')
        if input().lower().startswith('y'):
            sections.append('estimation')
    else:
        sections = ['summary', 'rooms', 'products', 'estimation']
    
    # Generate PDF
    print(f"\n⏳ Generating PDF...")
    print(f"   Input: {Path(fez_path).name}")
    print(f"   Output: {Path(output).name}")
    print(f"   Sections: {', '.join(sections)}")
    print()
    
    try:
        from probuildiq_reportlab_generator import ProBuildIQPDFGenerator
        
        with ProBuildIQPDFGenerator(fez_path) as generator:
            generator.generate_pdf(output, include_sections=sections)
        
        print(f"\n✅ SUCCESS!")
        print(f"   PDF saved: {output}")
        
        # Ask if they want to open it
        print("\nWould you like to open the PDF now? (y/n): ", end='')
        if input().lower().startswith('y'):
            os.startfile(output)  # Windows only
        
    except ImportError:
        print("\n❌ ERROR: ReportLab not installed!")
        print("   Please run: pip install reportlab")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to continue...")

def edit_fez_file():
    """Option 2: Edit FEZ file (rename rooms, update products)"""
    clear_screen()
    print_header()
    print("✏️  EDIT FEZ FILE")
    print("-" * 70)
    print()
    
    # Get FEZ file via dialog
    print("A file browser window will open to select your FEZ file.")
    fez_path = pick_file_dialog(
        title="Select FEZ file to edit",
        filetypes=[("FEZ Files", "*.fez"), ("All files", "*.*")],
    )
    if not fez_path:
        print("\n⚠️ No file selected. Cancelling.")
        input("\nPress Enter to continue...")
        return
    
    print("\nWhat would you like to edit?")
    print("  1. Rename rooms (interactive)")
    print("  2. Use standard name cleanup")
    print("  3. Update product information")
    
    choice = input("\nChoose (1-3): ").strip()
    
    try:
        from probuildiq_fez_editor import FEZFileEditor
        
        with FEZFileEditor(fez_path) as editor:
            
            if choice == '1':
                # Interactive room renaming
                rooms = editor.get_all_room_names()
                print(f"\nFound {len(rooms)} rooms:")
                for i, room in enumerate(rooms, 1):
                    print(f"  {i}. {room['name']}")
                
                print("\nEnter new names (or press Enter to skip):")
                for room in rooms:
                    print(f"\n  Current: {room['name']}")
                    new_name = input("  New name: ").strip()
                    if new_name:
                        editor.rename_room(room['name'], new_name)
            
            elif choice == '2':
                # Standard cleanup
                print("\n⏳ Applying standard name cleanup...")
                name_mapping = {
                    'Primary Bdrm': 'Master Bedroom',
                    'MBR CL': 'Master Bedroom Closet',
                    'LR CL': 'Living Room Closet',
                    'Master Vanity': 'Master Bathroom Vanity',
                    'LR': 'Living Room',
                    'DR': 'Dining Room',
                }
                count = editor.batch_rename_rooms(name_mapping)
                print(f"   Renamed {count} rooms")
            
            elif choice == '3':
                # Product update
                products = editor.parser.get_products()
                print(f"\nFound {len(products)} products:")
                for i, prod in enumerate(products, 1):
                    print(f"  {i}. {prod['name']} (ID: {prod['id']})")
                
                print("\nWhich product to update? (number): ", end='')
                try:
                    prod_num = int(input().strip()) - 1
                    if 0 <= prod_num < len(products):
                        product = products[prod_num]
                        print(f"\nUpdating: {product['name']}")
                        print("  New vendor (Enter to skip): ", end='')
                        vendor = input().strip()
                        print("  New sales price (Enter to skip): ", end='')
                        price = input().strip()
                        
                        updates = {}
                        if vendor:
                            updates['vendor'] = vendor
                        if price:
                            updates['salesPrice'] = price
                        
                        if updates:
                            editor.update_product_info(product['id'], updates)
                            print("  ✓ Product updated")
                except ValueError:
                    print("  Invalid selection")
            
            # Save changes
            if editor.modified:
                print("\n💾 Saving changes...")
                output_path = editor.save()
                print(f"   ✅ Saved: {output_path}")
            else:
                print("\n  No changes made.")
        
    except ImportError as e:
        print(f"\n❌ ERROR: Missing module - {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to continue...")


def upload_to_cloud_and_extract(config):
    """Option 3: Upload local FEZ to cloud and get high-quality PDF"""
    clear_screen()
    print_header()
    print("☁️  UPLOAD TO CLOUD & GET HIGH-QUALITY PDF")
    print("-" * 70)
    print()
    print("This uploads your local FEZ file to MeasureSquare Cloud")
    print("and generates a perfect, cloud-rendered PDF!")
    print()
    
    # Get API credentials from config
    print("Using credentials from config.json")
    api_key = config['api']['api_key']
    m2_id = config['api']['m2_id']
    
    if not api_key or not m2_id:
        print("\n❌ API key and M2 ID are required")
        input("\nPress Enter to continue...")
        return
    
    # Get FEZ file
    print("\nA file browser window will open to select the FEZ file to upload.")
    fez_path = pick_file_dialog(
        title="Select FEZ file to upload to cloud",
        filetypes=[("FEZ Files", "*.fez"), ("All files", "*.*")],
    )
    if not fez_path:
        print("\n⚠️ No file selected. Cancelling.")
        input("\nPress Enter to continue...")
        return

    
    # Get output directory
    print("\nWhere to save the cloud PDF?")
    print("  (Press Enter for ./cloud_pdfs)")
    output_dir = input("  Output folder: ").strip() or "./cloud_pdfs"
    
    print(f"\n⏳ Starting cloud workflow...")
    print(f"   This will:")
    print(f"   1. Upload {Path(fez_path).name} to cloud")
    print(f"   2. Wait for cloud processing")
    print(f"   3. Download high-quality PDF")
    print(f"   4. Download layer images")
    print()
    
    try:
        from cloud_api_complete_workflow import CloudAPIWorkflow
        
        workflow = CloudAPIWorkflow(api_key=api_key, m2_id=m2_id)
        
        result = workflow.upload_and_extract_workflow(
            fez_path,
            output_dir=output_dir
        )
        
        print(f"\n✅ SUCCESS!")
        print(f"   Project ID: {result['project_id']}")
        print(f"   PDF: {result['pdf_path']}")
        print(f"   Images: {result['images_dir']}")
        
        # Ask if they want to open
        print("\nWould you like to open the PDF now? (y/n): ", end='')
        if input().lower().startswith('y'):
            import os
            os.startfile(result['pdf_path'])
        
    except ImportError:
        print("\n❌ ERROR: cloud_api_complete_workflow.py not found!")
        print("   Make sure all files are in the same folder")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to continue...")

def get_all_cloud_projects(config):
    """Option 4: Get all cloud projects (handles 400+)"""
    clear_screen()
    print_header()
    print("📊 GET ALL CLOUD PROJECTS")
    print("-" * 70)
    print()
    print("This will fetch ALL your cloud projects")
    print("(handles pagination automatically for 400+ projects)")
    print()
    
    # Get credentials from config
    print("Using credentials from config.json")
    api_key = config['api']['api_key']
    m2_id = config['api']['m2_id']
    
    if not api_key or not m2_id:
        print("\n❌ Credentials required")
        input("\nPress Enter to continue...")
        return
    
    print("\n⏳ Fetching all projects...")
    
    try:
        from cloud_api_complete_workflow import CloudAPIWorkflow
        
        workflow = CloudAPIWorkflow(api_key=api_key, m2_id=m2_id)
        all_projects = workflow.get_all_projects()
        
        print(f"\n✅ Found {len(all_projects)} projects!")
        print("\nFirst 10 projects:")
        for i, proj in enumerate(all_projects[:10], 1):
            print(f"  {i}. {proj['Name']} (ID: {proj['ProjectId']})")
        
        if len(all_projects) > 10:
            print(f"  ... and {len(all_projects) - 10} more")
        
        # Option to save list
        print("\nSave project list to file? (y/n): ", end='')
        if input().lower().startswith('y'):
            import json
            with open("all_projects.json", 'w') as f:
                json.dump(all_projects, f, indent=2)
            print("  ✓ Saved to: all_projects.json")
        
    except ImportError:
        print("\n❌ ERROR: Required module not found")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
    
    input("\nPress Enter to continue...")


def filter_cloud_projects(config):
    """Option 5: Filter and extract specific cloud projects with PDF filtering"""
    clear_screen()
    print_header()
    print("🔍 FILTER & EXTRACT SPECIFIC PROJECTS (WITH PDF FILTERING)")
    print("-" * 70)
    print()
    
    # Get credentials from config
    print("Using credentials from config.json")
    api_key = config['api']['api_key']
    m2_id = config['api']['m2_id']
    
    if not api_key or not m2_id:
        print("\n❌ Credentials required")
        input("\nPress Enter to continue...")
        return
    
    # Get filter criteria
    print("\nProject Filter (press Enter to skip any):")
    name_filter = input("  Project name contains: ").strip() or None
    date_filter = input("  Created after (YYYY-MM-DD): ").strip() or None
    customer_filter = input("  Customer name contains: ").strip() or None
    
    # PDF FILTERING OPTIONS (NEW!)
    print("\n" + "="*70)
    print("PDF PAGE FILTERING OPTIONS")
    print("="*70)
    print("\nWould you like to remove unwanted pages from the PDFs?")
    print("(Like blank 3D rendering pages)")
    print()
    print("  1. No filtering - keep all pages")
    print("  2. Auto-remove blank pages (recommended)")
    print("  3. Remove specific page numbers")
    print("  4. Custom filtering (advanced)")
    print()
    
    filter_choice = input("Choose PDF filtering (1-4, default=2): ").strip() or '2'
    
    pdf_filter_options = None
    
    if filter_choice == '1':
        pdf_filter_options = None  # No filtering
        print("   ✓ No filtering - all pages will be kept")
        
    elif filter_choice == '2':
        pdf_filter_options = {'blank_pages': True}
        print("   ✓ Will auto-remove blank pages (3D rendering pages)")
        
    elif filter_choice == '3':
        print("\nEnter page numbers to remove (comma-separated)")
        print("Example: 4,8,10")
        pages_input = input("  Pages to remove: ").strip()
        
        if pages_input:
            try:
                page_numbers = [int(p.strip()) for p in pages_input.split(',')]
                pdf_filter_options = {'page_numbers': page_numbers}
                print(f"   ✓ Will remove pages: {page_numbers}")
            except ValueError:
                print("   ⚠️ Invalid input, no page filtering will be applied")
                pdf_filter_options = None
        else:
            pdf_filter_options = None
            
    elif filter_choice == '4':
        print("\nCustom filtering options:")
        
        remove_blank = input("  Remove blank pages? (y/n, default=y): ").strip().lower()
        remove_blank = remove_blank != 'n'
        
        pages_input = input("  Specific pages to remove (comma-separated, optional): ").strip()
        page_numbers = None
        if pages_input:
            try:
                page_numbers = [int(p.strip()) for p in pages_input.split(',')]
            except ValueError:
                print("   ⚠️ Invalid page numbers, skipping")
        
        pdf_filter_options = {}
        if remove_blank:
            pdf_filter_options['blank_pages'] = True
        if page_numbers:
            pdf_filter_options['page_numbers'] = page_numbers
        
        if not pdf_filter_options:
            pdf_filter_options = None
        
        print(f"   ✓ Custom filtering: {pdf_filter_options}")
    
    print("\n⏳ Filtering projects...")
    
    try:
        from cloud_api_complete_workflow import CloudAPIWorkflow
        from measuresquare_extractor import MeasureSquareAPIClient
        import time
        
        # Import PDF filter if filtering is requested
        if pdf_filter_options:
            try:
                from pdf_page_filter import CloudPDFDownloaderWithFilter
                use_filter = True
                downloader = CloudPDFDownloaderWithFilter(api_key)
                print("   ✓ PDF filtering enabled")
            except ImportError:
                print("   ⚠️ PDF filter module not found, downloading without filtering")
                use_filter = False
                client = MeasureSquareAPIClient(api_key)
        else:
            use_filter = False
            client = MeasureSquareAPIClient(api_key)
        
        workflow = CloudAPIWorkflow(api_key=api_key, m2_id=m2_id)
        
        filtered = workflow.filter_projects(
            name_contains=name_filter,
            created_after=date_filter,
            customer_name=customer_filter
        )
        
        print(f"\n✅ Found {len(filtered)} matching projects:")
        for i, proj in enumerate(filtered[:20], 1):
            print(f"  {i}. {proj['Name']}")
        
        if len(filtered) > 20:
            print(f"  ... and {len(filtered) - 20} more")
        
        # Option to extract PDFs
        print(f"\nExtract PDFs for these {len(filtered)} projects? (y/n): ", end='')
        if input().lower().startswith('y'):
            output_dir = input("  Output folder (press Enter for ./filtered_pdfs): ").strip() or "./filtered_pdfs"
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            print(f"\n⏳ Extracting {len(filtered)} PDFs...")
            
            for i, proj in enumerate(filtered, 1):
                project_id = proj['ProjectId']
                project_name = proj['Name']
                pdf_path = Path(output_dir) / f"{project_name}.pdf"
                
                print(f"\n[{i}/{len(filtered)}] {project_name}")
                
                if use_filter and pdf_filter_options:
                    # Download and filter
                    result = downloader.download_and_filter(
                        project_id,
                        str(pdf_path),
                        pdf_filter_options
                    )
                    print(f"  ✓ PDF saved ({result['final_pages']} pages, removed {result['removed_pages']})")
                else:
                    # Download without filtering
                    client.download_pdf(project_id, str(pdf_path))
                    print(f"  ✓ PDF saved")
                
                time.sleep(1)  # Rate limiting
                
                # Extra pause every 10 files
                if i % 10 == 0:
                    print("  ⏸️ Cooling down...")
                    time.sleep(10)
            
            print(f"\n✅ Complete! PDFs saved to: {output_dir}")
        
    except ImportError:
        print("\n❌ ERROR: Required module not found")
        print("   Make sure pdf_page_filter.py is in the same folder")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to continue...")


def update_cloud_project(config):
    """Option 6: Update cloud project metadata"""
    clear_screen()
    print_header()
    print("📝 UPDATE CLOUD PROJECT METADATA")
    print("-" * 70)
    print()
    
    # Get credentials from config
    print("Using credentials from config.json")
    api_key = config['api']['api_key']
    m2_id = config['api']['m2_id']
    project_id = input("Project ID to update: ").strip()
    
    if not all([api_key, m2_id, project_id]):
        print("\n❌ All fields required")
        input("\nPress Enter to continue...")
        return
    
    print("\nWhat would you like to update? (Enter to skip)")
    
    updates = {}
    
    customer_name = input("  Customer name: ").strip()
    if customer_name:
        updates['ContactName'] = customer_name
    
    email = input("  Email: ").strip()
    if email:
        updates['Email'] = email
    
    phone = input("  Phone: ").strip()
    if phone:
        updates['Phone'] = phone
    
    notes = input("  Project notes: ").strip()
    if notes:
        updates['ProjectNote'] = notes
    
    if not updates:
        print("\n⚠️ No updates provided")
        input("\nPress Enter to continue...")
        return
    
    print(f"\n⏳ Updating project {project_id}...")
    
    try:
        from cloud_api_complete_workflow import CloudAPIWorkflow
        
        workflow = CloudAPIWorkflow(api_key=api_key, m2_id=m2_id)
        result = workflow.update_project_metadata(project_id, updates)
        
        print(f"\n✅ Project updated successfully!")
        
    except ImportError:
        print("\n❌ ERROR: Required module not found")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
    
    input("\nPress Enter to continue...")


def test_api_connection(config):
    """Option 3: Test cloud API connection"""
    clear_screen()
    print_header()
    print("🔌 TEST CLOUD API CONNECTION")
    print("-" * 70)
    print()
    
    print("This will test your MeasureSquare cloud API connection.")
    print("Using credentials from config.json")
    print()
    
    api_key = config['api']['api_key']
    m2_id = config['api']['m2_id']
    
    if not api_key or not m2_id:
        print("\n❌ API key and M2 ID are required")
        input("\nPress Enter to continue...")
        return
    
    print("\n⏳ Testing connection...")
    
    try:
        from measuresquare_extractor import MeasureSquareAPIClient
        
        client = MeasureSquareAPIClient(api_key)
        projects = client.get_projects(m2_id)
        
        print(f"\n✅ SUCCESS!")
        print(f"   Connected to MeasureSquare Cloud")
        print(f"   Found {len(projects)} projects")
        
        if projects:
            print("\n   Your projects:")
            for i, proj in enumerate(projects[:5], 1):
                print(f"     {i}. {proj.get('Name', 'Unnamed')}")
            
            if len(projects) > 5:
                print(f"     ... and {len(projects) - 5} more")
        
    except ImportError:
        print("\n❌ ERROR: requests module not installed!")
        print("   Please run: pip install requests")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n   Possible issues:")
        print("   - Check your API key is correct")
        print("   - Check your M2 ID (email) is correct")
        print("   - Check your internet connection")
    
    input("\nPress Enter to continue...")


def batch_convert_fez_files():
    """Option 4: Batch convert multiple FEZ files"""
    clear_screen()
    print_header()
    print("📚 BATCH CONVERT FEZ FILES")
    print("-" * 70)
    print()
    
    print("Select the folder containing FEZ files (a folder browser will open).")
    folder = pick_folder_dialog(
        title="Select folder with FEZ files",
    )

    if not folder:
        print("\n⚠️ No folder selected. Cancelling.")
        input("\nPress Enter to continue...")
        return
    
    if not Path(folder).exists():
        print(f"\n❌ Folder not found: {folder}")
        input("\nPress Enter to continue...")
        return
    
    # Find all FEZ files
    fez_files = list(Path(folder).glob("*.fez"))
    
    if not fez_files:
        print(f"\n❌ No FEZ files found in: {folder}")
        input("\nPress Enter to continue...")
        return
    
    print(f"\nFound {len(fez_files)} FEZ file(s):")
    for i, fez in enumerate(fez_files[:10], 1):
        print(f"  {i}. {fez.name}")
    if len(fez_files) > 10:
        print(f"  ... and {len(fez_files) - 10} more")
    
    print(f"\nConvert all {len(fez_files)} files to PDF? (y/n): ", end='')
    if not input().lower().startswith('y'):
        return
    
    # Process files
    print(f"\n⏳ Processing {len(fez_files)} files...")
    
    try:
        from probuildiq_reportlab_generator import ProBuildIQPDFGenerator
        
        successful = 0
        failed = []
        
        for i, fez_path in enumerate(fez_files, 1):
            print(f"\n  [{i}/{len(fez_files)}] {fez_path.name}")
            
            try:
                output_path = fez_path.with_suffix('.pdf')
                
                with ProBuildIQPDFGenerator(str(fez_path)) as generator:
                    generator.generate_pdf(
                        str(output_path),
                        include_sections=['summary', 'rooms', 'estimation']
                    )
                
                print(f"       ✓ Success")
                successful += 1
                
            except Exception as e:
                print(f"       ✗ Failed: {e}")
                failed.append(fez_path.name)
        
        print(f"\n" + "="*70)
        print(f"✅ Complete!")
        print(f"   Successful: {successful}/{len(fez_files)}")
        if failed:
            print(f"   Failed: {len(failed)}")
            for name in failed:
                print(f"     - {name}")
    
    except ImportError:
        print("\n❌ ERROR: ReportLab not installed!")
        print("   Please run: pip install reportlab")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
    
    input("\nPress Enter to continue...")


# # ==========================================
# Option 12: Batch Update Projects from CSV
# # ==========================================

# This function reads a CSV file (like the one generated by Option 8)
# and allows batch updates to multiple projects.

# Why this is useful:
# - Update 100+ projects at once
# - Use Excel to prepare updates
# - Automate metadata changes
# """

def batch_update_from_csv(config):
    """Option 12: Batch update projects from CSV file"""
    clear_screen()
    print_header()
    print("🔄 BATCH UPDATE PROJECTS FROM CSV")
    print("-" * 70)
    print()
    print("This will read a CSV file and batch update cloud projects")
    print()
    print("CSV Format Expected:")
    print("  ProjectId,ContactName,Email,Phone,ProjectNote")
    print("  abc123,John Smith,john@example.com,555-1234,Updated note")
    print()
    print("Tip: Export from Option 8, edit in Excel, then import here!")
    print()
    
    # Get credentials from config
    print("Using credentials from config.json")
    api_key = config['api']['api_key']
    m2_id = config['api']['m2_id']
    
    if not api_key or not m2_id:
        print("\n❌ Credentials required")
        input("\nPress Enter to continue...")
        return
    
    # Get CSV file via file dialog
    print("\nA file browser window will open to select your CSV file.")
    csv_path = pick_file_dialog(
        title="Select CSV file with project updates",
        filetypes=[("CSV Files", "*.csv"), ("All files", "*.*")],
    )
    
    if not csv_path:
        print("\n⚠️ No file selected. Cancelling.")
        input("\nPress Enter to continue...")
        return
    
    print(f"\nSelected: {Path(csv_path).name}")
    
    # Read CSV file
    try:
        import csv
        
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            updates_list = list(reader)
        
        if not updates_list:
            print("\n❌ CSV file is empty!")
            input("\nPress Enter to continue...")
            return
        
        print(f"\n✅ Loaded {len(updates_list)} projects from CSV")
        
        # Show first few
        print("\nFirst 5 projects to update:")
        for i, row in enumerate(updates_list[:5], 1):
            proj_id = row.get('ProjectId', 'Unknown')
            name = row.get('Name', row.get('ContactName', 'Unknown'))
            print(f"  {i}. {name} (ID: {proj_id})")
        
        if len(updates_list) > 5:
            print(f"  ... and {len(updates_list) - 5} more")
        
        # Confirm
        print(f"\n⚠️  This will update {len(updates_list)} projects!")
        print("Are you sure? (yes/no): ", end='')
        if input().lower() != 'yes':
            print("Cancelled.")
            input("\nPress Enter to continue...")
            return
        
        # Which fields to update?
        print("\nWhich fields should be updated?")
        print("(If a column exists in CSV, it will be used)")
        print()
        
        # Available fields
        available_fields = [
            'ContactName', 'Email', 'Phone', 'Mobile', 'Fax',
            'Street', 'City', 'State', 'ZipCode', 'Country',
            'ProjectNote', 'ProjectName',
            'ProjectStreet', 'ProjectCity', 'ProjectState', 
            'ProjectZipCode', 'ProjectCountry',
            'ProjectEmail', 'ProjectPhone', 'ProjectMobile'
        ]
        
        # Detect which fields are in CSV
        csv_fields = set(updates_list[0].keys())
        detected_fields = [f for f in available_fields if f in csv_fields]
        
        if detected_fields:
            print(f"Detected fields in CSV: {', '.join(detected_fields)}")
            print("\nUpdate all these fields? (y/n, default=y): ", end='')
            if input().lower().startswith('n'):
                # Let user choose
                selected_fields = []
                for field in detected_fields:
                    print(f"  Update {field}? (y/n): ", end='')
                    if input().lower().startswith('y'):
                        selected_fields.append(field)
                detected_fields = selected_fields
        
        if not detected_fields:
            print("\n⚠️ No update fields detected in CSV!")
            print("Make sure CSV has columns like: ContactName, Email, Phone, etc.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\nWill update: {', '.join(detected_fields)}")
        
        # Process updates
        print(f"\n⏳ Updating {len(updates_list)} projects...")
        print()
        
        from cloud_api_complete_workflow import CloudAPIWorkflow
        import time
        
        workflow = CloudAPIWorkflow(api_key=api_key, m2_id=m2_id)
        
        successful = 0
        failed = []
        
        for i, row in enumerate(updates_list, 1):
            project_id = row.get('ProjectId')
            
            if not project_id:
                print(f"[{i}/{len(updates_list)}] ⚠️  Skipping - No ProjectId")
                failed.append(row)
                continue
            
            project_name = row.get('Name', project_id[:8])
            print(f"[{i}/{len(updates_list)}] {project_name}... ", end='', flush=True)
            
            try:
                # Build update dict with only fields in CSV
                updates = {'ProjectId': project_id}
                
                # Add detected fields
                for field in detected_fields:
                    if field in row and row[field]:  # Only if value exists
                        updates[field] = row[field]
                
                # Also need Name field for API
                if 'Name' not in updates:
                    updates['Name'] = row.get('Name', project_name)
                
                # Update via API
                workflow.update_project_metadata(project_id, updates)
                
                print("✓")
                successful += 1
                
            except Exception as e:
                print(f"✗ ({e})")
                failed.append(row)
            
            # Rate limiting
            time.sleep(0.5)
            
            # Extra pause every 20
            if i % 20 == 0:
                print("  ⏸️ Cooling down...")
                time.sleep(5)
        
        # Summary
        print(f"\n" + "="*70)
        print(f"✅ Batch Update Complete!")
        print(f"   Successful: {successful}/{len(updates_list)}")
        
        if failed:
            print(f"   Failed: {len(failed)}")
            print("\nFailed projects:")
            for row in failed[:10]:
                proj_id = row.get('ProjectId', 'Unknown')
                name = row.get('Name', 'Unknown')
                print(f"     - {name} (ID: {proj_id})")
            
            if len(failed) > 10:
                print(f"     ... and {len(failed) - 10} more")
            
            # Option to save failed list
            print("\nSave failed projects to CSV? (y/n): ", end='')
            if input().lower().startswith('y'):
                with open('failed_updates.csv', 'w', newline='') as f:
                    if failed:
                        writer = csv.DictWriter(f, fieldnames=failed[0].keys())
                        writer.writeheader()
                        writer.writerows(failed)
                print("  ✓ Saved to: failed_updates.csv")
        
    except ImportError as e:
        print(f"\n❌ ERROR: Missing module - {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to continue...")

def show_help():
    """Option 5: Show help and documentation"""
    clear_screen()
    print_header()
    print("❓ HELP & DOCUMENTATION")
    print("-" * 70)
    print()
    
    print("📁 FILES IN THIS PACKAGE:")
    print()
    print("  📄 PDF Generation:")
    print("     • probuildiq_reportlab_generator.py - Generate PDFs from FEZ files")
    print("     • probuildiq_fez_editor.py - Edit FEZ file data")
    print("     • measuresquare_extractor.py - Cloud API client")
    print()
    print("  🧪 Testing & Examples:")
    print("     • test_extractor.py - Test all functionality")
    print("     • workflow_examples.py - Business workflow examples")
    print()
    print("  📖 Documentation:")
    print("     • PDF_GENERATION_COMPLETE_GUIDE.md - Complete PDF guide")
    print("     • QUICK_START.md - Quick start guide")
    print("     • README.md - Full documentation")
    print("     • HOW_TO_RUN.md - How to run programs")
    print()
    print("  ⚙️ Configuration:")
    print("     • requirements.txt - Python dependencies")
    print("     • config.json - Configuration (created on first run)")
    print()
    print("="*70)
    print()
    print("💡 INSTALLATION:")
    print()
    print("  1. Install Python dependencies:")
    print("     pip install -r requirements.txt")
    print()
    print("  2. (Optional) For PDF generation:")
    print("     pip install reportlab")
    print()
    print("="*70)
    print()
    print("🚀 QUICK TASKS:")
    print()
    print("  • Generate PDF from FEZ file → Option 1 from main menu")
    print("  • Clean up room names → Option 2 from main menu")
    print("  • Test cloud API → Option 3 from main menu")
    print("  • Batch convert files → Option 4 from main menu")
    print()
    print("="*70)
    print()
    print("📞 MORE HELP:")
    print()
    print("  • Read: PDF_GENERATION_COMPLETE_GUIDE.md")
    print("  • Read: QUICK_START.md")
    print("  • Check: README.md for full documentation")
    print()
    
    input("Press Enter to return to main menu...")


def extract_materials_from_projects(config):
    """Option 7: Extract materials/products from selected projects"""
    clear_screen()
    print_header()
    print("📦 EXTRACT MATERIALS/PRODUCTS FROM PROJECTS")
    print("-" * 70)
    print()
    print("This will extract detailed material and product information")
    print("from your selected cloud projects")
    print()
    
    # Get credentials from config
    print("Using credentials from config.json")
    api_key = config['api']['api_key']
    m2_id = config['api']['m2_id']
    
    if not api_key or not m2_id:
        print("\n❌ Credentials required")
        input("\nPress Enter to continue...")
        return
    
    # Get filter criteria
    print("\nProject Filter (press Enter to get all):")
    name_filter = input("  Project name contains: ").strip() or None
    
    print("\n⏳ Fetching projects...")
    
    try:
        from cloud_api_complete_workflow import CloudAPIWorkflow
        from measuresquare_extractor import MeasureSquareAPIClient
        import json
        import time
        
        workflow = CloudAPIWorkflow(api_key=api_key, m2_id=m2_id)
        client = MeasureSquareAPIClient(api_key)
        
        # Get filtered projects
        if name_filter:
            filtered = workflow.filter_projects(name_contains=name_filter)
        else:
            filtered = workflow.get_all_projects()
        
        print(f"\n✅ Found {len(filtered)} projects")
        
        if len(filtered) == 0:
            print("\n⚠️ No projects found")
            input("\nPress Enter to continue...")
            return
        
        # Show sample
        print("\nFirst 10 projects:")
        for i, proj in enumerate(filtered[:10], 1):
            print(f"  {i}. {proj['Name']}")
        
        if len(filtered) > 10:
            print(f"  ... and {len(filtered) - 10} more")
        
        # Ask if they want to extract materials
        print(f"\nExtract materials from these {len(filtered)} projects? (y/n): ", end='')
        if not input().lower().startswith('y'):
            print("Cancelled.")
            input("\nPress Enter to continue...")
            return
        
        # Choose output format
        print("\nOutput format:")
        print("  1. JSON (detailed, machine-readable)")
        print("  2. CSV (Excel-friendly)")
        print("  3. Text report (human-readable)")
        format_choice = input("Choose format (1-3, default=3): ").strip() or '3'
        
        output_file = input("Output file name (press Enter for materials_report): ").strip()
        if not output_file:
            if format_choice == '1':
                output_file = "materials_report.json"
            elif format_choice == '2':
                output_file = "materials_report.csv"
            else:
                output_file = "materials_report.txt"
        
        print(f"\n⏳ Extracting materials from {len(filtered)} projects...")
        
        all_materials = []
        
        for i, proj in enumerate(filtered, 1):
            project_id = proj['ProjectId']
            project_name = proj['Name']
            
            print(f"[{i}/{len(filtered)}] {project_name}")
            
            try:
                # Get estimation data (contains product info)
                estimation = client.get_estimation(project_id)
                
                # Extract products from estimation
                if estimation and 'Items' in estimation:
                    for item in estimation['Items']:
                        material_info = {
                            'project_id': project_id,
                            'project_name': project_name,
                            'product_name': item.get('Description', 'Unknown'),
                            'quantity': item.get('Usage', 0),
                            'unit': item.get('Unit', ''),
                            'linear_length': item.get('LinearLength', ''),
                            'net_area': item.get('NetArea', ''),
                            'waste': item.get('Waste', '')
                        }
                        all_materials.append(material_info)
                
            except Exception as e:
                print(f"  ⚠️ Error extracting from {project_name}: {e}")
            
            # Rate limiting
            if i % 10 == 0:
                time.sleep(2)
            else:
                time.sleep(0.5)
        
        # Save to file
        if format_choice == '1':
            # JSON format
            with open(output_file, 'w') as f:
                json.dump(all_materials, f, indent=2)
        
        elif format_choice == '2':
            # CSV format
            import csv
            with open(output_file, 'w', newline='') as f:
                if all_materials:
                    fieldnames = all_materials[0].keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(all_materials)
        
        else:
            # Text format
            with open(output_file, 'w') as f:
                f.write("="*70 + "\n")
                f.write("MATERIALS EXTRACTION REPORT\n")
                f.write("="*70 + "\n\n")
                f.write(f"Total Projects: {len(filtered)}\n")
                f.write(f"Total Materials: {len(all_materials)}\n")
                f.write("="*70 + "\n\n")
                
                current_project = None
                for material in all_materials:
                    if material['project_name'] != current_project:
                        current_project = material['project_name']
                        f.write(f"\n{'='*70}\n")
                        f.write(f"PROJECT: {current_project}\n")
                        f.write(f"Project ID: {material['project_id']}\n")
                        f.write(f"{'='*70}\n\n")
                    
                    f.write(f"  • {material['product_name']}\n")
                    f.write(f"    Quantity: {material['quantity']} {material['unit']}\n")
                    if material['net_area']:
                        f.write(f"    Net Area: {material['net_area']}\n")
                    if material['linear_length']:
                        f.write(f"    Linear Length: {material['linear_length']}\n")
                    if material['waste']:
                        f.write(f"    Waste: {material['waste']}\n")
                    f.write("\n")
        
        print(f"\n✅ Complete!")
        print(f"   Extracted {len(all_materials)} materials from {len(filtered)} projects")
        print(f"   Saved to: {output_file}")
        
    except ImportError:
        print("\n❌ ERROR: Required modules not found")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to continue...")


def generate_project_list_report(config):
    """Option 8: Generate project list report with ProjectId"""
    clear_screen()
    print_header()
    print("📋 GENERATE PROJECT LIST REPORT (WITH PROJECT ID)")
    print("-" * 70)
    print()
    print("This will create a comprehensive list of all your projects")
    print("with their ProjectId for easy identification")
    print()
    
    # Get credentials from config
    print("Using credentials from config.json")
    api_key = config['api']['api_key']
    m2_id = config['api']['m2_id']
    m2_idHead = m2_id.split("@", 1)[0]
    
    if not api_key or not m2_id:
        print("\n❌ Credentials required")
        input("\nPress Enter to continue...")
        return
    
    # Get filter criteria
    print("\nFilter options (press Enter to skip):")
    name_filter = input("  Project name contains: ").strip() or None
    include_archived = input("  Include archived projects? (y/n, default=n): ").strip().lower().startswith('y')
    
    print("\n⏳ Fetching projects...")
    
    try:
        from cloud_api_complete_workflow import CloudAPIWorkflow
        import json
        from datetime import datetime
        
        workflow = CloudAPIWorkflow(api_key=api_key, m2_id=m2_id)
        
        # Get all projects
        all_projects = workflow.get_all_projects(
            search=name_filter,
            is_archived=include_archived
        )
        
        print(f"\n✅ Found {len(all_projects)} projects")
        
        if len(all_projects) == 0:
            print("\n⚠️ No projects found")
            input("\nPress Enter to continue...")
            return
        
        # Choose output format
        print("\nOutput format:")
        print("  1. JSON (detailed, machine-readable)")
        print("  2. CSV (Excel-friendly)")
        print("  3. Text report (human-readable)")
        print("  4. Markdown table (documentation-friendly)")
        format_choice = input("Choose format (1-4, default=3): ").strip() or '3'
        
        config_output = Path(config['output']['project_list'])
        print(f"Default folder: {config_output}")
        output_file = input("Output file name (press Enter for default, or include a path): ").strip()

        if not output_file:
            # ✅ create the output file
            if format_choice == '1':
                output_path = config_output / f"{m2_idHead}_project_list.json"
            elif format_choice == '2':
                output_path = config_output / f"{m2_idHead}_project_list.csv"
            elif format_choice == '4':
                output_path = config_output / f"{m2_idHead}_project_list.md"
            else:
                output_path = config_output / f"{m2_idHead}_project_list.txt"
        else:
            output_path = Path(output_file)

        # ✅ ensure the folder exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"\n⏳ Generating report...")
        
        # Save to file based on format
        if format_choice == '1':
            # JSON format
            with output_path.open('w') as f:
                json.dump(all_projects, f, indent=2)
        
        elif format_choice == '2':
            # CSV format
            import csv
            with output_path.open('w', newline='') as f:
                fieldnames = ['ProjectId', 'Name', 'Revision', 'OwnerM2Id', 'LastUpdatedOn', 'Size', 'IsArchived']
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()

                for proj in all_projects:
                    proj = proj.copy()
                    ts = proj.get('LastUpdateOn')
                    if ts: 
                        proj['LastUpdatedOn'] = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        proj["LastUpdatedOn"] = ''
                    writer.writerows(all_projects)
        
        elif format_choice == '4':
            # Markdown table format
            with output_path.open('w') as f:
                f.write("# Project List Report\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"Total Projects: {len(all_projects)}\n\n")
                f.write("## Projects\n\n")
                f.write("| # | Project Name | Project ID | Updated | Archived |\n")
                f.write("|---|--------------|------------|---------|----------|\n")
                
                for i, proj in enumerate(all_projects, 1):
                    name = proj.get('Name', 'Unknown')
                    proj_id = proj.get('ProjectId', 'Unknown')
                    updated = datetime.fromtimestamp(proj.get('LastUpdatedOn', 0)).strftime('%Y-%m-%d') if proj.get('LastUpdatedOn') else 'Unknown'
                    archived = '✓' if proj.get('IsArchived', False) else ''
                    
                    f.write(f"| {i} | {name} | `{proj_id}` | {updated} | {archived} | \n")
        
        else:
            # Text format (most detailed)
            with output_path.open('w') as f:
                f.write("="*70 + "\n")
                f.write("PROJECT LIST REPORT\n")
                f.write("="*70 + "\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"M2 ID: {m2_id}\n")
                f.write(f"Total Projects: {len(all_projects)}\n")
                f.write("="*70 + "\n\n")
                
                for i, proj in enumerate(all_projects, 1):
                    f.write(f"\n{'='*70}\n")
                    f.write(f"#{i}: {proj.get('Name', 'Unknown')}\n")
                    f.write(f"{'='*70}\n")
                    f.write(f"Project ID: {proj.get('ProjectId', 'Unknown')}\n")
                    f.write(f"Revision: {proj.get('Revision', 'Unknown')}\n")
                    f.write(f"Owner: {proj.get('OwnerM2Id', 'Unknown')}\n")
                    
                    if proj.get('LastUpdatedOn'):
                        updated = datetime.fromtimestamp(proj['LastUpdatedOn']).strftime('%Y-%m-%d %H:%M:%S')
                        f.write(f"Last Updated: {updated}\n")
                    
                    if proj.get('Size'):
                        size_kb = proj['Size'] / 1024
                        f.write(f"File Size: {size_kb:.2f} KB\n")
                    
                    if proj.get('IsArchived'):
                        f.write(f"Status: ARCHIVED\n")
                    
                    if proj.get('Tags'):
                        f.write(f"Tags: {', '.join(proj['Tags'])}\n")
                    
                    f.write("\n")
        
        print(f"\n✅ Complete!")
        print(f"   Report generated: {output_file}")
        print(f"   Total projects: {len(all_projects)}")
        
        # Show first few projects
        print(f"\nFirst 5 projects:")
        for i, proj in enumerate(all_projects[:5], 1):
            print(f"  {i}. {proj['Name']}")
            print(f"     ProjectId: {proj['ProjectId']}")
        
        if len(all_projects) > 5:
            print(f"  ... and {len(all_projects) - 5} more in the report")
        
    except ImportError:
        print("\n❌ ERROR: Required modules not found")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to continue...")


def main_menu():
    """Main menu loop"""
    while True:
        # Load configuration
        config = load_config()
        if not config:
            return
        
        clear_screen()
        print("\nConfiguration loaded:")
        print(f"  API Key: {'*' * 10}{config['api']['api_key'][-4:]}")
        print(f"  M2 ID: {config['api']['m2_id']}")
        print(f"  Local FEZ: {config['local']['fez_file_path']}")

        print_header()
        print("What would you like to do?")
        print()
        print("\n  LOCAL FILE OPTIONS:")
        print("  1. 📄 Generate PDF from local FEZ file (basic quality)")
        print("  2. ✏️  Edit FEZ file (rename rooms, update products)")
        print()
        print("  CLOUD API OPTIONS:")
        print("  3. ☁️  Upload FEZ to cloud & get high-quality PDF")
        print("  4. 📊 Get all cloud projects (handles 400+)")
        print("  5. 🔍 Filter & extract specific cloud projects (with PDF filtering)")
        print("  6. 📝 Update cloud project metadata")
        print("  7. 📦 Extract materials/products from projects")
        print("  8. 📋 Generate project list report (with ProjectId)")
        print("  9. 🔄 Batch update projects from CSV")
        print()
        print("  OTHER:")
        print("  10. 🔌 Test cloud API connection")
        print("  11. 📚 Batch convert multiple local FEZ files")
        print("  12. ❓ Help & Documentation")
        print("  0. 🚪 Exit")
        print()
        
        choice = input("Enter your choice (0-12): ").strip()
        
        if choice == '1':
            generate_pdf_from_fez()
        elif choice == '2':
            edit_fez_file()
        elif choice == '3':
            upload_to_cloud_and_extract(config)
        elif choice == '4':
            get_all_cloud_projects(config)
        elif choice == '5':
            filter_cloud_projects(config)
        elif choice == '6':
            update_cloud_project(config)
        elif choice == '7':
            extract_materials_from_projects(config)
        elif choice == '8':
            generate_project_list_report(config)
        elif choice == '9':
            batch_update_from_csv(config)
        elif choice == '10':
            test_api_connection(config)
        elif choice == '11':
            batch_convert_fez_files()
        elif choice == '12':
            show_help()
        elif choice == '0':
            print("\n👋 Goodbye!")
            sys.exit(0)
        else:
            print("\n❌ Invalid choice. Please enter 0-11.")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
