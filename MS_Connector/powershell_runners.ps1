# PowerShell Runner Scripts
# Save these as .ps1 files and right-click → "Run with PowerShell"

# =============================================================================
# generate_pdf.ps1 - Generate PDF from FEZ file
# =============================================================================

<#
.SYNOPSIS
    Generate PDF from MeasureSquare FEZ file

.DESCRIPTION
    Converts a local FEZ file to PDF using ReportLab

.PARAMETER FezFile
    Path to the FEZ file

.PARAMETER OutputPdf
    Path for output PDF (optional, defaults to same location as FEZ)

.PARAMETER Sections
    Comma-separated list of sections: summary,rooms,products,estimation

.EXAMPLE
    .\generate_pdf.ps1 -FezFile "C:\Projects\B_Down_-_1x1.fez"
    
.EXAMPLE
    .\generate_pdf.ps1 -FezFile "project.fez" -OutputPdf "report.pdf" -Sections "summary,rooms,estimation"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$FezFile,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputPdf = "",
    
    [Parameter(Mandatory=$false)]
    [string]$Sections = "summary,rooms,products,estimation"
)

# Check if file exists
if (-not (Test-Path $FezFile)) {
    Write-Host "ERROR: File not found: $FezFile" -ForegroundColor Red
    exit 1
}

# Set output path if not specified
if ($OutputPdf -eq "") {
    $OutputPdf = [System.IO.Path]::ChangeExtension($FezFile, ".pdf")
}

Write-Host "Generating PDF..." -ForegroundColor Cyan
Write-Host "  Input:  $FezFile" -ForegroundColor Gray
Write-Host "  Output: $OutputPdf" -ForegroundColor Gray
Write-Host "  Sections: $Sections" -ForegroundColor Gray
Write-Host ""

# Run Python script
$pythonScript = @"
from probuildiq_reportlab_generator import ProBuildIQPDFGenerator

sections = '$Sections'.split(',')
sections = [s.strip() for s in sections]

with ProBuildIQPDFGenerator('$FezFile') as generator:
    generator.generate_pdf('$OutputPdf', include_sections=sections)

print('SUCCESS!')
"@

python -c $pythonScript

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "SUCCESS! PDF generated: $OutputPdf" -ForegroundColor Green
    
    # Ask if user wants to open
    $open = Read-Host "Open PDF now? (y/n)"
    if ($open -eq 'y' -or $open -eq 'Y') {
        Start-Process $OutputPdf
    }
} else {
    Write-Host ""
    Write-Host "ERROR: Failed to generate PDF" -ForegroundColor Red
    Write-Host "Make sure you have installed: pip install reportlab" -ForegroundColor Yellow
}

# =============================================================================
# batch_convert.ps1 - Batch convert all FEZ files in a folder
# =============================================================================

<#
.SYNOPSIS
    Batch convert all FEZ files in a folder to PDF

.PARAMETER Folder
    Path to folder containing FEZ files

.PARAMETER Sections
    Sections to include (default: summary,rooms,estimation)

.EXAMPLE
    .\batch_convert.ps1 -Folder "C:\Projects"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$Folder,
    
    [Parameter(Mandatory=$false)]
    [string]$Sections = "summary,rooms,estimation"
)

if (-not (Test-Path $Folder)) {
    Write-Host "ERROR: Folder not found: $Folder" -ForegroundColor Red
    exit 1
}

# Find all FEZ files
$fezFiles = Get-ChildItem -Path $Folder -Filter "*.fez" -Recurse

if ($fezFiles.Count -eq 0) {
    Write-Host "No FEZ files found in: $Folder" -ForegroundColor Yellow
    exit 0
}

Write-Host "Found $($fezFiles.Count) FEZ file(s)" -ForegroundColor Cyan
Write-Host ""

$successful = 0
$failed = @()

foreach ($fez in $fezFiles) {
    $outputPdf = [System.IO.Path]::ChangeExtension($fez.FullName, ".pdf")
    
    Write-Host "Processing: $($fez.Name)" -ForegroundColor Gray
    
    $pythonScript = @"
from probuildiq_reportlab_generator import ProBuildIQPDFGenerator

sections = '$Sections'.split(',')
sections = [s.strip() for s in sections]

try:
    with ProBuildIQPDFGenerator('$($fez.FullName)') as generator:
        generator.generate_pdf('$outputPdf', include_sections=sections)
    print('OK')
except Exception as e:
    print(f'ERROR: {e}')
"@
    
    $result = python -c $pythonScript
    
    if ($result -like "*OK*") {
        Write-Host "  SUCCESS" -ForegroundColor Green
        $successful++
    } else {
        Write-Host "  FAILED: $result" -ForegroundColor Red
        $failed += $fez.Name
    }
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Complete: $successful/$($fezFiles.Count) successful" -ForegroundColor Green

if ($failed.Count -gt 0) {
    Write-Host ""
    Write-Host "Failed files:" -ForegroundColor Red
    foreach ($f in $failed) {
        Write-Host "  - $f" -ForegroundColor Red
    }
}

# =============================================================================
# test_api.ps1 - Test cloud API connection
# =============================================================================

<#
.SYNOPSIS
    Test MeasureSquare Cloud API connection

.PARAMETER ApiKey
    Your API key from cloud.measuresquare.com

.PARAMETER M2Id
    Your M2 ID (email address)

.EXAMPLE
    .\test_api.ps1 -ApiKey "your_key" -M2Id "your.email@company.com"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$ApiKey,
    
    [Parameter(Mandatory=$true)]
    [string]$M2Id
)

Write-Host "Testing API connection..." -ForegroundColor Cyan
Write-Host "  API Key: ********$($ApiKey.Substring($ApiKey.Length - 4))" -ForegroundColor Gray
Write-Host "  M2 ID: $M2Id" -ForegroundColor Gray
Write-Host ""

$pythonScript = @"
from measuresquare_extractor import MeasureSquareAPIClient

try:
    client = MeasureSquareAPIClient('$ApiKey')
    projects = client.get_projects('$M2Id')
    
    print(f'SUCCESS! Found {len(projects)} projects')
    
    if projects:
        print('\nYour projects:')
        for i, proj in enumerate(projects[:5], 1):
            print(f'  {i}. {proj.get(\"Name\", \"Unnamed\")}')
        
        if len(projects) > 5:
            print(f'  ... and {len(projects) - 5} more')
    
except Exception as e:
    print(f'ERROR: {e}')
"@

python -c $pythonScript

# =============================================================================
# USAGE INSTRUCTIONS
# =============================================================================

<#

HOW TO USE THESE POWERSHELL SCRIPTS:

Method 1: Save and Run
----------------------
1. Copy the script you want (e.g., generate_pdf.ps1)
2. Save as a .ps1 file
3. Right-click → "Run with PowerShell"
4. Or in PowerShell: .\generate_pdf.ps1 -FezFile "file.fez"

Method 2: Copy-Paste
--------------------
1. Open PowerShell
2. Navigate to your project folder: cd "C:\path\to\folder"
3. Copy the command and run it

Method 3: Create Shortcuts
---------------------------
1. Right-click desktop → New → Shortcut
2. Target: powershell.exe -File "C:\path\to\generate_pdf.ps1" -FezFile "C:\path\to\file.fez"
3. Now double-click to run!

EXAMPLES:

# Generate PDF with all sections
.\generate_pdf.ps1 -FezFile "B_Down_-_1x1.fez"

# Generate PDF with only specific sections
.\generate_pdf.ps1 -FezFile "project.fez" -Sections "summary,rooms,estimation"

# Batch convert all FEZ files in a folder
.\batch_convert.ps1 -Folder "C:\Projects"

# Test API connection
.\test_api.ps1 -ApiKey "your_api_key" -M2Id "your.email@company.com"

#>
