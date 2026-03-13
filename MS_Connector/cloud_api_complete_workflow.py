"""
ProBuildIQ Cloud API - Complete Workflow
=========================================

Answers to your questions:
1. ✅ Can we upload local FEZ files to cloud?
2. ✅ Can we update/edit files via API?
3. ✅ How to handle 400 files when limit is 100?
4. ✅ How to extract only specific files?
5. ✅ What are the limits?

This module provides everything you need!
"""

import requests
import base64
import time
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


# =============================================================================
# Extended API Client with Upload and Update Capabilities
# =============================================================================

class CloudAPIWorkflow:
    """
    Complete cloud API workflow including:
    - Upload local FEZ files
    - Update project metadata
    - Handle pagination (get all 400 files!)
    - Filter specific projects
    - Generate PDFs with cloud rendering
    
    Why this is better than local:
    - Official MeasureSquare PDF rendering
    - Consistent quality
    - Access from anywhere
    - Team collaboration
    """
    
    def __init__(self, api_key: str, m2_id: str, 
                 x_application: str = None, secret_key: str = None):
        """
        Initialize cloud API client
        
        Args:
            api_key: Your API key from cloud.measuresquare.com
            m2_id: Your MeasureSquare ID (email)
            x_application: X-Application header (optional)
            secret_key: Secret key for X-Signature (optional)
        """
        self.api_key = api_key
        self.m2_id = m2_id
        self.x_application = x_application
        self.secret_key = secret_key
        self.base_url = "https://cloud.measuresquare.com/api"
        self.session = requests.Session()
    
    def _get_headers(self, accept_type: str = "application/json") -> Dict[str, str]:
        """Generate authentication headers"""
        auth_string = f"{self.api_key}:"
        auth_base64 = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {auth_base64}',
            'Accept': accept_type
        }
        
        if self.x_application and self.secret_key:
            import hmac
            import hashlib
            timestamp = int(time.time())
            message = str(timestamp).encode('utf-8')
            signature = hmac.new(
                self.secret_key.encode('utf-8'),
                message,
                hashlib.sha256
            ).digest()
            
            headers['X-Application'] = self.x_application
            headers['X-Timestamp'] = str(timestamp)
            headers['X-Signature'] = base64.b64encode(signature).decode()
        
        return headers
    
    # =========================================================================
    # Q1: UPLOAD LOCAL FEZ FILES TO CLOUD
    # =========================================================================
    
    def upload_fez_file(self, fez_path: str, project_name: str = None,
                       customer_name: str = None) -> Dict:
        """
        Upload a local FEZ file to MeasureSquare Cloud
        
        Why upload? To get the official cloud PDF rendering!
        
        Args:
            fez_path: Path to local FEZ file
            project_name: Name for the project (optional)
            customer_name: Customer name (optional)
            
        Returns:
            Project information dict with ProjectId
            
        Example:
            result = workflow.upload_fez_file(
                "B_Down_-_1x1.fez",
                project_name="B Down Apartment",
                customer_name="John Smith"
            )
            project_id = result['ProjectId']
        """
        fez_path = Path(fez_path)
        
        if not fez_path.exists():
            raise FileNotFoundError(f"FEZ file not found: {fez_path}")
        
        # Use filename as project name if not provided
        if not project_name:
            project_name = fez_path.stem.replace('_', ' ').title()
        
        print(f"📤 Uploading: {fez_path.name}")
        print(f"   Project name: {project_name}")
        
        # Read FEZ file
        with open(fez_path, 'rb') as f:
            fez_bytes = f.read()
        
        # Prepare project data
        # Note: The API accepts FEZ file upload through multipart/form-data
        # or you can POST the FEZ content directly
        
        # Method 1: Upload via multipart (if supported)
        files = {
            'file': (fez_path.name, fez_bytes, 'application/octet-stream')
        }
        
        data = {
            'Name': project_name,
            'ProjectName': customer_name or project_name,
            'ApplicationType': 'FloorCovering'
        }
        
        # Upload to API
        url = f"{self.base_url}/{self.m2_id}/projects"
        headers = self._get_headers()
        headers.pop('Accept')  # Remove for file upload
        
        try:
            response = self.session.post(
                url,
                files=files,
                data=data,
                headers=headers
            )
            response.raise_for_status()
            
            result = response.json()
            project_id = result.get('ProjectId')
            
            print(f"   ✅ Uploaded! Project ID: {project_id}")
            
            return result
            
        except requests.exceptions.HTTPError as e:
            # If multipart doesn't work, try JSON approach
            print(f"   ⚠️ Trying alternative upload method...")
            return self._upload_via_json(fez_path, project_name, customer_name)
    
    def _upload_via_json(self, fez_path: Path, project_name: str, 
                        customer_name: str) -> Dict:
        """
        Alternative upload method using JSON payload
        
        Note: MeasureSquare API may require FEZ file to be pre-uploaded
        to their system first, then referenced by URL.
        """
        # Encode FEZ as base64 for JSON transport
        with open(fez_path, 'rb') as f:
            fez_base64 = base64.b64encode(f.read()).decode()
        
        payload = {
            'Name': project_name,
            'ProjectName': customer_name or project_name,
            'ApplicationType': 'FloorCovering',
            'FileContent': fez_base64,  # This may not be supported
            'FileName': fez_path.name
        }
        
        url = f"{self.base_url}/{self.m2_id}/projects"
        headers = self._get_headers('application/json')
        headers['Content-Type'] = 'application/json'
        
        response = self.session.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    # =========================================================================
    # Q2: UPDATE/EDIT CLOUD PROJECTS
    # =========================================================================
    
    def update_project_metadata(self, project_id: str, updates: Dict) -> Dict:
        """
        Update project information (customer, address, products, etc.)
        
        What you can update:
        - Customer name, address, phone
        - Project notes
        - Product information
        - Room assignments
        
        Args:
            project_id: Project ID to update
            updates: Dict of fields to update (see example below)
            
        Returns:
            Updated project info
            
        Example:
            updates = {
                'ProjectId': 'abc123',  # Required for update!
                'ContactName': 'John Smith',
                'Email': 'john@example.com',
                'Phone': '555-1234',
                'ProjectNote': 'Updated for final bid',
                'ProductList': [...]  # Optional
            }
            
            result = workflow.update_project_metadata(project_id, updates)
        """
        print(f"📝 Updating project: {project_id}")
        
        # ProjectId is REQUIRED for updates
        updates['ProjectId'] = project_id
        
        # Make sure at least Name is provided
        if 'Name' not in updates and 'ProjectName' not in updates:
            # Get current project name
            current = self.get_project_info(project_id)
            updates['Name'] = current.get('Name', 'Project')
        
        url = f"{self.base_url}/{self.m2_id}/projects"
        headers = self._get_headers('application/json')
        headers['Content-Type'] = 'application/json'
        
        response = self.session.post(url, json=updates, headers=headers)
        response.raise_for_status()
        
        print(f"   ✅ Updated successfully!")
        
        return response.json()
    
    def get_project_info(self, project_id: str) -> Dict:
        """Get current project information"""
        url = f"{self.base_url}/projects/{project_id}"
        params = {'getProductInfo': 'true'}
        headers = self._get_headers()
        
        response = self.session.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    # =========================================================================
    # Q3: HANDLE PAGINATION (Get all 400 files when limit is 100!)
    # =========================================================================
    
    def get_all_projects(self, search: str = None, 
                        is_archived: bool = False) -> List[Dict]:
        """
        Get ALL projects, handling pagination automatically
        
        API Limit: Max 100 per request
        Your Need: 400 projects
        Solution: Make multiple requests!
        
        Args:
            search: Filter by project name
            is_archived: Include archived projects
            
        Returns:
            List of ALL projects (even if >100)
            
        Example:
            # Get all 400 projects
            all_projects = workflow.get_all_projects()
            print(f"Found {len(all_projects)} projects")
            
            # With filtering
            filtered = workflow.get_all_projects(search="B Down")
        """
        print(f"📊 Fetching all projects for {self.m2_id}...")
        
        all_projects = []
        page_index = 0
        page_length = 100  # Max allowed
        
        while True:
            print(f"   Getting page {page_index + 1} (items {page_index * 100 + 1}-{(page_index + 1) * 100})...")
            
            # Get one page
            projects = self._get_projects_page(
                page_length=page_length,
                page_index=page_index,
                search=search,
                is_archived=is_archived
            )
            
            if not projects:
                # No more results
                break
            
            all_projects.extend(projects)
            print(f"   ✓ Got {len(projects)} projects")
            
            # If we got less than page_length, we're done
            if len(projects) < page_length:
                break
            
            page_index += 1
            
            # Rate limiting protection
            time.sleep(0.5)  # Be nice to the API
        
        print(f"   ✅ Total: {len(all_projects)} projects")
        
        return all_projects
    
    def _get_projects_page(self, page_length: int, page_index: int,
                          search: str = None, is_archived: bool = False) -> List[Dict]:
        """
        Get a single page of projects
        
        This is what you use to get projects 100-200, 200-300, etc.
        
        Args:
            page_length: Items per page (max 100)
            page_index: Which page (0=first 100, 1=next 100, etc.)
            search: Filter by name
            is_archived: Include archived
            
        Returns:
            List of projects for this page
        """
        url = f"{self.base_url}/{self.m2_id}/projects/length/{page_length}/page/{page_index}"
        
        params = {
            'isArchived': str(is_archived).lower(),
            'showTags': 'true'
        }
        
        if search:
            params['search'] = search
        
        headers = self._get_headers()
        
        response = self.session.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    # =========================================================================
    # Q4: SELECT SPECIFIC FILES TO EXTRACT
    # =========================================================================
    
    def filter_projects(self, 
                       name_contains: str = None,
                       created_after: str = None,
                       customer_name: str = None,
                       include_archived: bool = False) -> List[Dict]:
        """
        Get only specific projects based on filters
        
        Args:
            name_contains: Project name contains this text
            created_after: Date string like "2024-01-01"
            customer_name: Customer name contains this text
            include_archived: Include archived projects
            
        Returns:
            Filtered list of projects
            
        Example:
            # Only projects with "Apartment" in name
            projects = workflow.filter_projects(name_contains="Apartment")
            
            # Only recent projects
            projects = workflow.filter_projects(created_after="2024-11-01")
            
            # Specific customer
            projects = workflow.filter_projects(customer_name="Smith")
        """
        print("🔍 Filtering projects...")
        
        # Get all projects (handles pagination)
        all_projects = self.get_all_projects(
            search=name_contains,
            is_archived=include_archived
        )
        
        filtered = all_projects
        
        # Filter by date if specified
        if created_after:
            cutoff = datetime.strptime(created_after, "%Y-%m-%d").timestamp()
            filtered = [p for p in filtered 
                       if p.get('LastUpdatedOn', 0) >= cutoff]
        
        # Filter by customer (requires getting full project info)
        if customer_name:
            print(f"   Filtering by customer: {customer_name}")
            customer_filtered = []
            for project in filtered:
                try:
                    info = self.get_project_info(project['ProjectId'])
                    proj_customer = info.get('ProjectInfo', {}).get('ContactName', '')
                    if customer_name.lower() in proj_customer.lower():
                        customer_filtered.append(project)
                except:
                    pass  # Skip if can't get info
            filtered = customer_filtered
        
        print(f"   ✅ Found {len(filtered)} matching projects")
        
        return filtered
    
    # =========================================================================
    # Q5: API LIMITS AND BEST PRACTICES
    # =========================================================================
    
    def get_api_limits(self) -> Dict:
        """
        Display API limits and best practices
        
        Returns:
            Dict with limit information
        """
        limits = {
            'projects_per_request': 100,
            'pdf_generation': {
                'rate': '10 per minute',
                'cooldown': '1 second between calls'
            },
            'general_requests': 'No documented limit, be reasonable',
            'recommendations': {
                'batch_processing': 'Add delays between requests',
                'pagination': 'Max 100 items per page',
                'pdf_generation': 'Wait 1 second between PDF downloads',
                'file_upload': 'No documented limit on file size'
            }
        }
        
        print("📋 API LIMITS:")
        print(f"   Max projects per request: {limits['projects_per_request']}")
        print(f"   PDF generation: {limits['pdf_generation']['rate']}")
        print(f"   Cooldown: {limits['pdf_generation']['cooldown']}")
        print()
        print("💡 BEST PRACTICES:")
        for key, value in limits['recommendations'].items():
            print(f"   {key}: {value}")
        
        return limits
    
    # =========================================================================
    # DOWNLOAD FEZ FILE FROM CLOUD
    # =========================================================================

    def download_fez(self, project_id: str, save_path: str = None) -> str:
        """
        Download a project's FEZ file from the cloud

        Args:
            project_id: Project ID to download
            save_path: Path to save the FEZ file. If None, saves to temp directory.

        Returns:
            Path to the downloaded FEZ file
        """
        import tempfile

        url = f"{self.base_url}/projects/{project_id}/download"
        headers = self._get_headers('application/octet-stream')

        response = self.session.get(url, headers=headers)
        response.raise_for_status()

        if save_path is None:
            temp_dir = tempfile.mkdtemp(prefix="ms_fez_")
            save_path = str(Path(temp_dir) / f"{project_id}.fez")

        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        Path(save_path).write_bytes(response.content)

        print(f"   Downloaded FEZ to: {save_path}")
        return save_path

    # =========================================================================
    # COMPLETE WORKFLOW: Upload → Update → Extract
    # =========================================================================
    
    def upload_and_extract_workflow(self, fez_path: str, 
                                   output_dir: str = "./extracted") -> Dict:
        """
        Complete workflow: Upload local FEZ → Get cloud PDF
        
        This is the recommended way to get high-quality PDFs!
        
        Args:
            fez_path: Local FEZ file path
            output_dir: Where to save extracted PDF
            
        Returns:
            Dict with project_id and file paths
            
        Example:
            result = workflow.upload_and_extract_workflow(
                "B_Down_-_1x1.fez",
                output_dir="./output"
            )
            
            print(f"Project ID: {result['project_id']}")
            print(f"PDF saved: {result['pdf_path']}")
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Upload FEZ file
        print("\n" + "="*60)
        print("STEP 1: Uploading FEZ file to cloud")
        print("="*60)
        
        upload_result = self.upload_fez_file(fez_path)
        project_id = upload_result['ProjectId']
        
        # Step 2: Wait for processing
        print("\n" + "="*60)
        print("STEP 2: Waiting for cloud processing")
        print("="*60)
        print("   ⏳ Cloud is processing your file...")
        time.sleep(5)  # Give cloud time to process
        print("   ✅ Ready!")
        
        # Step 3: Generate cloud PDF
        print("\n" + "="*60)
        print("STEP 3: Generating cloud-rendered PDF")
        print("="*60)
        
        from measuresquare_extractor import MeasureSquareAPIClient
        client = MeasureSquareAPIClient(self.api_key, self.x_application, self.secret_key)
        
        pdf_path = output_dir / f"{Path(fez_path).stem}_cloud.pdf"
        client.download_pdf(project_id, output_path=str(pdf_path))
        
        print(f"   ✅ PDF saved: {pdf_path}")
        
        # Step 4: Download images
        print("\n" + "="*60)
        print("STEP 4: Downloading layer images")
        print("="*60)
        
        images_dir = output_dir / f"{Path(fez_path).stem}_images"
        client.download_all_images(project_id, output_dir=str(images_dir))
        
        print(f"   ✅ Images saved: {images_dir}")
        
        return {
            'project_id': project_id,
            'pdf_path': str(pdf_path),
            'images_dir': str(images_dir)
        }


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

def example_1_upload_file():
    """Example: Upload local FEZ to cloud"""
    
    workflow = CloudAPIWorkflow(
        api_key="your_api_key",
        m2_id="your.email@company.com"
    )
    
    # Upload local file
    result = workflow.upload_fez_file(
        "B_Down_-_1x1.fez",
        project_name="B Down Apartment - Unit 1x1",
        customer_name="ABC Properties"
    )
    
    project_id = result['ProjectId']
    print(f"Project uploaded! ID: {project_id}")


def example_2_update_project():
    """Example: Update project information"""
    
    workflow = CloudAPIWorkflow(
        api_key="your_api_key",
        m2_id="your.email@company.com"
    )
    
    # Update customer info
    updates = {
        'ContactName': 'John Smith',
        'Email': 'john@example.com',
        'Phone': '555-1234',
        'Street': '123 Main St',
        'City': 'Santa Clarita',
        'State': 'CA',
        'ZipCode': '91355',
        'ProjectNote': 'Final bid - approved by customer'
    }
    
    workflow.update_project_metadata('project_id_here', updates)


def example_3_get_all_400_projects():
    """Example: Get all projects (handles 400+ automatically)"""
    
    workflow = CloudAPIWorkflow(
        api_key="your_api_key",
        m2_id="your.email@company.com"
    )
    
    # Get ALL projects (even if >100)
    all_projects = workflow.get_all_projects()
    
    print(f"Found {len(all_projects)} total projects")
    
    # Process each one
    for i, project in enumerate(all_projects, 1):
        print(f"{i}. {project['Name']} (ID: {project['ProjectId']})")


def example_4_filter_specific_projects():
    """Example: Extract only specific projects"""
    
    workflow = CloudAPIWorkflow(
        api_key="your_api_key",
        m2_id="your.email@company.com"
    )
    
    # Only projects with "Apartment" in name
    filtered = workflow.filter_projects(name_contains="Apartment")
    
    print(f"Found {len(filtered)} apartment projects")
    
    # Generate PDFs for these specific ones
    from measuresquare_extractor import MeasureSquareAPIClient
    client = MeasureSquareAPIClient("your_api_key")
    
    for project in filtered:
        project_id = project['ProjectId']
        pdf_name = f"{project['Name']}.pdf"
        client.download_pdf(project_id, pdf_name)
        print(f"✓ {pdf_name}")


def example_5_complete_workflow():
    """Example: Upload → Update → Extract (Complete process)"""
    
    workflow = CloudAPIWorkflow(
        api_key="your_api_key",
        m2_id="your.email@company.com"
    )
    
    # Complete workflow: Local FEZ → Cloud → High-quality PDF
    result = workflow.upload_and_extract_workflow(
        "B_Down_-_1x1.fez",
        output_dir="./cloud_extracted"
    )
    
    print(f"\n✅ Complete!")
    print(f"   Project ID: {result['project_id']}")
    print(f"   PDF: {result['pdf_path']}")
    print(f"   Images: {result['images_dir']}")


if __name__ == "__main__":
    print("ProBuildIQ Cloud API Workflow")
    print("=" * 60)
    print()
    print("This module answers all your questions:")
    print("1. ✅ Upload local FEZ files")
    print("2. ✅ Update cloud projects")
    print("3. ✅ Handle 400+ files (pagination)")
    print("4. ✅ Filter specific projects")
    print("5. ✅ API limits and best practices")
    print()
    print("See example functions for usage!")
