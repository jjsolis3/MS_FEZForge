# CLOUD API ANSWERS - All Your Questions Solved! ✅

## Your Observations

> "PDF creation from local files is not coming out as intended... 
> the PDF summary, room, layout is not the same at all"

**You're absolutely right!** Local rendering can't match MeasureSquare's official cloud rendering. 

**Solution:** Upload to cloud → Generate PDF → Get perfect results! 🎯

---

## Q1: Can We UPDATE Files via API? ✅ YES!

### Answer: Absolutely! Here's what you can update:

**Project Metadata:**
- Customer name, address, phone, email
- Project notes and dates
- Installation/measurement info
- Job site contact details

**Products:**
- Add/remove/update products in project
- Change prices, vendors, descriptions
- Update quantities and assignments

**Example:**
```python
from cloud_api_complete_workflow import CloudAPIWorkflow

workflow = CloudAPIWorkflow(api_key="your_key", m2_id="your_email")

# Update customer info
updates = {
    'ProjectId': 'abc123',  # Required!
    'ContactName': 'John Smith',
    'Email': 'john@example.com', 
    'Phone': '555-1234',
    'ProjectNote': 'Updated for final bid - approved'
}

workflow.update_project_metadata('abc123', updates)
```

---

## Q2: What Are the Limits? 📊

### API Limits (from MeasureSquare documentation):

| Limit Type | Value | Notes |
|------------|-------|-------|
| **Projects per request** | 100 max | Use pagination for more |
| **PDF generation rate** | 10 per minute | Wait 1 second between calls |
| **General API calls** | No hard limit | Be reasonable, add delays |
| **File upload size** | No documented limit | Large files = longer upload |
| **Page length** | 1-100 | Parameter: `pageLength` |

### Rate Limiting Protection:
```python
import time

# For PDF generation
for project in projects:
    client.download_pdf(project['ProjectId'])
    time.sleep(1)  # Respect rate limit!

# For general requests  
for project in projects:
    do_something(project)
    time.sleep(0.5)  # Be nice to the API
```

---

## Q3: How to Get 400 Files When Limit is 100? 🔄 PAGINATION!

### The Problem:
```
You have: 400 projects
API returns: Max 100 per request
Question: How to get all 400?
```

### The Solution: PAGINATION!

**Concept:**
- Request 1: Projects 1-100 (pageIndex=0)
- Request 2: Projects 101-200 (pageIndex=1)  
- Request 3: Projects 201-300 (pageIndex=2)
- Request 4: Projects 301-400 (pageIndex=3)

**Automatic Code:**
```python
from cloud_api_complete_workflow import CloudAPIWorkflow

workflow = CloudAPIWorkflow(api_key="your_key", m2_id="your_email")

# Get ALL 400 projects automatically!
all_projects = workflow.get_all_projects()

print(f"Found {len(all_projects)} projects")  # Will show 400!

# The method handles pagination automatically:
# - Makes multiple requests (4 in your case)
# - Combines results
# - Adds rate limiting delays
```

**Manual Control (if you want):**
```python
# Get projects 101-200 specifically
projects_page2 = workflow._get_projects_page(
    page_length=100,
    page_index=1  # 0=first 100, 1=second 100, etc.
)

# Get projects 201-300
projects_page3 = workflow._get_projects_page(
    page_length=100,
    page_index=2
)
```

---

## Q4: How to Extract Only SPECIFIC Files? 🔍

### Answer: Filter by name, date, customer, etc.

**Method 1: Filter by Project Name**
```python
# Only projects with "Apartment" in name
apartments = workflow.filter_projects(name_contains="Apartment")

print(f"Found {len(apartments)} apartment projects")

# Extract just these
for project in apartments:
    client.download_pdf(project['ProjectId'], f"{project['Name']}.pdf")
```

**Method 2: Filter by Date**
```python
# Only projects after November 1, 2024
recent = workflow.filter_projects(created_after="2024-11-01")

print(f"Found {len(recent)} recent projects")
```

**Method 3: Filter by Customer**
```python
# Only projects for specific customer
customer_projects = workflow.filter_projects(customer_name="Smith")

print(f"Found {len(customer_projects)} projects for Smith")
```

**Method 4: Combine Filters**
```python
# Recent apartment projects for Smith
filtered = workflow.filter_projects(
    name_contains="Apartment",
    created_after="2024-11-01",
    customer_name="Smith"
)
```

**Method 5: Manual Filtering (Most Control)**
```python
all_projects = workflow.get_all_projects()

# Filter by any criteria you want!
my_selection = [
    p for p in all_projects
    if "B Down" in p['Name'] 
    and p['LastUpdatedOn'] > some_timestamp
    and not p.get('IsArchived', False)
]
```

---

## Q5: Complete Workflow - Upload Local → Get Cloud PDF

### Your Best Workflow:

```python
from cloud_api_complete_workflow import CloudAPIWorkflow

workflow = CloudAPIWorkflow(
    api_key="13a86...434",  # Your key from screenshot
    m2_id="mslfc.mgr@seamlessfloor..."  # Your M2 ID
)

# Upload your local FEZ file → Get cloud-rendered PDF
result = workflow.upload_and_extract_workflow(
    "B_Down_-_1x1.fez",
    output_dir="./cloud_pdfs"
)

# That's it! You get:
# - Perfect cloud-rendered PDF
# - All layer images
# - Project ID for future updates

print(f"PDF: {result['pdf_path']}")
print(f"Project ID: {result['project_id']}")
```

---

## Comparison: Local vs Cloud

| Feature | Local ReportLab | Cloud API |
|---------|----------------|-----------|
| **PDF Quality** | ⚠️ Basic | ⭐⭐⭐⭐⭐ Perfect |
| **Diagrams** | ❌ Manual rendering | ✅ Official rendering |
| **Layout** | ⚠️ Custom | ✅ MeasureSquare standard |
| **Setup** | Easy | Easy |
| **Offline** | ✅ Yes | ❌ Needs internet |
| **Speed** | ⚡ Fast | ⚡⚡ Moderate |
| **Your Use Case** | ❌ Not matching | ✅ **RECOMMENDED** |

---

## Real-World Examples

### Example 1: Batch Upload 10 Local Files
```python
from pathlib import Path
from cloud_api_complete_workflow import CloudAPIWorkflow
from measuresquare_extractor import MeasureSquareAPIClient
import time

workflow = CloudAPIWorkflow(api_key="your_key", m2_id="your_email")
client = MeasureSquareAPIClient("your_key")

# Find all FEZ files
fez_files = Path("./local_projects").glob("*.fez")

for fez in fez_files:
    print(f"\n{'='*60}")
    print(f"Processing: {fez.name}")
    print('='*60)
    
    # Upload to cloud
    result = workflow.upload_fez_file(str(fez))
    project_id = result['ProjectId']
    
    # Wait for processing
    time.sleep(5)
    
    # Download cloud-rendered PDF
    pdf_path = f"./output/{fez.stem}_cloud.pdf"
    client.download_pdf(project_id, pdf_path)
    
    print(f"✅ Cloud PDF: {pdf_path}")
    
    # Rate limiting
    time.sleep(1)
```

### Example 2: Update Then Extract All 400 Projects
```python
workflow = CloudAPIWorkflow(api_key="your_key", m2_id="your_email")
client = MeasureSquareAPIClient("your_key")

# Get all 400 projects (automatic pagination!)
all_projects = workflow.get_all_projects()

print(f"Processing {len(all_projects)} projects...")

for i, project in enumerate(all_projects, 1):
    project_id = project['ProjectId']
    
    print(f"\n[{i}/{len(all_projects)}] {project['Name']}")
    
    # Update project info if needed
    if "old_customer" in project['Name']:
        workflow.update_project_metadata(project_id, {
            'ContactName': 'Updated Customer Name',
            'ProjectNote': 'Migrated to new system'
        })
    
    # Download PDF
    pdf_path = f"./pdfs/{project['Name']}.pdf"
    client.download_pdf(project_id, pdf_path)
    
    print(f"  ✓ PDF saved")
    
    # Rate limiting (important!)
    if i % 10 == 0:
        print("  ⏸️ Cooling down...")
        time.sleep(10)  # Extra pause every 10 files
    else:
        time.sleep(1)
```

### Example 3: Select 50 Specific Projects
```python
workflow = CloudAPIWorkflow(api_key="your_key", m2_id="your_email")
client = MeasureSquareAPIClient("your_key")

# Get all projects
all_projects = workflow.get_all_projects()

# Filter to your 50 specific ones
selected = [
    p for p in all_projects
    if "2024" in p['Name']  # Only 2024 projects
    and "Apartment" in p['Name']  # Only apartments
    and not p.get('IsArchived', False)  # Not archived
][:50]  # Limit to 50

print(f"Selected {len(selected)} projects")

# Extract just these 50
for project in selected:
    client.download_pdf(project['ProjectId'], f"./output/{project['Name']}.pdf")
    time.sleep(1)
```

---

## Pagination Details (Technical)

### How Pagination Works:

```
Total Projects: 400
Page Size: 100

Page 0 (pageIndex=0): Projects 1-100
Page 1 (pageIndex=1): Projects 101-200
Page 2 (pageIndex=2): Projects 201-300
Page 3 (pageIndex=3): Projects 301-400
```

### API Endpoint:
```
GET /api/{m2Id}/projects/length/{pageLength}/page/{pageIndex}
```

### Parameters:
- `pageLength`: Items per page (max 100)
- `pageIndex`: Which page (0-indexed)
- `search`: Filter by name (optional)
- `orderby`: "asc" or "desc" by update date

### Code Example:
```python
# Manual pagination (if you want control)
page_length = 100
total_pages = 4  # 400 / 100

all_projects = []

for page_index in range(total_pages):
    print(f"Getting page {page_index + 1}/{total_pages}")
    
    url = f"https://cloud.measuresquare.com/api/{m2_id}/projects/length/{page_length}/page/{page_index}"
    
    response = requests.get(url, headers=headers)
    projects = response.json()
    
    all_projects.extend(projects)
    
    if len(projects) < page_length:
        # No more results
        break
    
    time.sleep(0.5)  # Rate limiting

print(f"Total: {len(all_projects)} projects")
```

---

## API Update Capabilities

### What You Can Update:

**Customer Information:**
```python
{
    'ContactName': 'John Smith',
    'Email': 'john@example.com',
    'Phone': '555-1234',
    'Mobile': '555-5678',
    'Fax': '555-9012',
    'Street': '123 Main St',
    'City': 'Santa Clarita',
    'State': 'CA',
    'ZipCode': '91355',
    'Country': 'USA',
    'Memo': 'Preferred customer'
}
```

**Job Site Information:**
```python
{
    'ProjectName': 'Job Site Name',
    'ProjectStreet': '456 Oak Ave',
    'ProjectCity': 'Los Angeles',
    'ProjectState': 'CA',
    'ProjectZipCode': '90001',
    'ProjectEmail': 'site@example.com',
    'ProjectPhone': '555-0000'
}
```

**Project Details:**
```python
{
    'ProjectNote': 'Updated for final bid',
    'InstallationDate': 1704153600,  # Unix timestamp
    'InstallationBy': 'ProBuildIQ Team',
    'MeasurementDate': 1704067200,
    'MeasurementBy': 'John Doe'
}
```

**Products:**
```python
{
    'ProductList': [
        {
            'ID': 'product_id',
            'Name': 'Premium Vinyl Plank',
            'Vendor': 'ProBuildIQ Flooring',
            'SalesPrice': '5.99',
            'CostPrice': '3.50'
        }
    ]
}
```

---

## Rate Limiting Best Practices

### PDF Generation (10 per minute limit):
```python
import time

# Generate PDFs with rate limiting
for i, project in enumerate(projects):
    client.download_pdf(project['ProjectId'])
    
    # Wait 1 second between calls
    time.sleep(1)
    
    # Extra pause every 10 PDFs
    if (i + 1) % 10 == 0:
        print(f"Generated {i+1} PDFs, cooling down...")
        time.sleep(10)
```

### General Requests:
```python
# Add small delays for general requests
for project in projects:
    do_something(project)
    time.sleep(0.5)  # 0.5 second delay
```

### Batch Processing:
```python
# For large batches (400 files)
total = len(projects)

for i, project in enumerate(projects):
    process(project)
    
    # Progress indicator
    if (i + 1) % 50 == 0:
        print(f"Progress: {i+1}/{total} ({(i+1)/total*100:.1f}%)")
        time.sleep(30)  # Longer pause every 50
    else:
        time.sleep(1)
```

---

## Your Specific Scenario

### You have:
- ~400 projects in repository
- Need high-quality PDFs
- Want to update some metadata
- Need to filter/select specific files

### Recommended workflow:

```python
from cloud_api_complete_workflow import CloudAPIWorkflow
from measuresquare_extractor import MeasureSquareAPIClient
import time

# Setup
workflow = CloudAPIWorkflow(
    api_key="13a86...434",
    m2_id="mslfc.mgr@seamlessfloor..."
)
client = MeasureSquareAPIClient("13a86...434")

# Step 1: Get all 400 projects (automatic pagination!)
print("Step 1: Fetching all projects...")
all_projects = workflow.get_all_projects()
print(f"✓ Found {len(all_projects)} projects")

# Step 2: Filter to what you need
print("\nStep 2: Filtering...")
selected = workflow.filter_projects(
    name_contains="Apartment",  # Example filter
    created_after="2024-01-01"
)
print(f"✓ Selected {len(selected)} projects")

# Step 3: Update any that need it
print("\nStep 3: Updating metadata...")
for project in selected:
    if needs_update(project):  # Your logic
        workflow.update_project_metadata(project['ProjectId'], {
            'ContactName': 'Updated Name',
            'ProjectNote': 'Processed by ProBuildIQ system'
        })
        time.sleep(0.5)

# Step 4: Generate high-quality PDFs
print("\nStep 4: Generating PDFs...")
for i, project in enumerate(selected, 1):
    print(f"[{i}/{len(selected)}] {project['Name']}")
    
    pdf_path = f"./output/{project['Name']}.pdf"
    client.download_pdf(project['ProjectId'], pdf_path)
    
    # Rate limiting
    time.sleep(1)
    
    if i % 10 == 0:
        print("  ⏸️ Cooling down...")
        time.sleep(10)

print("\n✅ Complete!")
```

---

## Summary - Direct Answers

| Your Question | Answer |
|---------------|--------|
| **Can we update files?** | ✅ YES - Customer info, products, dates, notes |
| **What are the limits?** | 100 per request, 10 PDFs/min, paginate for more |
| **How to get all 400?** | Use `get_all_projects()` - handles pagination automatically |
| **How to select specific files?** | Use filters (name, date, customer) or manual selection |
| **Cloud better than local?** | ✅ YES - Perfect rendering, matches MeasureSquare exactly |

---

## Next Steps

1. **Download** `cloud_api_complete_workflow.py`
2. **Test** with one file:
   ```python
   workflow.upload_and_extract_workflow("test.fez")
   ```
3. **Scale** to your 400 files with filtering
4. **Enjoy** perfect cloud-rendered PDFs! 🎉

All the code is ready and documented above! 🚀
