# HOW TO RUN THE PROGRAMS - Complete Guide

## 🚀 Quick Answer

Yes, you can run with PowerShell (or Command Prompt)! Here's the basic format:

```powershell
python script_name.py
```

But let me show you the EASY way and the detailed way...

---

## 📋 Three Ways to Run (Easiest to Most Control)

### 🥇 METHOD 1: Double-Click (Easiest!)

**Step 1:** Create a simple runner script

I'll create this for you below - just save it as `run_pdf_generator.py`

**Step 2:** Double-click the file

That's it! The program runs and asks you what to do.

---

### 🥈 METHOD 2: PowerShell with Parameters

**Step 1:** Open PowerShell in your project folder
- Right-click folder → "Open in Terminal" (Windows 11)
- Or: Shift + Right-click → "Open PowerShell window here" (Windows 10)

**Step 2:** Run the command:

```powershell
# Generate PDF from FEZ file
python probuildiq_reportlab_generator.py "C:\path\to\your\file.fez" "output.pdf"

# Or use the test script
python test_extractor.py
```

---

### 🥉 METHOD 3: Import in Your Own Script

```python
# In your own script
from probuildiq_reportlab_generator import ProBuildIQPDFGenerator

# Your custom code here
```

---

## 🎯 RECOMMENDED: Easy Runner Scripts

---

## 🎯 EASIEST METHOD: Double-Click Runner

I've created `easy_runner.py` - just double-click it!

**What it does:**
- Interactive menu (no typing paths!)
- Drag-and-drop file support
- Step-by-step guidance
- No parameters needed

**How to use:**
1. Double-click `easy_runner.py`
2. Choose what you want to do from the menu
3. Follow the prompts

That's it! Perfect for beginners.

---

## 💻 PowerShell/Command Prompt Methods

### Method 1: No Parameters (Interactive)

```powershell
# Navigate to the folder
cd "C:\path\to\ProBuildIQ_Tools"

# Run the easy runner
python easy_runner.py
```

Then follow the menu!

---

### Method 2: With Parameters (Advanced)

#### Generate PDF from FEZ:
```powershell
python probuildiq_reportlab_generator.py "path\to\file.fez" "output.pdf"
```

**Example:**
```powershell
python probuildiq_reportlab_generator.py "G:\Shared drives\SEAMLESS FLOORING SALES\B_Down_-_1x1.fez" "B_Down_Report.pdf"
```

#### Edit FEZ file:
```powershell
python probuildiq_fez_editor.py "path\to\file.fez"
```

#### Test API:
```powershell
python test_extractor.py
```

---

### Method 3: Import in Your Own Script

```python
# Create your own script: my_workflow.py
from probuildiq_reportlab_generator import ProBuildIQPDFGenerator

# Your custom logic
fez_file = "B_Down_-_1x1.fez"

with ProBuildIQPDFGenerator(fez_file) as gen:
    gen.generate_pdf("output.pdf")

print("Done!")
```

Then run:
```powershell
python my_workflow.py
```

---

## 🪟 Windows Batch File (Double-Click)

Create a file called `generate_pdf.bat`:

```batch
@echo off
echo ProBuildIQ PDF Generator
echo ========================
echo.

REM Set your default paths here
set FEZ_FILE=G:\Shared drives\SEAMLESS FLOORING SALES\B_Down_-_1x1.fez
set OUTPUT_PDF=B_Down_Report.pdf

echo Generating PDF...
echo   Input: %FEZ_FILE%
echo   Output: %OUTPUT_PDF%
echo.

python probuildiq_reportlab_generator.py "%FEZ_FILE%" "%OUTPUT_PDF%"

echo.
echo Done!
pause
```

**How to use:**
1. Edit the paths in the batch file
2. Double-click the .bat file
3. PDF generates automatically!

---

## 📂 Drag-and-Drop Method (Windows)

Create `drag_and_drop_pdf.bat`:

```batch
@echo off
echo Generating PDF from: %1
echo.

python probuildiq_reportlab_generator.py %1

echo.
echo Done! PDF saved in same folder.
pause
```

**How to use:**
1. Drag a FEZ file onto the batch file
2. PDF generates automatically!

---

## 🔧 PowerShell Scripts (Advanced Users)

I've created `powershell_runners.ps1` with ready-to-use scripts:

### Generate PDF:
```powershell
.\generate_pdf.ps1 -FezFile "project.fez" -OutputPdf "report.pdf"
```

### Batch Convert Folder:
```powershell
.\batch_convert.ps1 -Folder "C:\Projects"
```

### Test API:
```powershell
.\test_api.ps1 -ApiKey "your_key" -M2Id "your.email@company.com"
```

**To enable PowerShell scripts:**
```powershell
# Run once as Administrator
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 🐍 Python Module Import (Programmers)

If you want to use these tools in your own code:

```python
# Import the modules
from probuildiq_reportlab_generator import ProBuildIQPDFGenerator
from probuildiq_fez_editor import FEZFileEditor
from measuresquare_extractor import MeasureSquareAPIClient

# Use them in your code
with ProBuildIQPDFGenerator("file.fez") as gen:
    gen.generate_pdf("output.pdf", 
                     include_sections=['summary', 'rooms'])
```

---

## 📝 Common Examples

### Example 1: Simple PDF Generation
```powershell
# Open PowerShell in the folder with your FEZ file
# Then run:
python probuildiq_reportlab_generator.py "B_Down_-_1x1.fez"

# PDF saves as B_Down_-_1x1.pdf
```

### Example 2: Custom Sections (No 3D)
```python
# Create: my_pdf.py
from probuildiq_reportlab_generator import ProBuildIQPDFGenerator

with ProBuildIQPDFGenerator("project.fez") as gen:
    gen.generate_pdf(
        "installer_report.pdf",
        include_sections=['summary', 'rooms', 'estimation']  # No products!
    )
```

Run: `python my_pdf.py`

### Example 3: Clean Names Then Generate PDF
```python
# Create: cleanup_and_generate.py
from probuildiq_fez_editor import FEZFileEditor
from probuildiq_reportlab_generator import ProBuildIQPDFGenerator

# Step 1: Clean names
with FEZFileEditor("B_Down_-_1x1.fez") as editor:
    editor.batch_rename_rooms({
        'Primary Bdrm': 'Master Bedroom',
        'MBR CL': 'Master Bedroom Closet'
    })
    clean_fez = editor.save()

# Step 2: Generate PDF
with ProBuildIQPDFGenerator(clean_fez) as gen:
    gen.generate_pdf("B_Down_Report.pdf")

print("Done!")
```

Run: `python cleanup_and_generate.py`

### Example 4: Process All Files in Folder
```python
# Create: batch_process.py
from pathlib import Path
from probuildiq_reportlab_generator import ProBuildIQPDFGenerator

# Find all FEZ files
folder = Path("G:/Shared drives/SEAMLESS FLOORING SALES")
fez_files = list(folder.glob("**/*.fez"))

print(f"Found {len(fez_files)} FEZ files")

for fez in fez_files:
    print(f"Processing: {fez.name}")
    output = fez.with_suffix('.pdf')
    
    try:
        with ProBuildIQPDFGenerator(str(fez)) as gen:
            gen.generate_pdf(str(output))
        print(f"  ✓ Success")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

print("All done!")
```

Run: `python batch_process.py`

---

## ❓ Troubleshooting

### "Python is not recognized"
**Problem:** Python not in PATH
**Solution:**
```powershell
# Find Python
where python

# If not found, reinstall Python and check "Add to PATH"
```

### "No module named 'reportlab'"
**Problem:** ReportLab not installed
**Solution:**
```powershell
pip install reportlab
```

### "File not found"
**Problem:** Wrong path or quotes missing
**Solution:**
```powershell
# Use quotes for paths with spaces
python script.py "C:\My Documents\file.fez"

# Or use forward slashes
python script.py "C:/My Documents/file.fez"
```

### "Permission denied"
**Problem:** File is open in another program
**Solution:** Close MeasureSquare and try again

### PowerShell script won't run
**Problem:** Execution policy
**Solution:**
```powershell
# Run as Administrator
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 🎓 Learning Path

### Beginner (Just want PDFs):
1. Use `easy_runner.py` (double-click)
2. Or use drag-and-drop batch file
3. Done!

### Intermediate (Want control):
1. Learn basic PowerShell commands
2. Use PowerShell scripts with parameters
3. Customize sections

### Advanced (Integration):
1. Import modules in your code
2. Create custom workflows
3. Automate everything

---

## 📋 Quick Reference Card

| Task | Command |
|------|---------|
| **Easy menu** | `python easy_runner.py` |
| **Generate PDF** | `python probuildiq_reportlab_generator.py "file.fez"` |
| **Edit FEZ** | `python probuildiq_fez_editor.py "file.fez"` |
| **Test API** | `python test_extractor.py` |
| **Help** | `python easy_runner.py` → Option 5 |

---

## 💡 Pro Tips

1. **Drag and Drop**: Most scripts support dragging files into the console
2. **Tab Completion**: In PowerShell, press Tab to autocomplete paths
3. **Recent Files**: Press ↑ in PowerShell to see recent commands
4. **Batch Processing**: Use the batch_convert option for multiple files
5. **Save Time**: Create desktop shortcuts to your favorite scripts

---

## 🎯 Recommended Workflow

**For one-time use:**
- Double-click `easy_runner.py`
- Choose Option 1
- Drag file in
- Done!

**For repeated use:**
- Create a batch file with your settings
- Double-click it whenever needed
- Or use PowerShell scripts

**For automation:**
- Create Python scripts
- Schedule with Windows Task Scheduler
- Or call from other programs

---

## 🆘 Still Stuck?

1. Check `PDF_GENERATION_COMPLETE_GUIDE.md`
2. Read `QUICK_START.md`
3. Look at the example code in the files
4. All code has comments explaining what it does!

Remember: The `easy_runner.py` is the simplest way - try it first! 🚀
