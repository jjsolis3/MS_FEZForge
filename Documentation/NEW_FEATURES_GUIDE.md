# 🆕 NEW FEATURES GUIDE - Materials Extraction & Project List

## What's New in Easy Runner

You now have a **FULL 12-option menu** with two powerful new features:

### ✅ RESTORED: Full 10-option menu you had before
### ✅ NEW: Option 7 - Extract Materials/Products
### ✅ NEW: Option 8 - Generate Project List with ProjectId

---

## 📋 Complete Menu Structure

```
ProBuildIQ MeasureSquare Tools - Easy Runner

LOCAL FILE OPTIONS:
  1. 📄 Generate PDF from local FEZ file (basic quality)
  2. ✏️  Edit FEZ file (rename rooms, update products)

CLOUD API OPTIONS:
  3. ☁️  Upload FEZ to cloud & get high-quality PDF
  4. 📊 Get all cloud projects (handles 400+)
  5. 🔍 Filter & extract specific cloud projects (with PDF filtering)
  6. 📝 Update cloud project metadata
  7. 📦 Extract materials/products from projects ← NEW!
  8. 📋 Generate project list report (with ProjectId) ← NEW!

OTHER:
  9. 🔌 Test cloud API connection
  10. 📚 Batch convert multiple local FEZ files
  11. ❓ Help & Documentation
  0. 🚪 Exit
```

---

## 🆕 Option 7: Extract Materials/Products from Projects

### What It Does

Extracts detailed material and product information from your cloud projects:
- Product names
- Quantities
- Units (SY, LF, SF, EA)
- Linear lengths
- Net areas
- Waste percentages

### Why This Is Useful

**For Estimating:**
- Get a complete material list across multiple projects
- See what products you're using most
- Calculate total quantities for bulk ordering

**For Purchasing:**
- Export to CSV for your ordering system
- Track material usage by project
- Identify patterns in product usage

**For Reporting:**
- Generate material summaries
- Track inventory needs
- Create purchase orders

### How to Use

#### Via Easy Runner (Interactive):

```bash
python easy_runner.py

# Choose option 7
# Enter project filter (or press Enter for all)
# Choose output format:
#   1. JSON (machine-readable)
#   2. CSV (Excel-friendly)
#   3. Text report (human-readable)
# Enter output filename
# Done!
```

#### Example Session:

```
📦 EXTRACT MATERIALS/PRODUCTS FROM PROJECTS
----------------------------------------------------------------------
Project Filter (press Enter to get all):
  Project name contains: 2024

⏳ Fetching projects...
✅ Found 50 projects

First 10 projects:
  1. 2024-01-10 Apartment A
  2. 2024-01-15 Unit 203
  ...

Extract materials from these 50 projects? (y/n): y

Output format:
  1. JSON (detailed, machine-readable)
  2. CSV (Excel-friendly)
  3. Text report (human-readable)
Choose format (1-3, default=3): 2

Output file name (press Enter for materials_report): 2024_materials.csv

⏳ Extracting materials from 50 projects...
[1/50] 2024-01-10 Apartment A
[2/50] 2024-01-15 Unit 203
...

✅ Complete!
   Extracted 350 materials from 50 projects
   Saved to: 2024_materials.csv
```

### Output Formats

#### 1. JSON Format (materials_report.json)

```json
[
  {
    "project_id": "abc123",
    "project_name": "B Down - 1x1",
    "product_name": "CPTBroadloom#1 12'0\" SY",
    "quantity": "64.33 SY (579.00 SF)",
    "unit": "SY",
    "linear_length": "12'0\"x48'3\"",
    "net_area": "52.01 SY (468.06 SF)",
    "waste": "19.2%"
  },
  ...
]
```

**Use for:** Import into databases, automated processing

#### 2. CSV Format (materials_report.csv)

```csv
project_id,project_name,product_name,quantity,unit,linear_length,net_area,waste
abc123,B Down - 1x1,CPTBroadloom#1 12'0" SY,64.33 SY,SY,12'0"x48'3",52.01 SY,19.2%
abc123,B Down - 1x1,Vinyl Plank 7-1/2" SF,107.86 SF,SF,,78.48 SF,37.4%
...
```

**Use for:** Open in Excel, import into accounting systems

#### 3. Text Format (materials_report.txt)

```
======================================================================
MATERIALS EXTRACTION REPORT
======================================================================

Total Projects: 50
Total Materials: 350
======================================================================

======================================================================
PROJECT: B Down - 1x1
Project ID: abc123
======================================================================

  • CPTBroadloom#1 12'0" SY
    Quantity: 64.33 SY (579.00 SF) SY
    Net Area: 52.01 SY (468.06 SF)
    Linear Length: 12'0"x48'3"
    Waste: 19.2%

  • Vinyl Plank 7-1/2" SF
    Quantity: 107.86 SF (11.98 SY) (2*53.93SF/Box) (29PCs) SF
    Net Area: 78.48 SF (8.72 SY)
    Linear Length: 24'7"
    Waste: 37.4%

  • 3/8 Quarter Round 8" LF
    Quantity: 43.3 LF LF
    Net Area: 41.2 LF
    Waste: 5.3%
...
```

**Use for:** Quick review, printing, email reports

### Python Code Example

```python
from easy_runner import extract_materials_from_projects

# Assuming you have config loaded
config = {
    'api': {
        'api_key': 'your_key',
        'm2_id': 'your_email'
    }
}

extract_materials_from_projects(config)
```

Or directly:

```python
from measuresquare_extractor import MeasureSquareAPIClient
from cloud_api_complete_workflow import CloudAPIWorkflow

workflow = CloudAPIWorkflow(api_key="your_key", m2_id="your_email")
client = MeasureSquareAPIClient("your_key")

# Get all projects
projects = workflow.get_all_projects()

# Extract materials from each
all_materials = []

for project in projects:
    estimation = client.get_estimation(project['ProjectId'])
    
    if estimation and 'Items' in estimation:
        for item in estimation['Items']:
            all_materials.append({
                'project': project['Name'],
                'product': item.get('Description'),
                'quantity': item.get('Usage'),
                'unit': item.get('Unit')
            })

# Save to CSV
import csv
with open('materials.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['project', 'product', 'quantity', 'unit'])
    writer.writeheader()
    writer.writerows(all_materials)
```

---

## 🆕 Option 8: Generate Project List Report (with ProjectId)

### What It Does

Creates a comprehensive list of ALL your projects with their ProjectId for easy identification and reference.

### Why This Is Needed

**The Problem:** You can't use the API without ProjectId, but how do you find the ProjectId?

**The Solution:** Generate a report with ALL projects and their ProjectIds!

**Use Cases:**
- Find ProjectId for a specific project by name
- Get a complete inventory of all projects
- Track when projects were last updated
- Identify archived projects
- Share project list with team members

### How to Use

#### Via Easy Runner (Interactive):

```bash
python easy_runner.py

# Choose option 8
# Enter filter (or press Enter for all)
# Choose to include archived projects
# Choose output format:
#   1. JSON
#   2. CSV
#   3. Text report
#   4. Markdown table
# Enter output filename
# Done!
```

#### Example Session:

```
📋 GENERATE PROJECT LIST REPORT (WITH PROJECT ID)
----------------------------------------------------------------------
Filter options (press Enter to skip):
  Project name contains: [Press Enter]
  Include archived projects? (y/n, default=n): n

⏳ Fetching projects...
✅ Found 400 projects

Output format:
  1. JSON (detailed, machine-readable)
  2. CSV (Excel-friendly)
  3. Text report (human-readable)
  4. Markdown table (documentation-friendly)
Choose format (1-4, default=3): 3

Output file name (press Enter for project_list): my_projects.txt

⏳ Generating report...

✅ Complete!
   Report generated: my_projects.txt
   Total projects: 400

First 5 projects:
  1. B Down - 1x1
     ProjectId: abc123xyz789
  2. 2x1 Topanga 762 SF
     ProjectId: def456uvw012
  ...
```

### Output Formats

#### 1. JSON Format (project_list.json)

```json
[
  {
    "ProjectId": "abc123xyz789",
    "Name": "B Down - 1x1",
    "Revision": 1,
    "OwnerM2Id": "mslfc.mgr@seamlessflooring.com",
    "LastUpdatedOn": 1702339200,
    "Size": 112873,
    "IsArchived": false,
    "ApplicationType": "FloorCovering",
    "Tags": ["apartment", "vinyl"]
  },
  ...
]
```

**Use for:** Import into databases, API automation

#### 2. CSV Format (project_list.csv)

```csv
ProjectId,Name,Revision,OwnerM2Id,LastUpdatedOn,Size,IsArchived
abc123xyz789,B Down - 1x1,1,mslfc.mgr@seamlessflooring.com,1702339200,112873,False
def456uvw012,2x1 Topanga 762 SF,1,mslfc.mgr@seamlessflooring.com,1702425600,127459,False
...
```

**Use for:** Excel, filtering, sorting

#### 3. Text Format (project_list.txt)

```
======================================================================
PROJECT LIST REPORT
======================================================================

Generated: 2024-12-10 18:30:45
M2 ID: mslfc.mgr@seamlessflooring.com
Total Projects: 400
======================================================================

======================================================================
#1: B Down - 1x1
======================================================================
Project ID: abc123xyz789
Revision: 1
Owner: mslfc.mgr@seamlessflooring.com
Last Updated: 2024-12-10 17:48:00
File Size: 110.23 KB

======================================================================
#2: 2x1 Topanga 762 SF
======================================================================
Project ID: def456uvw012
Revision: 1
Owner: mslfc.mgr@seamlessflooring.com
Last Updated: 2025-06-17 15:04:00
File Size: 123.00 KB

...
```

**Use for:** Quick reference, printing

#### 4. Markdown Format (project_list.md)

```markdown
# Project List Report

Generated: 2024-12-10 18:30:45

Total Projects: 400

## Projects

| # | Project Name | Project ID | Updated | Archived |
|---|--------------|------------|---------|----------|
| 1 | B Down - 1x1 | `abc123xyz789` | 2024-12-10 | |
| 2 | 2x1 Topanga 762 SF | `def456uvw012` | 2025-06-17 | |
| 3 | 3x2 Vista Del Mar 1125 SF 2 | `ghi789rst345` | 2025-02-06 | |
...
```

**Use for:** Documentation, GitHub, wikis

### How to Find ProjectId for a Specific Project

**Step 1:** Generate report
```bash
python easy_runner.py
# Choose option 8
# Press Enter for all projects
# Choose format 3 (text)
```

**Step 2:** Open the report file
```bash
notepad project_list.txt  # Windows
open project_list.txt     # Mac
```

**Step 3:** Search for your project
- Press Ctrl+F (Windows) or Cmd+F (Mac)
- Type project name: "B Down"
- Find the ProjectId listed below

**Example:**
```
======================================================================
#1: B Down - 1x1
======================================================================
Project ID: abc123xyz789   ← THIS IS WHAT YOU NEED!
...
```

**Step 4:** Use the ProjectId
```python
client.download_pdf("abc123xyz789", "B_Down.pdf")
```

---

## 🔧 Real-World Use Cases

### Use Case 1: Material Ordering

**Goal:** Order materials for all 2024 projects

```bash
# Step 1: Extract materials
python easy_runner.py
→ Option 7
→ Filter: "2024"
→ Format: CSV
→ Output: 2024_materials.csv

# Step 2: Open in Excel
# Step 3: Pivot table to sum quantities
# Step 4: Place bulk order
```

### Use Case 2: Find ProjectId for Updates

**Goal:** Update metadata for "B Down - 1x1"

```bash
# Step 1: Generate project list
python easy_runner.py
→ Option 8
→ Format: Text
→ Output: projects.txt

# Step 2: Search for "B Down"
# Find ProjectId: abc123xyz789

# Step 3: Update project
python easy_runner.py
→ Option 6
→ Enter ProjectId: abc123xyz789
→ Update fields
```

### Use Case 3: Quarterly Reporting

**Goal:** Generate quarterly material usage report

```bash
# Step 1: Extract materials from Q4 projects
python easy_runner.py
→ Option 7
→ Filter: "2024-10" OR "2024-11" OR "2024-12"
→ Format: Text
→ Output: Q4_2024_materials.txt

# Step 2: Generate project list
python easy_runner.py
→ Option 8
→ Format: Markdown
→ Output: Q4_2024_projects.md

# Step 3: Combine into quarterly report
# Copy both files into report document
```

### Use Case 4: Inventory Management

**Goal:** Track what's currently in use across all projects

```python
from measuresquare_extractor import MeasureSquareAPIClient
from cloud_api_complete_workflow import CloudAPIWorkflow
from collections import defaultdict

workflow = CloudAPIWorkflow(api_key="your_key", m2_id="your_email")
client = MeasureSquareAPIClient("your_key")

# Get all active projects
all_projects = workflow.get_all_projects()
active_projects = [p for p in all_projects if not p.get('IsArchived', False)]

# Track material totals
material_totals = defaultdict(float)

for project in active_projects:
    estimation = client.get_estimation(project['ProjectId'])
    
    if estimation and 'Items' in estimation:
        for item in estimation['Items']:
            product = item.get('Description', 'Unknown')
            quantity = item.get('Usage', '0')
            
            # Parse quantity (e.g., "64.33 SY" → 64.33)
            try:
                qty_value = float(quantity.split()[0])
                material_totals[product] += qty_value
            except:
                pass

# Print inventory needs
print("Current Inventory Needs:")
print("="*70)
for product, total in sorted(material_totals.items(), key=lambda x: x[1], reverse=True):
    print(f"{product}: {total:.2f}")
```

---

## 📊 Output File Examples

### Example: 2024_materials.csv (opened in Excel)

| project_id | project_name | product_name | quantity | unit |
|------------|-------------|--------------|----------|------|
| abc123 | B Down - 1x1 | CPTBroadloom#1 | 64.33 | SY |
| abc123 | B Down - 1x1 | Vinyl Plank | 107.86 | SF |
| def456 | Unit 203 | Vinyl Plank | 250.00 | SF |

**Excel Pivot Table:**
- Rows: product_name
- Values: Sum of quantity
- Result: Total materials needed across all projects

### Example: project_list.txt (opened in Notepad)

Easy to search with Ctrl+F to find any project and its ProjectId!

---

## 💡 Tips and Best Practices

### For Materials Extraction:

1. **Use CSV for Excel:** Easy to sort, filter, create pivot tables
2. **Filter by date:** Extract only recent projects for current inventory
3. **Save monthly:** Create monthly material reports for tracking
4. **Combine with cost data:** Add pricing in Excel for cost analysis

### For Project Lists:

1. **Generate quarterly:** Keep updated list of all projects
2. **Use Markdown for docs:** Great for team wikis or GitHub
3. **Search feature:** Text format is easiest to search (Ctrl+F)
4. **Include ProjectId in notes:** Reference ProjectId when discussing projects

### General:

1. **Backup regularly:** Export lists before making bulk changes
2. **Use filters wisely:** Filter by name, date, or tags for targeted reports
3. **Combine features:** Generate list → Find ProjectId → Extract materials
4. **Share with team:** Export to CSV/Markdown for easy sharing

---

## 🚀 Quick Start Commands

### Extract All Materials:
```bash
python easy_runner.py
# 7 → Enter → y → 2 → materials.csv → Done!
```

### Generate Project List:
```bash
python easy_runner.py
# 8 → Enter → n → 3 → projects.txt → Done!
```

### Find Specific Project:
```bash
python easy_runner.py
# 8 → apartment → n → 3 → apartments.txt
# Open apartments.txt and search for your project
```

---

## ✅ Summary

**Option 7 - Extract Materials:**
- Get complete material lists
- Export to CSV for Excel
- Perfect for purchasing and estimating

**Option 8 - Generate Project List:**
- Find ProjectId for any project
- Get complete project inventory
- Export to multiple formats

**Together:** Complete project and material tracking system!

Your workflow is now:
1. Generate project list (find ProjectIds)
2. Extract materials (get quantities)
3. Use other options (update, filter, download PDFs)
4. All automated! 🎉
