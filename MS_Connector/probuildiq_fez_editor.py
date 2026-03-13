"""
ProBuildIQ FEZ Editor & Local PDF Generator

This module provides:
1. Edit/modify FEZ file data (names, labels, products)
2. Generate PDFs from local FEZ files (without cloud)
3. AI-assisted diagram interpretation and rendering
4. Customizable PDF output (select sections)

Why we need this:
- Cloud API generates PDFs server-side (requires upload)
- Local files can't generate PDFs via API
- Need to modify project data before export
- Want custom PDF layouts
"""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import io
import base64


# =============================================================================
# FEZ File Editor - Modify project data
# =============================================================================

class FEZFileEditor:
    """
    Edit and modify FEZ file contents
    
    Capabilities:
    - Update room names
    - Modify product assignments
    - Edit measurements
    - Add/remove layers
    - Save changes back to FEZ
    
    Why this is useful:
    - Fix naming before generating reports
    - Update product prices
    - Correct measurements
    - Standardize naming conventions
    """
    
    def __init__(self, fez_path: str):
        """
        Initialize editor with FEZ file
        
        Args:
            fez_path: Path to .fez file
        """
        self.fez_path = Path(fez_path)
        self.zip_file = zipfile.ZipFile(self.fez_path, 'r')
        
        # Load and parse XML
        xml_content = self.zip_file.read('_serialized_content.xml')
        self.root = ET.fromstring(xml_content)
        self.tree = ET.ElementTree(self.root)
        
        # Track modifications
        self.modified = False
    
    def get_all_room_names(self) -> List[Dict[str, str]]:
        """
        Get all room names in the project
        
        Returns:
            List of dicts with room IDs and names
        """
        rooms = []
        
        # Find all plan regions (rooms)
        for plan_region in self.root.findall('.//PlanRegion'):
            room_id = plan_region.get('shapeId', '')
            if room_id:
                rooms.append({
                    'id': room_id,
                    'name': room_id,
                    'element': plan_region
                })
        
        return rooms
    
    def rename_room(self, old_name: str, new_name: str) -> bool:
        """
        Rename a room in the project
        
        Why this is important:
        - Room names appear in reports and PDFs
        - Need consistent naming (e.g., "Master Bath" vs "MBR")
        - Makes reports more professional
        
        Args:
            old_name: Current room name
            new_name: New room name
            
        Returns:
            True if room was found and renamed
        """
        found = False
        
        # Find and update all references to this room
        for plan_region in self.root.findall('.//PlanRegion'):
            shape_id = plan_region.get('shapeId', '')
            if shape_id == old_name:
                plan_region.set('shapeId', new_name)
                found = True
                self.modified = True
        
        # Also update in other locations where room names appear
        for result_elem in self.root.findall('.//*[@sourceShapes]'):
            source_shapes = result_elem.get('sourceShapes', '')
            if old_name in source_shapes:
                # Replace in semicolon-separated list
                shapes = source_shapes.split(';')
                shapes = [new_name if s == old_name else s for s in shapes]
                result_elem.set('sourceShapes', ';'.join(shapes))
                found = True
                self.modified = True
        
        return found
    
    def batch_rename_rooms(self, name_mapping: Dict[str, str]) -> int:
        """
        Rename multiple rooms at once
        
        Example:
            name_mapping = {
                'Primary Bdrm': 'Master Bedroom',
                'MBR CL': 'Master Bedroom Closet',
                'LR CL': 'Living Room Closet'
            }
        
        Args:
            name_mapping: Dict of {old_name: new_name}
            
        Returns:
            Number of rooms renamed
        """
        count = 0
        for old_name, new_name in name_mapping.items():
            if self.rename_room(old_name, new_name):
                count += 1
        
        return count
    
    def update_product_info(self, product_id: str, updates: Dict) -> bool:
        """
        Update product information (price, description, etc.)
        
        Args:
            product_id: Product ID (fepID)
            updates: Dict of attributes to update
                     e.g., {'salesPrice': '5.99', 'vendor': 'New Vendor'}
        
        Returns:
            True if product was found and updated
        """
        found = False
        
        # Find all product types
        product_types = ['PlankProduct', 'RollProduct', 'LinearProduct', 
                        'CountProduct', 'TileProduct']
        
        for prod_type in product_types:
            for product in self.root.findall(f'.//{prod_type}[@fepID="{product_id}"]'):
                for key, value in updates.items():
                    product.set(key, str(value))
                found = True
                self.modified = True
        
        return found
    
    def add_project_note(self, note: str):
        """
        Add or update project notes
        
        Args:
            note: Note text to add
        """
        # Find or create project info
        project_info = self.root.find('.//ProjectInfo')
        if project_info is None:
            return False
        
        project_info.set('ProjectNote', note)
        self.modified = True
        return True
    
    def save(self, output_path: Optional[str] = None) -> str:
        """
        Save modifications back to FEZ file
        
        Why we create a new file:
        - Safer than overwriting original
        - Preserves original as backup
        - ZIP files can't be modified in-place easily
        
        Args:
            output_path: Path for new FEZ file (default: add _modified suffix)
        
        Returns:
            Path to saved file
        """
        if not self.modified:
            print("No modifications to save")
            return str(self.fez_path)
        
        # Determine output path
        if output_path is None:
            output_path = self.fez_path.parent / f"{self.fez_path.stem}_modified.fez"
        else:
            output_path = Path(output_path)
        
        # Create new ZIP with modified XML
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as new_zip:
            
            # Copy all files except the XML we're modifying
            for item in self.zip_file.namelist():
                if item != '_serialized_content.xml':
                    data = self.zip_file.read(item)
                    new_zip.writestr(item, data)
            
            # Write modified XML
            xml_bytes = ET.tostring(self.root, encoding='utf-8')
            new_zip.writestr('_serialized_content.xml', xml_bytes)
        
        print(f"Saved modified FEZ to: {output_path}")
        return str(output_path)
    
    def close(self):
        """Close the ZIP file"""
        self.zip_file.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# =============================================================================
# Local PDF Generator - Generate PDFs without cloud API
# =============================================================================

class LocalPDFGenerator:
    """
    Generate PDFs from local FEZ files
    
    Three approaches:
    1. Temporary cloud upload (uses MS rendering)
    2. HTML-to-PDF conversion (custom rendering)
    3. AI-assisted rendering (best quality)
    """
    
    def __init__(self, fez_path: str):
        self.fez_path = Path(fez_path)
        
        # Import parser
        from measuresquare_extractor import FEZFileParser
        self.parser = FEZFileParser(str(fez_path))
    
    def generate_pdf_via_temporary_upload(self, api_client, m2_id: str, 
                                         output_path: str = None) -> bytes:
        """
        Approach 1: Upload to cloud temporarily, generate PDF, download
        
        Pros: Uses MeasureSquare's official rendering
        Cons: Requires internet, uploads file temporarily
        
        Args:
            api_client: MeasureSquareAPIClient instance
            m2_id: Your MeasureSquare ID
            output_path: Where to save PDF
            
        Returns:
            PDF bytes
        """
        print("Approach 1: Temporary cloud upload")
        
        # Read FEZ file
        with open(self.fez_path, 'rb') as f:
            fez_data = f.read()
        
        # Upload as new project (with temp marker in name)
        print("  Uploading FEZ file...")
        # Note: Would need to implement project creation via POST API
        # This is complex - see API documentation for POST /api/{m2Id}/projects
        
        # Generate PDF from uploaded project
        # Download PDF
        # Delete temporary project
        
        raise NotImplementedError("Temporary upload not yet implemented")
    
    def generate_html_report(self, include_sections: List[str] = None) -> str:
        """
        Approach 2: Generate HTML report that can be converted to PDF
        
        Pros: Works offline, customizable
        Cons: Need to implement rendering logic
        
        Args:
            include_sections: List of sections to include
                            ['summary', 'rooms', 'products', 'estimation']
        
        Returns:
            HTML string
        """
        if include_sections is None:
            include_sections = ['summary', 'rooms', 'products', 'estimation']
        
        # Get data from parser
        app_info = self.parser.get_application_info()
        layers = self.parser.get_layers()
        products = self.parser.get_products()
        estimations = self.parser.get_estimations()
        
        # Build HTML
        html_parts = [
            self._html_header(),
            self._html_styles()
        ]
        
        if 'summary' in include_sections:
            html_parts.append(self._html_summary(app_info))
        
        if 'rooms' in include_sections:
            html_parts.append(self._html_rooms(layers))
        
        if 'products' in include_sections:
            html_parts.append(self._html_products(products))
        
        if 'estimation' in include_sections:
            html_parts.append(self._html_estimation(estimations, products))
        
        html_parts.append(self._html_footer())
        
        return '\n'.join(html_parts)
    
    def _html_header(self) -> str:
        """Generate HTML header"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ProBuildIQ Flooring Estimate</title>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ProBuildIQ Flooring Estimate</h1>
        </div>
"""
    
    def _html_styles(self) -> str:
        """Generate CSS styles"""
        return """
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white;
            padding: 40px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        .header { 
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        h1 { color: #2c3e50; font-size: 2.5em; }
        h2 { 
            color: #34495e; 
            margin-top: 30px; 
            margin-bottom: 15px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }
        h3 { color: #7f8c8d; margin-top: 20px; }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin: 20px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        th { 
            background: #3498db; 
            color: white; 
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        td { 
            padding: 10px; 
            border-bottom: 1px solid #ddd;
        }
        tr:hover { background: #f8f9fa; }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin: 20px 0;
        }
        .summary-card {
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }
        .summary-label { 
            font-weight: bold; 
            color: #7f8c8d;
            font-size: 0.9em;
            text-transform: uppercase;
        }
        .summary-value { 
            font-size: 1.5em; 
            color: #2c3e50;
            margin-top: 5px;
        }
        .total-row {
            background: #2c3e50;
            color: white;
            font-weight: bold;
        }
        .total-row td { border: none; }
        @media print {
            body { background: white; }
            .container { box-shadow: none; padding: 20px; }
        }
    </style>
"""
    
    def _html_summary(self, app_info: Dict) -> str:
        """Generate project summary section"""
        project_name = self.fez_path.stem.replace('_', ' ').title()
        
        return f"""
        <section class="summary">
            <h2>Project Summary</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="summary-label">Project Name</div>
                    <div class="summary-value">{project_name}</div>
                </div>
                <div class="summary-card">
                    <div class="summary-label">Application</div>
                    <div class="summary-value">{app_info.get('ApplicationType', 'Floor Covering')}</div>
                </div>
                <div class="summary-card">
                    <div class="summary-label">Version</div>
                    <div class="summary-value">{app_info.get('Version', 'N/A')}</div>
                </div>
                <div class="summary-card">
                    <div class="summary-label">Generated</div>
                    <div class="summary-value">{app_info.get('DateTime', 'N/A')[:10]}</div>
                </div>
            </div>
        </section>
"""
    
    def _html_rooms(self, layers: List[Dict]) -> str:
        """Generate rooms section"""
        html = '<section class="rooms"><h2>Room Measurements</h2>'
        
        for layer_idx, layer in enumerate(layers):
            if not layer['rooms']:
                continue
            
            html += f'<h3>Layer {layer_idx + 1}</h3>'
            html += '<table><thead><tr>'
            html += '<th>Room Name</th><th>Area (sq ft)</th><th>Perimeter (ft)</th>'
            html += '</tr></thead><tbody>'
            
            total_area = 0
            for room in layer['rooms']:
                area = room['area'] / 144  # Convert to sq ft (assuming mm²)
                total_area += area
                
                html += '<tr>'
                html += f'<td>{room["name"]}</td>'
                html += f'<td>{area:.2f}</td>'
                html += '<td>--</td>'  # Perimeter not calculated yet
                html += '</tr>'
            
            html += '<tr class="total-row">'
            html += f'<td>Total</td><td>{total_area:.2f} sq ft</td><td></td>'
            html += '</tr>'
            html += '</tbody></table>'
        
        html += '</section>'
        return html
    
    def _html_products(self, products: List[Dict]) -> str:
        """Generate products section"""
        html = '<section class="products"><h2>Materials</h2>'
        html += '<table><thead><tr>'
        html += '<th>Product Name</th><th>Type</th><th>Vendor</th>'
        html += '<th>Cost Price</th><th>Sales Price</th>'
        html += '</tr></thead><tbody>'
        
        for product in products:
            html += '<tr>'
            html += f'<td>{product["name"]}</td>'
            html += f'<td>{product["type"]}</td>'
            html += f'<td>{product.get("vendor", "N/A")}</td>'
            cost = product.get('cost_price', 0) or 0
            sales = product.get('sales_price', 0) or 0
            html += f'<td>${cost:.2f}</td>'
            html += f'<td>${sales:.2f}</td>'
            html += '</tr>'
        
        html += '</tbody></table></section>'
        return html
    
    def _html_estimation(self, estimations: List[Dict], products: List[Dict]) -> str:
        """Generate estimation/takeoff section"""
        # Create product lookup
        product_map = {p['id']: p['name'] for p in products}
        
        html = '<section class="estimation"><h2>Material Takeoff</h2>'
        html += '<table><thead><tr>'
        html += '<th>Product</th><th>Rooms</th><th>Quantity</th><th>Waste</th><th>Total</th>'
        html += '</tr></thead><tbody>'
        
        for est in estimations:
            product_ref = est['product_ref'].split(';')[0]
            product_name = product_map.get(product_ref, product_ref)
            
            html += '<tr>'
            html += f'<td>{product_name}</td>'
            html += f'<td>{est.get("rooms", "N/A")}</td>'
            html += f'<td>{est.get("original_qty", 0):.2f}</td>'
            html += f'<td>{est.get("waste", 0):.2f}</td>'
            html += f'<td>{est.get("usage", 0):.2f}</td>'
            html += '</tr>'
        
        html += '</tbody></table></section>'
        return html
    
    def _html_footer(self) -> str:
        """Generate HTML footer"""
        return """
    </div>
</body>
</html>
"""
    
    def save_html(self, output_path: str, include_sections: List[str] = None):
        """
        Save HTML report to file
        
        Args:
            output_path: Where to save HTML
            include_sections: Which sections to include
        """
        html = self.generate_html_report(include_sections)
        
        output_path = Path(output_path)
        output_path.write_text(html, encoding='utf-8')
        
        print(f"HTML report saved to: {output_path}")
        print(f"Open in browser or convert to PDF with:")
        print(f"  - Chrome: Print → Save as PDF")
        print(f"  - wkhtmltopdf: wkhtmltopdf {output_path} output.pdf")
        print(f"  - weasyprint: weasyprint {output_path} output.pdf")
    
    def close(self):
        """Close parser"""
        self.parser.close()


# =============================================================================
# AI-Assisted PDF Generator (Using Claude/Anthropic API)
# =============================================================================

class AIPDFGenerator:
    """
    Use AI to interpret XML and generate high-quality PDFs
    
    Why this approach is powerful:
    - AI can understand context and fix ambiguities
    - Generates professional layouts automatically
    - Handles edge cases in XML structure
    - Can create custom visualizations
    
    Requires:
    - Anthropic API key
    - Uses Claude to generate HTML/CSS
    - Converts to PDF
    """
    
    def __init__(self, fez_path: str, anthropic_api_key: str = None):
        self.fez_path = Path(fez_path)
        self.api_key = anthropic_api_key
        
        from measuresquare_extractor import FEZFileParser
        self.parser = FEZFileParser(str(fez_path))
    
    def generate_with_ai(self, 
                        include_sections: List[str] = None,
                        custom_prompt: str = None) -> str:
        """
        Use AI to generate PDF content
        
        How it works:
        1. Extract data from FEZ file
        2. Send to Claude with instructions
        3. Claude generates HTML/CSS
        4. Convert HTML to PDF
        
        Args:
            include_sections: Sections to include
            custom_prompt: Additional instructions for AI
            
        Returns:
            HTML string generated by AI
        """
        if not self.api_key:
            raise ValueError("Anthropic API key required for AI generation")
        
        # Extract all data
        app_info = self.parser.get_application_info()
        layers = self.parser.get_layers()
        products = self.parser.get_products()
        estimations = self.parser.get_estimations()
        
        # Prepare data for AI
        data_json = json.dumps({
            'project_info': app_info,
            'layers': layers,
            'products': products,
            'estimations': estimations
        }, indent=2)
        
        # Create prompt for Claude
        prompt = f"""I have flooring project data extracted from a MeasureSquare FEZ file.
Please generate a professional HTML report with embedded CSS styling.

Include these sections: {include_sections or ['all']}

Requirements:
- Professional, clean design
- Tables for measurements and materials
- Summary cards for key metrics
- Print-friendly layout
- Responsive design

{custom_prompt or ''}

Here's the project data:
```json
{data_json}
```

Generate complete HTML with embedded CSS. Make it look professional and suitable for client presentation.
"""
        
        # Call Anthropic API (would need implementation)
        # For now, return placeholder
        print("Would call Anthropic API here with prompt...")
        print("This requires: pip install anthropic")
        
        # Return generated HTML from AI
        return "<html><!-- AI-generated content would go here --></html>"


# =============================================================================
# Usage Examples
# =============================================================================

def example_edit_fez_file():
    """Example: Edit room names in FEZ file"""
    
    with FEZFileEditor("/path/to/project.fez") as editor:
        
        # Show current room names
        rooms = editor.get_all_room_names()
        print("Current rooms:")
        for room in rooms:
            print(f"  - {room['name']}")
        
        # Rename rooms for better clarity
        name_mapping = {
            'Primary Bdrm': 'Master Bedroom',
            'MBR CL': 'Master Bedroom Closet',
            'LR CL': 'Living Room Closet',
            'Master Vanity': 'Master Bathroom Vanity'
        }
        
        count = editor.batch_rename_rooms(name_mapping)
        print(f"\nRenamed {count} rooms")
        
        # Update product pricing
        editor.update_product_info(
            'Vinyl Plank',
            {'salesPrice': '5.99', 'vendor': 'ProBuildIQ Flooring'}
        )
        
        # Save modified file
        new_file = editor.save()
        print(f"Saved to: {new_file}")


def example_generate_local_pdf():
    """Example: Generate PDF from local FEZ file"""
    
    generator = LocalPDFGenerator("/path/to/project.fez")
    
    # Generate HTML report
    generator.save_html(
        "project_report.html",
        include_sections=['summary', 'rooms', 'products', 'estimation']
    )
    
    # Convert to PDF (requires external tool)
    print("\nTo convert to PDF:")
    print("1. Open project_report.html in Chrome")
    print("2. Press Ctrl+P")
    print("3. Select 'Save as PDF'")
    print("\nOr install: pip install weasyprint")
    print("Then run: weasyprint project_report.html project_report.pdf")


if __name__ == "__main__":
    print("ProBuildIQ FEZ Editor & PDF Generator")
    print("=" * 60)
    print("\nCapabilities:")
    print("1. Edit FEZ files (rename rooms, update products)")
    print("2. Generate PDFs from local files (HTML approach)")
    print("3. AI-assisted PDF generation (coming soon)")
    print("\nSee example functions for usage.")
