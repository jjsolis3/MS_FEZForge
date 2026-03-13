"""
ProBuildIQ PDF Filter - Remove Unwanted Pages
==============================================

This module downloads PDFs from MeasureSquare Cloud API and removes
unwanted pages like:
- Blank 3D rendering pages
- Empty pages
- Specific page numbers

Why this is needed:
- MeasureSquare PDFs include 3D rendering pages that show nothing
- Pages 4, 8, 10 are often blank because walls hide the floor
- We only need 2D layouts and summaries for installers

How it works:
- Downloads full PDF from cloud API
- Analyzes each page (blank detection)
- Removes unwanted pages
- Saves filtered PDF
"""

import io
from pathlib import Path
from typing import List, Set, Optional, Dict
from PyPDF2 import PdfReader, PdfWriter
import requests


class PDFPageFilter:
    """
    Filter and remove unwanted pages from MeasureSquare PDFs
    
    This class provides intelligent page filtering to remove:
    - Blank pages (3D rendering pages that show nothing)
    - Specific page numbers
    - Pages matching certain patterns
    
    Why PyPDF2:
    PyPDF2 is a pure-Python library for PDF manipulation. We use it to:
    1. Read the original PDF
    2. Detect blank or nearly-blank pages
    3. Copy only the wanted pages to a new PDF
    4. Save the filtered result
    
    This is better than trying to tell the API what to generate because:
    - We get the official cloud rendering (perfect quality)
    - Then we clean it up to our needs
    - More flexible than API parameters
    """
    
    def __init__(self):
        """Initialize the PDF filter"""
        self.blank_threshold = 1000  # Bytes - pages smaller than this are likely blank
    
    def filter_pdf(self, input_pdf_path: str, output_pdf_path: str,
                   remove_options: Dict[str, bool]) -> Dict[str, any]:
        """
        Filter a PDF based on user options
        
        Args:
            input_pdf_path: Path to the original PDF
            output_pdf_path: Path to save the filtered PDF
            remove_options: Dict of what to remove:
                {
                    'blank_pages': True/False,
                    'page_numbers': [4, 8, 10],  # Specific pages to remove
                    'pages_with_text': ['3D', 'Powered by'],  # Remove pages containing this text
                }
        
        Returns:
            Dict with filtering results:
                {
                    'original_pages': 10,
                    'removed_pages': 3,
                    'final_pages': 7,
                    'removed_page_numbers': [4, 8, 10],
                    'output_path': 'filtered.pdf'
                }
        
        Example:
            filter = PDFPageFilter()
            result = filter.filter_pdf(
                "original.pdf",
                "filtered.pdf",
                {
                    'blank_pages': True,
                    'page_numbers': [4, 8, 10]
                }
            )
            print(f"Removed {result['removed_pages']} pages")
        """
        print(f"📄 Filtering PDF: {Path(input_pdf_path).name}")
        print(f"   Options: {remove_options}")
        
        # Read the original PDF
        with open(input_pdf_path, 'rb') as file:
            reader = PdfReader(file)
            original_page_count = len(reader.pages)
            
            print(f"   Original: {original_page_count} pages")
            
            # Determine which pages to keep
            pages_to_remove = self._identify_pages_to_remove(
                reader, 
                remove_options
            )
            
            # Create a new PDF with only the pages we want
            writer = PdfWriter()
            
            for page_num in range(original_page_count):
                if page_num not in pages_to_remove:
                    writer.add_page(reader.pages[page_num])
            
            # Save the filtered PDF
            with open(output_pdf_path, 'wb') as output_file:
                writer.write(output_file)
        
        final_page_count = original_page_count - len(pages_to_remove)
        
        result = {
            'original_pages': original_page_count,
            'removed_pages': len(pages_to_remove),
            'final_pages': final_page_count,
            'removed_page_numbers': sorted([p + 1 for p in pages_to_remove]),  # 1-indexed for display
            'output_path': output_pdf_path
        }
        
        print(f"   ✓ Removed {len(pages_to_remove)} pages: {result['removed_page_numbers']}")
        print(f"   ✓ Final: {final_page_count} pages")
        print(f"   ✓ Saved: {output_pdf_path}")
        
        return result
    
    def _identify_pages_to_remove(self, reader: PdfReader, 
                                  remove_options: Dict[str, bool]) -> Set[int]:
        """
        Identify which pages should be removed
        
        Args:
            reader: PdfReader object
            remove_options: Dict of removal options
        
        Returns:
            Set of page indices (0-indexed) to remove
        
        How this works:
        - We check each page against the removal criteria
        - A page can be removed for multiple reasons
        - We return a set of unique page numbers to remove
        """
        pages_to_remove = set()
        
        # Option 1: Remove specific page numbers
        if 'page_numbers' in remove_options and remove_options['page_numbers']:
            for page_num in remove_options['page_numbers']:
                # Convert from 1-indexed (user) to 0-indexed (internal)
                pages_to_remove.add(page_num - 1)
        
        # Option 2: Remove blank pages
        if remove_options.get('blank_pages', False):
            blank_pages = self._detect_blank_pages(reader)
            pages_to_remove.update(blank_pages)
            print(f"   Detected blank pages: {sorted([p + 1 for p in blank_pages])}")
        
        # Option 3: Remove pages with specific text
        if 'pages_with_text' in remove_options:
            text_patterns = remove_options['pages_with_text']
            if text_patterns:
                matching_pages = self._find_pages_with_text(reader, text_patterns)
                pages_to_remove.update(matching_pages)
                print(f"   Pages with '{text_patterns}': {sorted([p + 1 for p in matching_pages])}")
        
        # Option 4: Remove every Nth page (e.g., every 2nd page for 3D renderings)
        if 'every_nth_page' in remove_options:
            nth = remove_options['every_nth_page']
            if nth > 0:
                nth_pages = set(range(nth - 1, len(reader.pages), nth))
                pages_to_remove.update(nth_pages)
                print(f"   Every {nth}th page: {sorted([p + 1 for p in nth_pages])}")
        
        return pages_to_remove
    
    def _detect_blank_pages(self, reader: PdfReader) -> Set[int]:
        """
        Detect blank or nearly-blank pages
        
        How blank detection works:
        1. Extract text from each page
        2. If page has very little or no text, it's likely blank
        3. This catches 3D rendering pages that show nothing
        
        Args:
            reader: PdfReader object
        
        Returns:
            Set of blank page indices (0-indexed)
        """
        blank_pages = set()
        
        for page_num, page in enumerate(reader.pages):
            try:
                # Extract text from the page
                text = page.extract_text()
                
                # Remove whitespace to get actual content
                text_content = text.strip()
                
                # Check if page is blank or has minimal content
                # Blank 3D rendering pages often have just "X/Y" page numbers
                # or "Powered by Measure Square" footer
                
                if len(text_content) < 50:  # Less than 50 characters = likely blank
                    blank_pages.add(page_num)
                    continue
                
                # Check if it's ONLY the standard footer/header
                text_lower = text_content.lower()
                is_only_header = (
                    'powered by measure square' in text_lower
                    and len(text_content) < 100
                )
                
                if is_only_header:
                    blank_pages.add(page_num)
                
            except Exception as e:
                print(f"   ⚠️ Warning: Could not analyze page {page_num + 1}: {e}")
                continue
        
        return blank_pages
    
    def _find_pages_with_text(self, reader: PdfReader, 
                             patterns: List[str]) -> Set[int]:
        """
        Find pages that contain specific text patterns
        
        Args:
            reader: PdfReader object
            patterns: List of text patterns to search for
        
        Returns:
            Set of page indices that contain any of the patterns
        """
        matching_pages = set()
        
        for page_num, page in enumerate(reader.pages):
            try:
                text = page.extract_text().lower()
                
                for pattern in patterns:
                    if pattern.lower() in text:
                        matching_pages.add(page_num)
                        break  # No need to check other patterns
                        
            except Exception as e:
                print(f"   ⚠️ Warning: Could not search page {page_num + 1}: {e}")
                continue
        
        return matching_pages
    
    def preview_pages(self, pdf_path: str) -> List[Dict]:
        """
        Preview what's on each page (for user to decide what to remove)
        
        Args:
            pdf_path: Path to PDF to preview
        
        Returns:
            List of page info dicts:
                [
                    {
                        'page_num': 1,
                        'text_length': 500,
                        'is_blank': False,
                        'preview': 'First 100 characters...'
                    },
                    ...
                ]
        """
        pages_info = []
        
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            
            for page_num, page in enumerate(reader.pages, 1):
                try:
                    text = page.extract_text()
                    text_content = text.strip()
                    
                    is_blank = len(text_content) < 50
                    
                    preview = text_content[:100] if text_content else "[Blank page]"
                    
                    pages_info.append({
                        'page_num': page_num,
                        'text_length': len(text_content),
                        'is_blank': is_blank,
                        'preview': preview
                    })
                    
                except Exception as e:
                    pages_info.append({
                        'page_num': page_num,
                        'text_length': 0,
                        'is_blank': True,
                        'preview': f"[Error reading page: {e}]"
                    })
        
        return pages_info


class CloudPDFDownloaderWithFilter:
    """
    Download PDFs from MeasureSquare Cloud API with automatic filtering
    
    This combines:
    1. Cloud API PDF download (perfect quality)
    2. Automatic page filtering (remove unwanted pages)
    
    Best of both worlds!
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the downloader
        
        Args:
            api_key: Your MeasureSquare API key
        """
        self.api_key = api_key
        self.base_url = "https://cloud.measuresquare.com/api"
        self.filter = PDFPageFilter()
    
    def download_and_filter(self, project_id: str, output_path: str,
                          filter_options: Dict[str, bool] = None) -> Dict:
        """
        Download PDF from cloud and apply filtering
        
        Args:
            project_id: MeasureSquare project ID
            output_path: Where to save the filtered PDF
            filter_options: What to remove (see PDFPageFilter.filter_pdf)
        
        Returns:
            Dict with download and filter results
        
        Example:
            downloader = CloudPDFDownloaderWithFilter("your_api_key")
            
            result = downloader.download_and_filter(
                "project_id_123",
                "output.pdf",
                filter_options={
                    'blank_pages': True,  # Remove blank 3D pages
                    'page_numbers': [4, 8, 10]  # Also remove these specific pages
                }
            )
            
            print(f"Downloaded and filtered! {result['final_pages']} pages")
        """
        if filter_options is None:
            filter_options = {'blank_pages': True}  # Default: remove blank pages
        
        print(f"\n{'='*60}")
        print(f"Downloading and Filtering PDF")
        print(f"{'='*60}")
        
        # Step 1: Download from cloud API
        print("\nStep 1: Downloading from cloud...")
        temp_path = str(Path(output_path).with_suffix('.temp.pdf'))
        
        self._download_pdf_from_api(project_id, temp_path)
        print(f"   ✓ Downloaded to: {temp_path}")
        
        # Step 2: Filter the PDF
        print("\nStep 2: Filtering pages...")
        filter_result = self.filter.filter_pdf(
            temp_path,
            output_path,
            filter_options
        )
        
        # Step 3: Clean up temp file
        Path(temp_path).unlink()
        
        print(f"\n{'='*60}")
        print(f"✅ Complete!")
        print(f"   Original: {filter_result['original_pages']} pages")
        print(f"   Removed: {filter_result['removed_pages']} pages")
        print(f"   Final: {filter_result['final_pages']} pages")
        print(f"   Saved: {output_path}")
        print(f"{'='*60}\n")
        
        return filter_result
    
    def _download_pdf_from_api(self, project_id: str, output_path: str):
        """Download PDF from MeasureSquare Cloud API"""
        import base64
        
        # Prepare authentication
        auth_string = f"{self.api_key}:"
        auth_base64 = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {auth_base64}',
            'Accept': 'application/pdf'
        }
        
        # Download PDF
        url = f"{self.base_url}/projects/{project_id}/pdf"
        
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        # Save to file
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

def example_1_remove_blank_pages():
    """Example: Download and remove blank 3D pages"""
    
    downloader = CloudPDFDownloaderWithFilter("your_api_key")
    
    result = downloader.download_and_filter(
        project_id="abc123",
        output_path="B_Down_filtered.pdf",
        filter_options={
            'blank_pages': True  # Automatically remove blank pages
        }
    )
    
    print(f"Removed {result['removed_pages']} blank pages!")


def example_2_remove_specific_pages():
    """Example: Remove specific page numbers (like 4, 8, 10)"""
    
    downloader = CloudPDFDownloaderWithFilter("your_api_key")
    
    result = downloader.download_and_filter(
        project_id="abc123",
        output_path="B_Down_filtered.pdf",
        filter_options={
            'page_numbers': [4, 8, 10]  # Remove these specific pages
        }
    )


def example_3_preview_then_filter():
    """Example: Preview pages first, then decide what to remove"""
    
    # First, download the full PDF
    downloader = CloudPDFDownloaderWithFilter("your_api_key")
    downloader._download_pdf_from_api("abc123", "temp.pdf")
    
    # Preview what's on each page
    filter = PDFPageFilter()
    pages = filter.preview_pages("temp.pdf")
    
    print("Page Preview:")
    for page in pages:
        status = "BLANK" if page['is_blank'] else "OK"
        print(f"  Page {page['page_num']}: [{status}] {page['preview'][:50]}...")
    
    # Now filter based on preview
    pages_to_remove = [p['page_num'] for p in pages if p['is_blank']]
    
    filter.filter_pdf(
        "temp.pdf",
        "filtered.pdf",
        {'page_numbers': pages_to_remove}
    )


def example_4_combined_filtering():
    """Example: Use multiple filtering options"""
    
    downloader = CloudPDFDownloaderWithFilter("your_api_key")
    
    result = downloader.download_and_filter(
        project_id="abc123",
        output_path="B_Down_filtered.pdf",
        filter_options={
            'blank_pages': True,  # Remove blank pages
            'page_numbers': [4, 8, 10],  # Also remove these specific pages
            'pages_with_text': ['3D View', 'Not Available']  # Remove pages with this text
        }
    )


if __name__ == "__main__":
    print("ProBuildIQ PDF Filter")
    print("=" * 60)
    print()
    print("This module filters unwanted pages from MeasureSquare PDFs")
    print()
    print("Features:")
    print("  • Remove blank 3D rendering pages")
    print("  • Remove specific page numbers")
    print("  • Remove pages with certain text")
    print("  • Preview pages before filtering")
    print()
    print("See example functions for usage!")
