"""
Test Script for MeasureSquare Data Extractor

This script demonstrates how to use the extractor with your actual data.
Fill in your credentials in config.json and run this script.
"""

import json
from pathlib import Path
from measuresquare_extractor import (
    MeasureSquareAPIClient,
    FEZFileParser,
    MeasureSquareExtractor
)


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


def test_api_connection(config):
    """
    Test 1: Verify API connection and credentials
    
    This is the first thing to test - can we connect to the API?
    """
    print("\n" + "="*60)
    print("TEST 1: API Connection")
    print("="*60)
    
    try:
        api_config = config['api']
        client = MeasureSquareAPIClient(
            api_key=api_config['api_key'],
            x_application=api_config.get('x_application'),
            secret_key=api_config.get('secret_key')
        )
        
        print("✓ API client initialized")
        
        # Try to get project list
        m2_id = api_config['m2_id']
        print(f"  Fetching projects for {m2_id}...")
        
        projects = client.get_projects(m2_id)
        
        print(f"✓ Successfully connected!")
        print(f"  Found {len(projects)} projects")
        
        # Display project list
        if projects:
            print("\n  Your projects:")
            for i, proj in enumerate(projects[:5], 1):  # Show first 5
                print(f"    {i}. {proj.get('Name', 'Unnamed')} (ID: {proj.get('ProjectId')})")
            
            if len(projects) > 5:
                print(f"    ... and {len(projects) - 5} more")
        
        return True, projects
        
    except Exception as e:
        print(f"✗ API connection failed: {e}")
        print("\n  Troubleshooting:")
        print("  - Check that your API key is correct")
        print("  - Verify your M2 ID (email) is correct")
        print("  - If you get 401 errors, contact MeasureSquare for X-Headers")
        return False, []


def test_project_data_extraction(config, projects):
    """
    Test 2: Extract data from a project
    
    This tests the actual data extraction functionality
    """
    print("\n" + "="*60)
    print("TEST 2: Project Data Extraction")
    print("="*60)
    
    if not projects:
        print("✗ No projects available to test")
        return False
    
    try:
        # Use first project
        project = projects[0]
        project_id = project['ProjectId']
        project_name = project.get('Name', 'Unnamed')
        
        print(f"Testing with project: {project_name}")
        print(f"Project ID: {project_id}")
        
        api_config = config['api']
        client = MeasureSquareAPIClient(
            api_key=api_config['api_key'],
            x_application=api_config.get('x_application'),
            secret_key=api_config.get('secret_key')
        )
        
        # Test 2a: Get layers
        print("\n  Getting layers...")
        layers = client.get_layers(project_id)
        print(f"  ✓ Found {len(layers)} layer(s)")
        
        # Display layer info
        for layer in layers:
            print(f"    Layer: {layer.get('Name', 'Unnamed')}")
            rooms = layer.get('Rooms', [])
            if rooms:
                print(f"      Rooms: {len(rooms)}")
                for room in rooms[:3]:  # Show first 3 rooms
                    area = room.get('Area', 0)
                    print(f"        - {room.get('Name')}: {area:.2f} sq ft")
        
        # Test 2b: Get estimations
        print("\n  Getting estimations...")
        estimation = client.get_estimation(project_id)
        print(f"  ✓ Retrieved estimation data")
        
        # Display summary
        if isinstance(estimation, dict):
            products = estimation.get('Products', [])
            if products:
                print(f"    Products used: {len(products)}")
                for prod in products[:3]:
                    print(f"      - {prod.get('Name', 'Unknown')}: {prod.get('TotalQuantity', 0):.2f}")
        
        # Test 2c: Get layer assignment
        print("\n  Getting product assignments...")
        assignments = client.get_layer_assignment(project_id)
        print(f"  ✓ Retrieved assignment data")
        
        return True
        
    except Exception as e:
        print(f"✗ Data extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_image_download(config, projects):
    """
    Test 3: Download project images
    
    This tests image/diagram export functionality
    """
    print("\n" + "="*60)
    print("TEST 3: Image Download")
    print("="*60)
    
    if not projects:
        print("✗ No projects available to test")
        return False
    
    try:
        project = projects[0]
        project_id = project['ProjectId']
        
        api_config = config['api']
        client = MeasureSquareAPIClient(
            api_key=api_config['api_key'],
            x_application=api_config.get('x_application'),
            secret_key=api_config.get('secret_key')
        )
        
        # Create output directory
        output_dir = Path(config['output']['images_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"  Downloading images to: {output_dir}")
        
        # Download all images as ZIP
        client.download_all_images(
            project_id,
            width=1920,
            height=1080,
            output_dir=str(output_dir)
        )
        
        print(f"  ✓ Images downloaded successfully")
        
        # List downloaded files
        image_files = list(output_dir.glob("*.png"))
        if image_files:
            print(f"    Downloaded {len(image_files)} image(s):")
            for img in image_files:
                print(f"      - {img.name}")
        
        return True
        
    except Exception as e:
        print(f"✗ Image download failed: {e}")
        return False


def test_pdf_export(config, projects):
    """
    Test 4: Export project as PDF
    
    This tests PDF report generation
    """
    print("\n" + "="*60)
    print("TEST 4: PDF Export")
    print("="*60)
    
    if not projects:
        print("✗ No projects available to test")
        return False
    
    try:
        project = projects[0]
        project_id = project['ProjectId']
        project_name = project.get('Name', 'Unnamed').replace(' ', '_')
        
        api_config = config['api']
        client = MeasureSquareAPIClient(
            api_key=api_config['api_key'],
            x_application=api_config.get('x_application'),
            secret_key=api_config.get('secret_key')
        )
        
        # Create output directory
        output_dir = Path(config['output']['reports_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        pdf_path = output_dir / f"{project_name}.pdf"
        
        print(f"  Generating PDF: {pdf_path}")
        
        client.download_pdf(project_id, output_path=str(pdf_path))
        
        print(f"  ✓ PDF exported successfully")
        print(f"    Size: {pdf_path.stat().st_size / 1024:.1f} KB")
        
        return True
        
    except Exception as e:
        print(f"✗ PDF export failed: {e}")
        print("  Note: PDF generation may have rate limits (max 10/minute)")
        return False


def test_local_file_parsing(config):
    """
    Test 5: Parse local FEZ file
    
    This tests the offline/local parsing capability
    """
    print("\n" + "="*60)
    print("TEST 5: Local FEZ File Parsing")
    print("="*60)
    
    fez_path = config['local'].get('fez_file_path')
    
    if not fez_path or not Path(fez_path).exists():
        print("✗ FEZ file not found or not configured")
        print(f"  Configured path: {fez_path}")
        print("  Update 'local.fez_file_path' in config.json")
        return False
    
    try:
        print(f"  Parsing: {fez_path}")
        
        with FEZFileParser(fez_path) as parser:
            
            # Get application info
            app_info = parser.get_application_info()
            print(f"  ✓ File opened successfully")
            print(f"    Application: {app_info.get('ApplicationType', 'Unknown')}")
            print(f"    Version: {app_info.get('Version', 'Unknown')}")
            
            # Get layers
            print("\n  Extracting layers...")
            layers = parser.get_layers()
            print(f"  ✓ Found {len(layers)} layer(s)")
            
            total_rooms = sum(len(layer['rooms']) for layer in layers)
            print(f"    Total rooms: {total_rooms}")
            
            # Get products
            print("\n  Extracting products...")
            products = parser.get_products()
            print(f"  ✓ Found {len(products)} product(s)")
            
            for prod in products[:3]:
                print(f"    - {prod['name']} ({prod['type']})")
            
            # Get estimations
            print("\n  Extracting estimations...")
            estimations = parser.get_estimations()
            print(f"  ✓ Found {len(estimations)} estimation(s)")
            
            for est in estimations[:3]:
                print(f"    - Usage: {est['usage']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Local file parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_json_export(config, projects):
    """
    Test 6: Export all data to JSON
    
    This tests the complete data export functionality
    """
    print("\n" + "="*60)
    print("TEST 6: JSON Data Export")
    print("="*60)
    
    if not projects:
        print("✗ No projects available to test")
        return False
    
    try:
        project = projects[0]
        project_id = project['ProjectId']
        
        api_config = config['api']
        
        # Use the unified extractor
        extractor = MeasureSquareExtractor(
            api_key=api_config['api_key'],
            x_application=api_config.get('x_application'),
            secret_key=api_config.get('secret_key')
        )
        
        # Export to JSON
        json_path = config['output']['json_export']
        Path(json_path).parent.mkdir(parents=True, exist_ok=True)
        
        print(f"  Exporting to: {json_path}")
        
        extractor.export_data_to_json(json_path, project_id=project_id)
        
        print(f"  ✓ Data exported successfully")
        
        # Show file size
        file_size = Path(json_path).stat().st_size
        print(f"    Size: {file_size / 1024:.1f} KB")
        
        # Load and show structure
        with open(json_path) as f:
            data = json.load(f)
        
        print(f"    Contains:")
        print(f"      - Layers: {len(data.get('layers', []))}")
        print(f"      - Products: {len(data.get('products', []))}")
        print(f"      - Estimations: {len(data.get('estimations', []))}")
        
        return True
        
    except Exception as e:
        print(f"✗ JSON export failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("MEASURESQUARE DATA EXTRACTOR - TEST SUITE")
    print("="*60)
    
    # Load configuration
    config = load_config()
    if not config:
        return
    
    print("\nConfiguration loaded:")
    print(f"  API Key: {'*' * 10}{config['api']['api_key'][-4:]}")
    print(f"  M2 ID: {config['api']['m2_id']}")
    print(f"  Local FEZ: {config['local']['fez_file_path']}")
    
    # Run tests
    results = {}
    
    # Test 1: API Connection
    api_ok, projects = test_api_connection(config)
    results['API Connection'] = api_ok
    
    if api_ok:
        # Test 2: Data Extraction
        results['Data Extraction'] = test_project_data_extraction(config, projects)
        
        # Test 3: Image Download
        results['Image Download'] = test_image_download(config, projects)
        
        # Test 4: PDF Export
        results['PDF Export'] = test_pdf_export(config, projects)
        
        # Test 6: JSON Export
        results['JSON Export'] = test_json_export(config, projects)
    
    # Test 5: Local File (independent)
    results['Local FEZ Parsing'] = test_local_file_parsing(config)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {test_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for passed in results.values() if passed)
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Your setup is working correctly.")
    elif passed_tests > 0:
        print("\n⚠️  Some tests passed. Review failures above.")
    else:
        print("\n❌ All tests failed. Check your configuration and credentials.")


if __name__ == "__main__":
    main()
