# QUICK START GUIDE - For Your Setup

Since you already have your MeasureSquare API key, here's how to get started immediately!

## Step 1: Download Your Files ⬇️

All files are ready in the outputs directory:
- `measuresquare_extractor.py` - Main library (32 KB)
- `test_extractor.py` - Test script (14 KB)
- `workflow_examples.py` - Practical examples (18 KB)
- `README.md` - Full documentation (13 KB)
- `requirements.txt` - Dependencies

## Step 2: Install Dependencies 📦

```bash
# In your terminal/command prompt:
pip install -r requirements.txt
```

This installs only one package: `requests` (for HTTP API calls)

## Step 3: Create Your Configuration 🔧

Run the test script to create a config template:

```bash
python test_extractor.py
```

This creates `config.json`. Edit it with your actual values:

```json
{
  "api": {
    "api_key": "13a86≥434",  // ← Your API key from screenshot
    "x_application": null,    // ← Leave null for now
    "secret_key": null,       // ← Leave null for now
    "m2_id": "mslfc.mgr@seamlessfloor..."  // ← Your email
  },
  "local": {
    "fez_file_path": "G:\\Shared drives\\SEAMLESS FLOORING SALES\\MEASURE SQUARE\\..."
  }
}
```

**Important Notes:**
- Your API key from the screenshot: `13a86...` (use the full key)
- Your M2 ID is: `mslfc.mgr@seamlessfloor...` (from the screenshot)
- Leave `x_application` and `secret_key` as `null` initially
- If you get auth errors, contact: integration@measuresquare.com for X-Headers

## Step 4: Run Your First Test 🧪

```bash
python test_extractor.py
```

This will:
1. ✓ Test API connection with your key
2. ✓ List your projects
3. ✓ Extract data from first project
4. ✓ Download layer images
5. ✓ Generate PDF report
6. ✓ Parse local FEZ file (if path configured)

Expected output:
```
==============================================================
MEASURESQUARE DATA EXTRACTOR - TEST SUITE
==============================================================

Configuration loaded:
  API Key: **********≥434
  M2 ID: mslfc.mgr@seamlessfloor...
  
==============================================================
TEST 1: API Connection
==============================================================
✓ API client initialized
  Fetching projects for mslfc.mgr@seamlessfloor...
✓ Successfully connected!
  Found XX projects
  
  Your projects:
    1. B Down - 1x1 (ID: ...)
    2. [Other projects...]
```

## Step 5: Try Practical Workflows 💼

Once tests pass, try the workflow examples:

```bash
python workflow_examples.py
```

This gives you a menu:
```
1. Export all projects to PDF
2. Generate material summary
3. Compare two project versions
4. Export for accounting system
5. Backup all projects locally
```

## Your Specific Use Cases

Based on your B_Down_-_1x1.fez file, here's how to extract its data:

### Option A: Via API (If uploaded to cloud)
```python
from measuresquare_extractor import MeasureSquareAPIClient

client = MeasureSquareAPIClient(api_key="your_key")

# Find the project
projects = client.get_projects("your.email@company.com")
# Look for "B Down - 1x1" in the list

project_id = "..." # The ID of B Down - 1x1

# Get layers and rooms
layers = client.get_layers(project_id)
for layer in layers:
    print(f"Layer: {layer['Name']}")
    for room in layer.get('Rooms', []):
        print(f"  - {room['Name']}: {room['Area']:.2f} sq ft")

# Get estimations
estimation = client.get_estimation(project_id)

# Download images
client.download_all_images(project_id, output_dir="./B_Down_Images")

# Export PDF
client.download_pdf(project_id, "B_Down_Report.pdf")
```

### Option B: Parse Local File
```python
from measuresquare_extractor import FEZFileParser

fez_path = "G:\\Shared drives\\...\\B Down - 1x1.fez"

with FEZFileParser(fez_path) as parser:
    # Get layers and rooms
    layers = parser.get_layers()
    for layer in layers:
        for room in layer['rooms']:
            print(f"{room['name']}: {room['area']:.2f}")
    
    # Get products
    products = parser.get_products()
    for prod in products:
        print(f"{prod['name']}: ${prod['sales_price']}")
    
    # Get estimations
    estimations = parser.get_estimations()
    for est in estimations:
        print(f"Rooms: {est['rooms']}")
        print(f"Quantity: {est['usage']:.2f}")
```

## Understanding Your B Down - 1x1 Project

From the files you shared, your project contains:
- **Primary Bdrm** - 153.86 sq ft (Carpet - 5 Star Fleck VP Seattle)
- **Dining Rm** - Areas with vinyl plank
- **Kitchen** - Areas with vinyl plank
- **Living Rm** - Large area
- **Master Bath** - Vinyl plank
- **Master Vanity** - Vinyl plank
- **MBR CL** (Master Bedroom Closet)
- **LR CL** (Living Room Closet)

The system calculated:
- Total vinyl plank needed (with waste)
- Quarter round molding
- Metal Z-Bar for transitions
- Tub strip

## Common Tasks

### Export takeoff to JSON
```python
extractor = MeasureSquareExtractor(api_key="your_key")
extractor.export_data_to_json("B_Down_Data.json", project_id="...")
```

### Get material list for ordering
```python
estimation = client.get_estimation(project_id)
products = estimation['Products']

for product in products:
    print(f"{product['Name']}: {product['TotalQuantity']} {product['Unit']}")
```

### Generate report with images
```python
# Download images
client.download_all_images(project_id, output_dir="./images")

# Generate PDF
client.download_pdf(project_id, "report.pdf")
```

## Troubleshooting

### "401 Unauthorized"
- Double-check your API key (from screenshot: 13a86...)
- Verify M2 ID is your email
- May need X-Headers (contact MeasureSquare)

### "Can't find project"
- Make sure project is uploaded to cloud
- Check if it's archived
- Try `get_projects()` to list all available IDs

### "Local file not found"
- Use full path: `G:\\Shared drives\\...`
- Check file permissions
- Make sure FEZ file isn't open in MeasureSquare

## Next Steps

1. **Run tests** - Verify everything works
2. **Try workflows** - Export PDFs, material summaries
3. **Customize** - Add your own business logic
4. **Integrate** - Connect to your accounting/inventory systems

## Support

- **API Issues**: integration@measuresquare.com
- **Code Help**: Read the inline comments - they explain everything!
- **Questions**: All code is documented with "why" explanations

## File Overview

```
measuresquare_extractor.py
├── MeasureSquareAPIClient    ← For cloud API access
├── FEZFileParser            ← For local file parsing
└── MeasureSquareExtractor   ← Hybrid (uses both)

test_extractor.py
└── Tests all functionality with your data

workflow_examples.py
├── Batch PDF export
├── Material summary
├── Project comparison
├── Accounting export
└── Project backup
```

Good luck! The code is heavily commented to help you learn as you go. 🚀
