# MeasureSquare Data Extractor

A comprehensive Python tool for extracting diagrams, measurements, and takeoffs from MeasureSquare projects using both the Cloud API and local FEZ file parsing.

## 📋 Features

- ✅ **Cloud API Integration** - Extract data from MeasureSquare Cloud
- ✅ **Local FEZ Parsing** - Parse project files offline
- ✅ **Hybrid Mode** - Automatic fallback between API and local parsing
- ✅ **Image Export** - Download floor plan diagrams and layer images
- ✅ **Measurement Extraction** - Get room dimensions, areas, and perimeters
- ✅ **Takeoff Data** - Extract material quantities and estimations
- ✅ **Multiple Export Formats** - PDF, DXF, JSON, and images
- ✅ **Well-Documented** - Extensive code comments explaining the "why"

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Credentials

Run the test script to create a configuration template:

```bash
python test_extractor.py
```

This creates `config.json`. Edit it with your credentials:

```json
{
  "api": {
    "api_key": "your_api_key_from_screenshot",
    "x_application": "contact_measuresquare_support",
    "secret_key": "contact_measuresquare_support",
    "m2_id": "your.email@company.com"
  },
  "local": {
    "fez_file_path": "/path/to/your/project.fez"
  }
}
```

**Note about X-Headers:**
- You can try without `x_application` and `secret_key` initially
- If you get authentication errors, contact integration@measuresquare.com
- They will provide both the X-Application ID and Secret Key

### 3. Run Tests

```bash
python test_extractor.py
```

This will:
- Test your API connection
- Extract data from your first project
- Download images and generate reports
- Parse local FEZ files
- Export everything to JSON

## 📖 Usage Examples

### Example 1: Using the API Client

```python
from measuresquare_extractor import MeasureSquareAPIClient

# Initialize client
client = MeasureSquareAPIClient(
    api_key="your_api_key",
    x_application="your_app_id",  # Optional
    secret_key="your_secret"      # Optional
)

# Get your projects
projects = client.get_projects("your.email@company.com")
print(f"Found {len(projects)} projects")

# Get layers and rooms from a project
project_id = projects[0]['ProjectId']
layers = client.get_layers(project_id)

for layer in layers:
    print(f"Layer: {layer['Name']}")
    for room in layer.get('Rooms', []):
        print(f"  - {room['Name']}: {room['Area']:.2f} sq ft")

# Get material estimations
estimation = client.get_estimation(project_id)

# Download images
client.download_all_images(project_id, output_dir="./images")

# Export to PDF
client.download_pdf(project_id, output_path="./report.pdf")
```

### Example 2: Parsing Local FEZ Files

```python
from measuresquare_extractor import FEZFileParser

# Parse a local FEZ file
with FEZFileParser("/path/to/project.fez") as parser:
    
    # Get application info
    app_info = parser.get_application_info()
    print(f"Version: {app_info['Version']}")
    
    # Get layers and rooms
    layers = parser.get_layers()
    for layer in layers:
        for room in layer['rooms']:
            print(f"{room['name']}: {room['area']:.2f} sq units")
    
    # Get products
    products = parser.get_products()
    for product in products:
        print(f"{product['name']} - ${product['sales_price']}")
    
    # Get estimations
    estimations = parser.get_estimations()
    for est in estimations:
        print(f"Product: {est['product_ref']}")
        print(f"Quantity: {est['usage']:.2f}")
```

### Example 3: Hybrid Approach (Recommended)

```python
from measuresquare_extractor import MeasureSquareExtractor

# Initialize with both API and local fallback
extractor = MeasureSquareExtractor(
    api_key="your_api_key",
    fez_path="/path/to/backup.fez"  # Fallback if API fails
)

# These methods automatically use API first, then fallback to local
layers = extractor.get_layers(project_id="123")
products = extractor.get_products(project_id="123")
estimations = extractor.get_estimations(project_id="123")

# Export all data to JSON
extractor.export_data_to_json("project_data.json", project_id="123")
```

## 🏗️ Architecture

### Why This Design?

The codebase uses a **three-layer architecture** for maximum flexibility:

```
┌─────────────────────────────────────┐
│   MeasureSquareExtractor           │  ← Unified interface
│   (Hybrid approach)                 │
└──────────┬──────────────────────────┘
           │
           ├─────────────┬─────────────┐
           │             │             │
┌──────────▼───────┐ ┌──▼──────────┐ │
│ APIClient        │ │ FEZParser   │ │
│ (Cloud access)   │ │ (Local)     │ │
└──────────────────┘ └─────────────┘ │
                                      │
                              ┌───────▼────────┐
                              │ Data Models    │
                              │ (Room, Product)│
                              └────────────────┘
```

**Benefits:**
1. **Separation of Concerns** - Each class has one responsibility
2. **Easy Testing** - Each component can be tested independently
3. **Flexible Usage** - Use API, local parsing, or both
4. **Future-Proof** - Easy to add new data sources

### Why Use Classes?

```python
# ❌ Without classes (procedural)
def get_layers(api_key, project_id):
    headers = generate_headers(api_key)  # Regenerate every time
    response = requests.get(url, headers=headers)
    return response.json()

# ✅ With classes (object-oriented)
class MeasureSquareAPIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()  # Reuse connection
    
    def get_layers(self, project_id):
        # Headers generated once, session reused
        return self._make_request(f"projects/{project_id}/layers")
```

**Why this is better:**
- State management (API key stored once)
- Connection reuse (faster)
- DRY principle (don't repeat yourself)
- Easier to extend with new methods

### Why Use Dataclasses?

```python
# ❌ Using dictionaries
room = {
    'id': '123',
    'name': 'Living Room',
    'area': 250.5
}
# No type checking, easy to make mistakes

# ✅ Using dataclasses
@dataclass
class Room:
    id: str
    name: str
    area: float

room = Room(id='123', name='Living Room', area=250.5)
# Type checking, autocomplete in IDE, cleaner code
```

## 📊 Data Structures

### Project Structure

```
Project
├── ProjectId: str
├── Name: str
├── Layers: List[Layer]
│   ├── Layer
│   │   ├── Name: str
│   │   ├── Rooms: List[Room]
│   │   │   └── Room
│   │   │       ├── Name: str
│   │   │       ├── Area: float
│   │   │       └── Perimeter: float
│   │   └── Products: List[Product]
│   └── ...
└── Estimations: List[Estimation]
    └── Estimation
        ├── ProductName: str
        ├── Quantity: float
        ├── Unit: str
        └── Waste: float
```

## 🔧 API Endpoints Reference

### Project Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/{m2Id}/projects` | GET | List all projects |
| `GET /api/projects/{projectId}` | GET | Get project details |
| `POST /api/{m2Id}/projects` | POST | Create/update project |

### Data Extraction

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/projects/{projectId}/layers` | GET | Get layers and rooms |
| `GET /api/projects/{projectId}/estimation` | GET | Get takeoffs |
| `GET /api/projects/{projectId}/worksheets` | GET | Get worksheets |
| `GET /api/projects/{projectId}/layerAssignment` | GET | Get product assignments |

### Export

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/projects/{projectId}/images` | GET | Download all images (ZIP) |
| `GET /api/projects/{projectId}/layers/{layerIndex}/image` | GET | Download layer image |
| `GET /api/projects/{projectId}/pdf` | GET | Generate PDF report |
| `GET /api/projects/{projectId}/dxf` | GET | Export to DXF (CAD) |
| `GET /api/projects/{projectId}/download` | GET | Download FEZ file |

## 🔐 Authentication

### Basic Auth

All API requests use HTTP Basic Authentication:

```python
# API Key as username, no password
auth_string = f"{api_key}:"
auth_base64 = base64.b64encode(auth_string.encode()).decode()

headers = {
    'Authorization': f'Basic {auth_base64}'
}
```

### X-Headers (Optional but Recommended)

Some operations may require additional security headers:

```python
headers = {
    'X-Application': 'your_app_id',
    'X-Timestamp': str(int(time.time())),
    'X-Signature': generate_hmac_sha256(timestamp, secret_key)
}
```

**To get X-Headers:**
Contact MeasureSquare at integration@measuresquare.com

## 📁 FEZ File Format

FEZ files are ZIP archives containing:

```
project.fez (ZIP)
├── _serialized_content.xml   ← Main project data
├── ApplicationInfo.xml        ← Metadata
└── [other files]
```

### XML Structure

The main XML contains:
- **Layers** (`<FepLayer>`) - Floor/level information
- **Rooms** (`<FepFloor>`) - Room shapes and dimensions
- **Products** (`<PlankProduct>`, `<RollProduct>`, etc.) - Materials
- **Estimations** (`<EstimateArea>`) - Quantity takeoffs

## 🐛 Troubleshooting

### API Connection Issues

**Problem:** `401 Unauthorized`
```
Solution: Check your API key is correct
- Copy from MeasureSquare Cloud Settings
- Don't include any extra spaces
- If still failing, you may need X-Headers
```

**Problem:** `404 Not Found`
```
Solution: Verify the project ID exists
- Use get_projects() to list valid IDs
- Project may be archived
```

**Problem:** Rate limit errors
```
Solution: Some endpoints have limits
- PDF generation: max 10 per minute
- Add delays between bulk operations
```

### Local File Parsing Issues

**Problem:** `Invalid FEZ file`
```
Solution: Check the file
- Is it a valid .fez file?
- Is it corrupted?
- Try opening in MeasureSquare first
```

**Problem:** Missing room data
```
Solution: XML structure varies by version
- Some data may not be in XML
- Use API for most reliable data
- Check parser._extract_rooms_from_layer()
```

### Common Errors

```python
# Error: No data source available
# Fix: Initialize with either api_key or fez_path
extractor = MeasureSquareExtractor(
    api_key="your_key"  # or fez_path="/path/to/file.fez"
)

# Error: Project ID required
# Fix: Provide project_id when using API
layers = extractor.get_layers(project_id="123")

# Error: Cannot connect to API
# Fix: Check internet connection and API status
# Try local parsing as fallback
```

## 📦 Dependencies

- **requests** - HTTP client for API calls
- **xml.etree.ElementTree** - XML parsing (built-in)
- **zipfile** - FEZ file extraction (built-in)

## 🤝 Getting X-Headers

If you need X-Headers for enhanced API access:

1. Email: integration@measuresquare.com
2. Subject: "API Integration - X-Headers Request"
3. Include:
   - Your company name
   - Your M2 ID (email)
   - Brief description of your use case

They will provide:
- `X-Application`: Your application identifier
- `Secret Key`: For generating HMAC signatures

## 📝 License

This is a tool for extracting data from your own MeasureSquare projects.
Please respect MeasureSquare's terms of service.

## 🆘 Support

- **MeasureSquare API Issues**: integration@measuresquare.com
- **Code Questions**: Check the inline comments in the code
- **Bug Reports**: Review the code and add error handling as needed

## 🎯 Next Steps

1. **Run the tests**: `python test_extractor.py`
2. **Check the examples**: See code comments in `measuresquare_extractor.py`
3. **Build your integration**: Use the hybrid extractor for your workflows
4. **Customize**: Add your own methods for specific needs

## 🔄 Updates

The code includes extensive comments explaining:
- **Why** each design decision was made
- **How** each algorithm works
- **When** to use each approach

Read through the code to learn best practices for Python API clients!
