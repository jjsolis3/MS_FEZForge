"""
Practical Workflow Example: Batch Processing MeasureSquare Projects

This demonstrates real-world use cases:
1. Process multiple projects in bulk
2. Generate reports for all projects
3. Export data for accounting/inventory systems
4. Compare projects or track changes
"""

import json
import re
import time
from pathlib import Path
from datetime import datetime
from measuresquare_extractor import (
    MeasureSquareAPIClient,
    MeasureSquareExtractor
)
from typing import List, Dict, Optional


# =============================================================================
# Use Case 1: Generate Reports for All Active Projects
# =============================================================================

def export_all_projects_to_pdf(api_key, m2_id, output_dir="./reports"):
    """
    Export PDF reports for all non-archived projects
    
    Why this is useful:
    - Batch generate reports for client presentations
    - Create backup documentation
    - Archive project states at specific dates
    
    Args:
        api_key: Your MeasureSquare API key
        m2_id: Your MeasureSquare ID (email)
        output_dir: Directory to save PDFs
    """
    print("="*60)
    print("BATCH PDF EXPORT")
    print("="*60)
    
    client = MeasureSquareAPIClient(api_key)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get all active projects
    print(f"\nFetching projects for {m2_id}...")
    projects = client.get_projects(m2_id, is_archived=False)
    print(f"Found {len(projects)} active projects")
    
    # Process each project
    successful = 0
    failed = []
    
    for i, project in enumerate(projects, 1):
        project_id = project['ProjectId']
        project_name = project.get('Name', 'Unnamed').replace('/', '-')
        
        print(f"\n[{i}/{len(projects)}] Processing: {project_name}")
        
        try:
            # Generate safe filename
            # Why sanitize? Filenames can't contain certain characters
            safe_name = "".join(c for c in project_name 
                               if c.isalnum() or c in (' ', '-', '_'))
            pdf_filename = f"{safe_name}_{project_id[:8]}.pdf"
            pdf_path = output_path / pdf_filename
            
            # Download PDF
            print(f"  Generating PDF...")
            client.download_pdf(project_id, output_path=str(pdf_path))
            
            file_size = pdf_path.stat().st_size / 1024
            print(f"  ✓ Saved: {pdf_filename} ({file_size:.1f} KB)")
            
            successful += 1
            
            # Rate limiting: PDF endpoint has limits
            # Why sleep? Prevents hitting rate limits (10 per minute)
            if i % 10 == 0:
                import time
                print("  Pausing to respect rate limits...")
                time.sleep(60)
            
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            failed.append(project_name)
    
    # Summary
    print("\n" + "="*60)
    print(f"Successfully exported: {successful}/{len(projects)}")
    if failed:
        print(f"Failed: {len(failed)}")
        for name in failed:
            print(f"  - {name}")


# =============================================================================
# Use Case 2: Extract Material Quantities for Inventory Management
# =============================================================================

def export_material_summary(api_key, m2_id, output_file="material_summary.json"):
    """
    Create a summary of all materials needed across all projects
    
    Why this is useful:
    - Plan bulk material orders
    - Track inventory needs
    - Forecast costs across multiple jobs
    
    Args:
        api_key: Your MeasureSquare API key
        m2_id: Your MeasureSquare ID
        output_file: Path to save summary JSON
    """
    print("="*60)
    print("MATERIAL SUMMARY EXPORT")
    print("="*60)
    
    client = MeasureSquareAPIClient(api_key)
    
    # Get all active projects
    projects = client.get_projects(m2_id, is_archived=False)
    print(f"Analyzing {len(projects)} projects...")
    
    # Aggregate materials across all projects
    # Why dictionary? Fast lookup by product ID
    material_totals = {}
    project_details = []
    
    for project in projects:
        project_id = project['ProjectId']
        project_name = project.get('Name', 'Unnamed')
        
        print(f"\nProcessing: {project_name}")
        
        try:
            # Get estimation data
            estimation = client.get_estimation(project_id)
            
            # Extract products and quantities
            # Note: API response structure may vary
            if isinstance(estimation, dict):
                products = estimation.get('Products', [])
                
                project_materials = []
                
                for product in products:
                    product_id = product.get('ID', 'unknown')
                    product_name = product.get('Name', 'Unknown')
                    quantity = float(product.get('TotalQuantity', 0))
                    unit = product.get('Unit', '')
                    
                    # Add to totals
                    if product_id not in material_totals:
                        material_totals[product_id] = {
                            'name': product_name,
                            'total_quantity': 0,
                            'unit': unit,
                            'projects': []
                        }
                    
                    material_totals[product_id]['total_quantity'] += quantity
                    material_totals[product_id]['projects'].append(project_name)
                    
                    project_materials.append({
                        'product': product_name,
                        'quantity': quantity,
                        'unit': unit
                    })
                
                project_details.append({
                    'project_name': project_name,
                    'project_id': project_id,
                    'materials': project_materials
                })
                
                print(f"  Found {len(products)} products")
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Create summary report
    summary = {
        'generated_at': datetime.now().isoformat(),
        'total_projects': len(projects),
        'material_totals': material_totals,
        'project_details': project_details
    }
    
    # Save to JSON
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Exported to: {output_file}")
    print(f"\nTotal unique materials: {len(material_totals)}")
    print("\nTop 10 materials by quantity:")
    
    # Sort by quantity
    sorted_materials = sorted(
        material_totals.items(),
        key=lambda x: x[1]['total_quantity'],
        reverse=True
    )
    
    for i, (prod_id, data) in enumerate(sorted_materials[:10], 1):
        print(f"  {i}. {data['name']}: {data['total_quantity']:.2f} {data['unit']}")


# =============================================================================
# Use Case 3: Compare Project Versions
# =============================================================================

def compare_project_versions(api_key, project_id_1, project_id_2):
    """
    Compare two versions of a project to see what changed
    
    Why this is useful:
    - Track design changes
    - Verify revisions
    - Audit material quantity changes
    
    Args:
        api_key: Your MeasureSquare API key
        project_id_1: First project ID (original)
        project_id_2: Second project ID (revised)
    """
    print("="*60)
    print("PROJECT COMPARISON")
    print("="*60)
    
    client = MeasureSquareAPIClient(api_key)
    
    # Get data for both projects
    print("\nFetching project 1...")
    est1 = client.get_estimation(project_id_1)
    
    print("Fetching project 2...")
    est2 = client.get_estimation(project_id_2)
    
    # Compare products
    # Why use sets? Fast membership testing for comparisons
    products1 = {p['ID']: p for p in est1.get('Products', [])}
    products2 = {p['ID']: p for p in est2.get('Products', [])}
    
    # Find differences
    added = set(products2.keys()) - set(products1.keys())
    removed = set(products1.keys()) - set(products2.keys())
    common = set(products1.keys()) & set(products2.keys())
    
    print("\n" + "="*60)
    print("CHANGES DETECTED")
    print("="*60)
    
    if added:
        print(f"\nAdded Products ({len(added)}):")
        for prod_id in added:
            product = products2[prod_id]
            print(f"  + {product['Name']}: {product['TotalQuantity']}")
    
    if removed:
        print(f"\nRemoved Products ({len(removed)}):")
        for prod_id in removed:
            product = products1[prod_id]
            print(f"  - {product['Name']}: {product['TotalQuantity']}")
    
    if common:
        print(f"\nQuantity Changes:")
        has_changes = False
        for prod_id in common:
            qty1 = float(products1[prod_id]['TotalQuantity'])
            qty2 = float(products2[prod_id]['TotalQuantity'])
            
            if abs(qty1 - qty2) > 0.01:  # Tolerance for floating point
                has_changes = True
                diff = qty2 - qty1
                pct_change = (diff / qty1 * 100) if qty1 != 0 else 0
                
                print(f"  {products1[prod_id]['Name']}")
                print(f"    {qty1:.2f} → {qty2:.2f} ({pct_change:+.1f}%)")
        
        if not has_changes:
            print("  No quantity changes detected")


# =============================================================================
# Use Case 4: Export for Accounting System
# =============================================================================

def export_for_accounting(api_key, m2_id, output_file="accounting_export.json"):
    """
    Export project data in format suitable for accounting systems
    
    Why this is useful:
    - Import into QuickBooks, Xero, etc.
    - Create invoices
    - Track job costs
    
    Args:
        api_key: Your MeasureSquare API key
        m2_id: Your MeasureSquare ID
        output_file: Path to save export
    """
    print("="*60)
    print("ACCOUNTING EXPORT")
    print("="*60)
    
    client = MeasureSquareAPIClient(api_key)
    
    # Get all projects
    projects = client.get_projects(m2_id)
    
    accounting_records = []
    
    for project in projects:
        project_id = project['ProjectId']
        project_name = project.get('Name', 'Unnamed')
        
        print(f"\nProcessing: {project_name}")
        
        try:
            # Get project details
            project_info = client.get_project_info(project_id)
            estimation = client.get_estimation(project_id)
            
            # Extract customer information
            customer_info = {
                'name': project_info.get('ProjectName', ''),
                'street': project_info.get('ProjectStreet', ''),
                'city': project_info.get('ProjectCity', ''),
                'state': project_info.get('ProjectState', ''),
                'zip': project_info.get('ProjectZipCode', ''),
                'phone': project_info.get('ProjectPhone', ''),
                'email': project_info.get('ProjectEmail', '')
            }
            
            # Extract line items (products)
            line_items = []
            total_cost = 0
            total_price = 0
            
            for product in estimation.get('Products', []):
                quantity = float(product.get('TotalQuantity', 0))
                cost_price = float(product.get('CostPrice', 0))
                sales_price = float(product.get('SalesPrice', 0))
                
                item_cost = quantity * cost_price
                item_price = quantity * sales_price
                
                line_items.append({
                    'description': product.get('Name', ''),
                    'quantity': quantity,
                    'unit': product.get('Unit', ''),
                    'unit_cost': cost_price,
                    'unit_price': sales_price,
                    'total_cost': item_cost,
                    'total_price': item_price
                })
                
                total_cost += item_cost
                total_price += item_price
            
            # Create accounting record
            accounting_records.append({
                'project_id': project_id,
                'project_name': project_name,
                'customer': customer_info,
                'line_items': line_items,
                'subtotal': total_price,
                'total_cost': total_cost,
                'gross_profit': total_price - total_cost,
                'margin_percent': ((total_price - total_cost) / total_price * 100) 
                                 if total_price > 0 else 0,
                'last_updated': project.get('LastUpdatedOn', '')
            })
            
            print(f"  Total: ${total_price:,.2f}")
            print(f"  Cost: ${total_cost:,.2f}")
            print(f"  Profit: ${total_price - total_cost:,.2f}")
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Save export
    export_data = {
        'export_date': datetime.now().isoformat(),
        'company_id': m2_id,
        'records': accounting_records,
        'summary': {
            'total_projects': len(accounting_records),
            'total_revenue': sum(r['subtotal'] for r in accounting_records),
            'total_cost': sum(r['total_cost'] for r in accounting_records),
            'total_profit': sum(r['gross_profit'] for r in accounting_records)
        }
    }
    
    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print("\n" + "="*60)
    print("EXPORT SUMMARY")
    print("="*60)
    print(f"Saved to: {output_file}")
    print(f"Total Revenue: ${export_data['summary']['total_revenue']:,.2f}")
    print(f"Total Cost: ${export_data['summary']['total_cost']:,.2f}")
    print(f"Total Profit: ${export_data['summary']['total_profit']:,.2f}")


# =============================================================================
# Use Case 5: Backup All Projects Locally
# =============================================================================

def backup_all_projects(api_key, m2_id, backup_dir="./project_backups"):
    """
    Download all project FEZ files for local backup
    
    Why this is useful:
    - Create offline backups
    - Archive completed projects
    - Ensure data availability
    
    Args:
        api_key: Your MeasureSquare API key
        m2_id: Your MeasureSquare ID
        backup_dir: Directory for backups
    """
    print("="*60)
    print("PROJECT BACKUP")
    print("="*60)
    
    client = MeasureSquareAPIClient(api_key)
    backup_path = Path(backup_dir)
    backup_path.mkdir(parents=True, exist_ok=True)
    
    # Get all projects
    projects = client.get_projects(m2_id)
    print(f"Backing up {len(projects)} projects...")
    
    successful = 0
    
    for i, project in enumerate(projects, 1):
        project_id = project['ProjectId']
        project_name = project.get('Name', 'Unnamed').replace('/', '-')
        
        print(f"\n[{i}/{len(projects)}] {project_name}")
        
        try:
            # Create safe filename
            safe_name = "".join(c for c in project_name 
                               if c.isalnum() or c in (' ', '-', '_'))
            fez_filename = f"{safe_name}_{project_id[:8]}.fez"
            fez_path = backup_path / fez_filename
            
            # Download FEZ file
            client.download_fez(project_id, output_path=str(fez_path))
            
            file_size = fez_path.stat().st_size / 1024
            print(f"  ✓ Saved: {file_size:.1f} KB")
            
            successful += 1
        
        except Exception as e:
            print(f"  ✗ Failed: {e}")
    
    print("\n" + "="*60)
    print(f"Successfully backed up: {successful}/{len(projects)} projects")


# =============================================================================
# Use Case 6: Batch PDF Export with Filtering
# =============================================================================

class BatchPDFExporter:
    """
    Export PDFs from multiple projects with filtering support.

    Features:
    - Export all projects
    - Export a filtered subset by name list, ID list, or name pattern
    - Respects MeasureSquare rate limits (10 PDFs/min, 1s between calls)
    - Progress tracking
    - Load filter list from a text file
    """

    # MeasureSquare rate limits for PDF endpoint
    MIN_INTERVAL_SECONDS = 1.5  # slightly above 1s minimum to be safe
    PAUSE_EVERY_N = 9  # pause after every 9 downloads (limit is 10/min)
    PAUSE_DURATION = 60  # seconds to pause for rate limit reset

    def __init__(self, api_key: str, m2_id: str,
                 x_application: str = None, secret_key: str = None):
        self.client = MeasureSquareAPIClient(api_key, x_application, secret_key)
        self.m2_id = m2_id
        self._last_download_time = 0
        self._download_count = 0

    def _get_all_projects(self) -> List[Dict]:
        """Get all projects using pagination."""
        from cloud_api_complete_workflow import CloudAPIWorkflow
        workflow = CloudAPIWorkflow(self.client.api_key, self.m2_id)
        return workflow.get_all_projects()

    def _apply_rate_limit(self):
        """Enforce rate limiting between PDF downloads."""
        # Enforce minimum interval
        elapsed = time.time() - self._last_download_time
        if elapsed < self.MIN_INTERVAL_SECONDS:
            time.sleep(self.MIN_INTERVAL_SECONDS - elapsed)

        # Pause every N downloads to respect 10/min limit
        self._download_count += 1
        if self._download_count % self.PAUSE_EVERY_N == 0:
            print(f"   Rate limit pause ({self.PAUSE_DURATION}s after {self._download_count} downloads)...")
            time.sleep(self.PAUSE_DURATION)

    def _download_single_pdf(self, project: Dict, output_dir: Path) -> Optional[str]:
        """
        Download a single project's PDF with rate limiting.

        Returns:
            Path to saved PDF, or None on failure.
        """
        project_id = project['ProjectId']
        project_name = project.get('Name', 'Unnamed').replace('/', '-')

        # Create safe filename
        safe_name = "".join(c for c in project_name
                            if c.isalnum() or c in (' ', '-', '_'))
        pdf_filename = f"{safe_name}_{project_id[:8]}.pdf"
        pdf_path = output_dir / pdf_filename

        try:
            self._apply_rate_limit()
            self._last_download_time = time.time()
            self.client.download_pdf(project_id, output_path=str(pdf_path))
            return str(pdf_path)
        except Exception as e:
            print(f"   Failed: {e}")
            return None

    def export_all(self, output_dir: str = "./pdf_exports") -> Dict:
        """
        Export PDFs for all projects.

        Args:
            output_dir: Directory to save PDFs

        Returns:
            Summary dict with counts and file paths
        """
        projects = self._get_all_projects()
        return self._export_projects(projects, output_dir)

    def export_filtered(self, filter_list: List[str],
                        output_dir: str = "./pdf_exports",
                        match_by: str = "name") -> Dict:
        """
        Export PDFs only for projects matching a filter list.

        Args:
            filter_list: List of project names or IDs to include
            output_dir: Directory to save PDFs
            match_by: "name" to match by project name, "id" to match by ProjectId

        Returns:
            Summary dict
        """
        all_projects = self._get_all_projects()

        filter_set = {item.strip().lower() for item in filter_list}

        if match_by == "id":
            matched = [p for p in all_projects
                       if p['ProjectId'].lower() in filter_set]
        else:
            matched = [p for p in all_projects
                       if p.get('Name', '').strip().lower() in filter_set]

        print(f"Matched {len(matched)} of {len(filter_list)} filter entries "
              f"(from {len(all_projects)} total projects)")

        return self._export_projects(matched, output_dir)

    def export_by_pattern(self, pattern: str,
                          output_dir: str = "./pdf_exports") -> Dict:
        """
        Export PDFs for projects whose names match a regex or substring pattern.

        Args:
            pattern: Regex pattern or substring to match project names
            output_dir: Directory to save PDFs

        Returns:
            Summary dict
        """
        all_projects = self._get_all_projects()

        try:
            regex = re.compile(pattern, re.IGNORECASE)
            matched = [p for p in all_projects
                       if regex.search(p.get('Name', ''))]
        except re.error:
            # Fall back to substring match
            pattern_lower = pattern.lower()
            matched = [p for p in all_projects
                       if pattern_lower in p.get('Name', '').lower()]

        print(f"Pattern '{pattern}' matched {len(matched)} projects")

        return self._export_projects(matched, output_dir)

    def export_from_file(self, filter_file: str,
                         output_dir: str = "./pdf_exports",
                         match_by: str = "name") -> Dict:
        """
        Export PDFs for projects listed in a text file (one per line).

        Args:
            filter_file: Path to text file with project names/IDs, one per line
            output_dir: Directory to save PDFs
            match_by: "name" or "id"

        Returns:
            Summary dict
        """
        filter_path = Path(filter_file)
        if not filter_path.exists():
            raise FileNotFoundError(f"Filter file not found: {filter_file}")

        lines = filter_path.read_text().strip().splitlines()
        filter_list = [line.strip() for line in lines if line.strip()]

        print(f"Loaded {len(filter_list)} entries from {filter_file}")
        return self.export_filtered(filter_list, output_dir, match_by)

    def _export_projects(self, projects: List[Dict], output_dir: str) -> Dict:
        """
        Internal method to export PDFs for a list of projects.

        Returns:
            Summary dict with 'successful', 'failed', 'total', 'files'
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        total = len(projects)
        if total == 0:
            print("No projects to export.")
            return {'successful': 0, 'failed': 0, 'total': 0, 'files': []}

        print(f"\nExporting {total} project PDF(s) to: {output_path}")
        print("=" * 60)

        self._download_count = 0
        successful = []
        failed = []

        for i, project in enumerate(projects, 1):
            name = project.get('Name', 'Unnamed')
            print(f"[{i}/{total}] {name}")

            path = self._download_single_pdf(project, output_path)
            if path:
                file_size = Path(path).stat().st_size / 1024
                print(f"   Saved ({file_size:.1f} KB)")
                successful.append(path)
            else:
                failed.append(name)

        # Summary
        print("\n" + "=" * 60)
        print(f"Export complete: {len(successful)}/{total} successful")
        if failed:
            print(f"Failed ({len(failed)}):")
            for name in failed:
                print(f"  - {name}")

        return {
            'successful': len(successful),
            'failed': len(failed),
            'total': total,
            'files': successful
        }


# =============================================================================
# Main Menu
# =============================================================================

def main():
    """Interactive menu for workflow examples"""
    
    print("\n" + "="*60)
    print("MEASURESQUARE WORKFLOW EXAMPLES")
    print("="*60)
    
    # Load configuration
    try:
        with open("config.json") as f:
            config = json.load(f)
        
        api_key = config['api']['api_key']
        m2_id = config['api']['m2_id']
        
    except FileNotFoundError:
        print("\n❌ config.json not found!")
        print("Run test_extractor.py first to create configuration")
        return
    
    print("\nSelect a workflow:")
    print("1. Export all projects to PDF")
    print("2. Generate material summary")
    print("3. Compare two project versions")
    print("4. Export for accounting system")
    print("5. Backup all projects locally")
    print("6. Run all workflows")
    print("0. Exit")
    
    choice = input("\nEnter choice (0-6): ").strip()
    
    if choice == '1':
        export_all_projects_to_pdf(api_key, m2_id)
    
    elif choice == '2':
        export_material_summary(api_key, m2_id)
    
    elif choice == '3':
        proj1 = input("Enter first project ID: ").strip()
        proj2 = input("Enter second project ID: ").strip()
        compare_project_versions(api_key, proj1, proj2)
    
    elif choice == '4':
        export_for_accounting(api_key, m2_id)
    
    elif choice == '5':
        backup_all_projects(api_key, m2_id)
    
    elif choice == '6':
        print("\nRunning all workflows...")
        export_all_projects_to_pdf(api_key, m2_id)
        export_material_summary(api_key, m2_id)
        export_for_accounting(api_key, m2_id)
        backup_all_projects(api_key, m2_id)
    
    elif choice == '0':
        print("Exiting...")
    
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
