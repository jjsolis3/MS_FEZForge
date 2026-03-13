"""
MeasureSquare Data Extractor - Hybrid Approach
Supports both API access and local FEZ file parsing

This program demonstrates:
1. API-based extraction (preferred when available)
2. Local FEZ file parsing (fallback or for offline use)
3. Unified interface for both methods
"""

import requests
import hmac
import hashlib
import base64
import time
import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import io


# =============================================================================
# Data Models - These represent the structured data we extract
# Why use dataclasses? They provide clean, typed data structures with
# automatic __init__, __repr__, and __eq__ methods
# =============================================================================

@dataclass
class Room:
    """Represents a room/area in the project"""
    id: str
    name: str
    area: float  # in square units
    perimeter: float  # in linear units
    layer_index: int
    
@dataclass
class Product:
    """Represents a flooring product"""
    id: str
    name: str
    type: str
    vendor: Optional[str] = None
    cost_price: Optional[float] = None
    sales_price: Optional[float] = None
    
@dataclass
class Estimation:
    """Represents material estimation/takeoff"""
    room_id: str
    room_name: str
    product_id: str
    product_name: str
    quantity: float
    unit: str
    waste: float
    total_quantity: float


# =============================================================================
# MeasureSquare Cloud API Client
# Why separate class? Encapsulates all API logic and authentication
# =============================================================================

class MeasureSquareAPIClient:
    """
    Client for interacting with MeasureSquare Cloud API
    
    Handles:
    - Authentication with API Key and X-Headers
    - Making authenticated requests
    - Parsing responses
    - Downloading binary data (images, PDFs)
    """
    
    def __init__(self, api_key: str, x_application: str = None, secret_key: str = None):
        """
        Initialize API client
        
        Args:
            api_key: Your API key from MeasureSquare Cloud
            x_application: Application ID (get from MeasureSquare support)
            secret_key: Secret key for HMAC signature (get from MeasureSquare support)
            
        Note: If x_application and secret_key are not provided, we'll try
        without X-Headers first (some APIs may not require them)
        """
        self.api_key = api_key
        self.x_application = x_application
        self.secret_key = secret_key
        self.base_url = "https://cloud.measuresquare.com/api"
        
        # Create a session to reuse connections (more efficient)
        # Why? TCP connection reuse improves performance for multiple requests
        self.session = requests.Session()
        
    def _generate_signature(self, timestamp: int) -> str:
        """
        Generate HMAC-SHA256 signature for X-Signature header
        
        Why HMAC? Provides cryptographic proof we know the secret key
        without transmitting it. The timestamp prevents replay attacks.
        
        Args:
            timestamp: Unix timestamp
            
        Returns:
            Base64-encoded HMAC-SHA256 signature
        """
        if not self.secret_key:
            return ""
            
        # Convert timestamp to string for HMAC
        message = str(timestamp).encode('utf-8')
        secret = self.secret_key.encode('utf-8')
        
        # Generate HMAC-SHA256
        signature = hmac.new(secret, message, hashlib.sha256).digest()
        
        # Base64 encode (API requirement)
        return base64.b64encode(signature).decode('utf-8')
    
    def _get_headers(self, accept_type: str = "application/json") -> Dict[str, str]:
        """
        Generate request headers including authentication
        
        Why separate method? Headers are needed for every request,
        so we centralize the logic here
        
        Args:
            accept_type: Response format (application/json or application/xml)
            
        Returns:
            Dictionary of headers
        """
        # Basic Auth: API key as username, no password
        # Why base64? HTTP Basic Auth requires base64-encoded credentials
        auth_string = f"{self.api_key}:"
        auth_bytes = auth_string.encode('utf-8')
        auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
        
        headers = {
            'Authorization': f'Basic {auth_base64}',
            'Accept': accept_type
        }
        
        # Add X-Headers if available
        if self.x_application and self.secret_key:
            timestamp = int(time.time())
            headers['X-Application'] = self.x_application
            headers['X-Timestamp'] = str(timestamp)
            headers['X-Signature'] = self._generate_signature(timestamp)
        
        return headers
    
    def _make_request(self, endpoint: str, method: str = "GET", 
                     params: Dict = None, accept_type: str = "application/json") -> requests.Response:
        """
        Make an authenticated API request
        
        Why separate method? Centralizes error handling and logging
        
        Args:
            endpoint: API endpoint (e.g., "projects/123/layers")
            method: HTTP method (GET, POST, etc.)
            params: Query parameters
            accept_type: Response content type
            
        Returns:
            Response object
            
        Raises:
            requests.HTTPError: If request fails
        """
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers(accept_type)
        
        response = self.session.request(
            method=method,
            url=url,
            headers=headers,
            params=params
        )
        
        # Raise exception for bad status codes
        # Why? Easier to handle errors with try/except than checking status codes
        response.raise_for_status()
        
        return response
    
    # -------------------------------------------------------------------------
    # Project Information Methods
    # -------------------------------------------------------------------------
    
    def get_projects(self, m2_id: str, search: str = None, 
                     is_archived: bool = False) -> List[Dict]:
        """
        Get list of projects for a MeasureSquare ID
        
        Args:
            m2_id: Your MeasureSquare ID (email)
            search: Optional search term
            is_archived: Include archived projects
            
        Returns:
            List of project dictionaries
        """
        params = {
            'search': search,
            'isArchived': str(is_archived).lower()
        }
        
        response = self._make_request(f"{m2_id}/projects", params=params)
        return response.json()
    
    def get_project_info(self, project_id: str, get_product_info: bool = True) -> Dict:
        """
        Get detailed project information
        
        Args:
            project_id: Project ID
            get_product_info: Include product information
            
        Returns:
            Project information dictionary
        """
        params = {'getProductInfo': str(get_product_info).lower()}
        response = self._make_request(f"projects/{project_id}", params=params)
        return response.json()
    
    # -------------------------------------------------------------------------
    # Layer and Room Methods
    # -------------------------------------------------------------------------
    
    def get_layers(self, project_id: str) -> List[Dict]:
        """
        Get all layers (floors) with room information
        
        This is KEY for getting room names, areas, and measurements
        
        Args:
            project_id: Project ID
            
        Returns:
            List of layer dictionaries with room data
        """
        response = self._make_request(f"projects/{project_id}/layers")
        return response.json()
    
    def get_layer_assignment(self, project_id: str, 
                            show_room_details: bool = True) -> Dict:
        """
        Get product assignments for each room
        
        This shows which products are assigned to which rooms
        
        Args:
            project_id: Project ID
            show_room_details: Include detailed room information
            
        Returns:
            Dictionary of product assignments
        """
        params = {'showRoomDetails': str(show_room_details).lower()}
        response = self._make_request(
            f"projects/{project_id}/layerAssignment",
            params=params
        )
        return response.json()
    
    # -------------------------------------------------------------------------
    # Estimation/Takeoff Methods
    # -------------------------------------------------------------------------
    
    def get_estimation(self, project_id: str, 
                      with_cut_image: bool = False) -> Dict:
        """
        Get project estimation (quantities, takeoffs)
        
        This is the MAIN method for getting material quantities
        
        Args:
            project_id: Project ID
            with_cut_image: Include cut optimization images
            
        Returns:
            Estimation data dictionary
        """
        params = {'withCutImage': str(with_cut_image).lower()}
        response = self._make_request(
            f"projects/{project_id}/estimation",
            params=params
        )
        return response.json()
    
    def get_worksheets(self, project_id: str) -> Dict:
        """
        Get project worksheets
        
        Worksheets contain formatted takeoff data
        
        Args:
            project_id: Project ID
            
        Returns:
            Worksheet data dictionary
        """
        response = self._make_request(f"projects/{project_id}/worksheets")
        return response.json()
    
    # -------------------------------------------------------------------------
    # Image/Diagram Methods
    # -------------------------------------------------------------------------
    
    def download_layer_image(self, project_id: str, layer_index: int,
                            width: int = 1920, height: int = 1080,
                            show_dimensions: bool = True,
                            output_path: str = None) -> bytes:
        """
        Download a single layer image
        
        Args:
            project_id: Project ID
            layer_index: Layer index (0-based)
            width: Image width in pixels
            height: Image height in pixels
            show_dimensions: Show dimension lines
            output_path: Optional path to save image
            
        Returns:
            Image bytes (PNG format)
        """
        params = {
            'width': width,
            'height': height,
            'showDimensions': str(show_dimensions).lower()
        }
        
        response = self._make_request(
            f"projects/{project_id}/layers/{layer_index}/image",
            params=params
        )
        
        image_data = response.content
        
        # Save if output path provided
        if output_path:
            Path(output_path).write_bytes(image_data)
            
        return image_data
    
    def download_all_images(self, project_id: str, 
                          width: int = 1920, height: int = 1080,
                          output_dir: str = None) -> bytes:
        """
        Download all layer images as a ZIP file
        
        Args:
            project_id: Project ID
            width: Image width in pixels
            height: Image height in pixels
            output_dir: Optional directory to extract images
            
        Returns:
            ZIP file bytes
        """
        params = {
            'width': width,
            'height': height
        }
        
        response = self._make_request(
            f"projects/{project_id}/images",
            params=params
        )
        
        zip_data = response.content
        
        # Extract if output directory provided
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
                zf.extractall(output_dir)
        
        return zip_data
    
    # -------------------------------------------------------------------------
    # Export Methods
    # -------------------------------------------------------------------------
    
    def download_pdf(self, project_id: str, output_path: str = None) -> bytes:
        """
        Download project as PDF
        
        Args:
            project_id: Project ID
            output_path: Optional path to save PDF
            
        Returns:
            PDF bytes
        """
        response = self._make_request(f"projects/{project_id}/pdf")
        pdf_data = response.content
        
        if output_path:
            Path(output_path).write_bytes(pdf_data)
            
        return pdf_data
    
    def download_dxf(self, project_id: str, output_path: str = None) -> bytes:
        """
        Download project as DXF (CAD format)
        
        Args:
            project_id: Project ID
            output_path: Optional path to save DXF
            
        Returns:
            DXF bytes
        """
        response = self._make_request(f"projects/{project_id}/dxf")
        dxf_data = response.content
        
        if output_path:
            Path(output_path).write_bytes(dxf_data)
            
        return dxf_data
    
    def download_fez(self, project_id: str, output_path: str = None) -> bytes:
        """
        Download original FEZ project file
        
        Args:
            project_id: Project ID
            output_path: Optional path to save FEZ
            
        Returns:
            FEZ file bytes
        """
        response = self._make_request(f"projects/{project_id}/download")
        fez_data = response.content
        
        if output_path:
            Path(output_path).write_bytes(fez_data)
            
        return fez_data


# =============================================================================
# Local FEZ File Parser
# Why separate? Provides offline capability and backup when API is unavailable
# =============================================================================

class FEZFileParser:
    """
    Parser for local FEZ files
    
    FEZ files are ZIP archives containing:
    - _serialized_content.xml (main project data)
    - ApplicationInfo.xml (metadata)
    - Other supporting files
    """
    
    def __init__(self, fez_path: str):
        """
        Initialize parser with FEZ file path
        
        Args:
            fez_path: Path to .fez file
        """
        self.fez_path = Path(fez_path)
        
        if not self.fez_path.exists():
            raise FileNotFoundError(f"FEZ file not found: {fez_path}")
        
        # FEZ is a ZIP file - open it for reading
        self.zip_file = zipfile.ZipFile(self.fez_path, 'r')
        
        # Parse main XML content
        self._parse_content()
    
    def _parse_content(self):
        """
        Parse the main _serialized_content.xml file
        
        Why separate method? XML parsing is complex and error-prone,
        so we isolate it here for better error handling
        """
        try:
            # Read the main XML file from the ZIP
            xml_content = self.zip_file.read('_serialized_content.xml')
            
            # Parse XML
            # Why ElementTree? It's built-in, efficient, and handles large XML well
            self.root = ET.fromstring(xml_content)
            
        except KeyError:
            raise ValueError("Invalid FEZ file: missing _serialized_content.xml")
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML in FEZ file: {e}")
    
    def get_application_info(self) -> Dict:
        """
        Get application/project metadata from ApplicationInfo.xml
        
        Returns:
            Dictionary of application info
        """
        try:
            xml_content = self.zip_file.read('ApplicationInfo.xml')
            app_root = ET.fromstring(xml_content)
            
            # Convert XML attributes to dictionary
            return dict(app_root.attrib)
            
        except KeyError:
            return {}
    
    def get_layers(self) -> List[Dict]:
        """
        Extract layer information from XML
        
        Returns:
            List of layer dictionaries
        """
        layers = []
        
        # Find all FepLayer elements
        # Why XPath? It's a powerful way to query XML structure
        for idx, layer_elem in enumerate(self.root.findall('.//FepLayer')):
            layer_data = {
                'index': idx,
                'id': layer_elem.get('_xid', f'layer_{idx}'),
                'rooms': self._extract_rooms_from_layer(layer_elem)
            }
            layers.append(layer_data)
        
        return layers
    
    def _extract_rooms_from_layer(self, layer_elem) -> List[Dict]:
        """
        Extract room information from a layer element
        
        This is complex because rooms can be represented as:
        - FepFloor elements
        - FepWallLayerRgn elements
        - Other shape types
        
        Args:
            layer_elem: XML element for the layer
            
        Returns:
            List of room dictionaries
        """
        rooms = []
        
        # Find floor/room elements
        # These contain the actual room shapes and measurements
        for room_elem in layer_elem.findall('.//FepFloor'):
            room_id = room_elem.get('_xid', '')
            
            # Try to extract room name from planRegion
            room_name = self._get_room_name(room_elem)
            
            # Calculate area from polygon points
            area = self._calculate_area_from_points(room_elem)
            
            rooms.append({
                'id': room_id,
                'name': room_name,
                'area': area,
                'element': room_elem  # Keep reference for detailed parsing
            })
        
        return rooms
    
    def _get_room_name(self, room_elem) -> str:
        """
        Extract room name from XML element
        
        Room names can be in different locations depending on the format
        
        Args:
            room_elem: XML element for the room
            
        Returns:
            Room name or empty string
        """
        # Try different possible locations for room name
        name_locations = [
            './/PlanRegion[@shapeId]',
            './geoRegion//ShapePolygon2d[@shape]'
        ]
        
        for location in name_locations:
            elem = room_elem.find(location)
            if elem is not None:
                shape_id = elem.get('shapeId') or elem.get('shape', '')
                if shape_id:
                    # Shape ID often contains room name
                    return shape_id.split(';')[0]
        
        return "Unnamed Room"
    
    def _calculate_area_from_points(self, room_elem) -> float:
        """
        Calculate room area from polygon points using Shoelace formula
        
        Why Shoelace? It's a standard algorithm for calculating polygon area
        from vertices, named for the crisscross pattern of the calculation
        
        Formula: Area = 0.5 * |Σ(x_i * y_{i+1} - x_{i+1} * y_i)|
        
        Args:
            room_elem: XML element containing polygon points
            
        Returns:
            Area in square units
        """
        # Find polygon with points
        polygon = room_elem.find('.//ShapePolygon2d[@points]')
        if polygon is None:
            return 0.0
        
        points_str = polygon.get('points', '')
        if not points_str:
            return 0.0
        
        # Parse points: "x1,y1|x2,y2|x3,y3"
        try:
            points = []
            for point_str in points_str.split('|'):
                x, y = map(float, point_str.split(','))
                points.append((x, y))
            
            # Shoelace formula implementation
            n = len(points)
            if n < 3:
                return 0.0
            
            area = 0.0
            for i in range(n):
                j = (i + 1) % n
                area += points[i][0] * points[j][1]
                area -= points[j][0] * points[i][1]
            
            return abs(area) / 2.0
            
        except (ValueError, IndexError):
            return 0.0
    
    def get_products(self) -> List[Dict]:
        """
        Extract product information from XML
        
        Returns:
            List of product dictionaries
        """
        products = []
        
        # Find all product elements
        # MeasureSquare has different product types: PlankProduct, RollProduct, etc.
        product_types = ['PlankProduct', 'RollProduct', 'LinearProduct', 
                        'CountProduct', 'TileProduct']
        
        for product_type in product_types:
            for prod_elem in self.root.findall(f'.//{product_type}'):
                product_data = {
                    'id': prod_elem.get('fepID', ''),
                    'type': product_type,
                    'name': prod_elem.get('fepDesc') or prod_elem.get('fepID', ''),
                    'vendor': prod_elem.get('vendor'),
                    'cost_price': self._parse_float(prod_elem.get('costPrice')),
                    'sales_price': self._parse_float(prod_elem.get('salesPrice')),
                    'unit': prod_elem.get('unit', ''),
                }
                products.append(product_data)
        
        return products
    
    def get_estimations(self) -> List[Dict]:
        """
        Extract estimation/takeoff data from XML
        
        This is where the material quantities are stored
        
        Returns:
            List of estimation dictionaries
        """
        estimations = []
        
        # Find EstimateArea elements which contain the takeoff results
        for est_area in self.root.findall('.//EstimateArea'):
            # Find all product usage results within this area
            for result_type in ['PlankResult', 'RollResult', 'LinearResult', 
                              'CountResult', 'TileResult']:
                for result in est_area.findall(f'.//{result_type}'):
                    estimation = {
                        'product_ref': result.get('product', ''),
                        'rooms': result.get('sourceShapes', ''),
                        'room_ids': result.get('sourceShapeIds', ''),
                        'original_qty': self._parse_float(result.get('originalQty')),
                        'usage': self._parse_float(result.get('usage')),
                        'waste': 0.0  # Calculate from difference
                    }
                    
                    # Calculate waste
                    if estimation['original_qty'] and estimation['usage']:
                        estimation['waste'] = (estimation['usage'] - 
                                             estimation['original_qty'])
                    
                    estimations.append(estimation)
        
        return estimations
    
    @staticmethod
    def _parse_float(value_str: Optional[str]) -> Optional[float]:
        """
        Safely parse float from string, handling comma-separated values
        
        MeasureSquare uses format like "1234.56,2" where ,2 indicates precision
        
        Args:
            value_str: String to parse
            
        Returns:
            Float value or None
        """
        if not value_str:
            return None
        
        try:
            # Take first part before comma
            return float(value_str.split(',')[0])
        except (ValueError, IndexError):
            return None
    
    def close(self):
        """Close the ZIP file"""
        self.zip_file.close()
    
    def __enter__(self):
        """Context manager support"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.close()


# =============================================================================
# Unified Interface - Hybrid Approach
# Why? Provides a single API that works with both cloud and local files
# =============================================================================

class MeasureSquareExtractor:
    """
    Unified interface for extracting data from MeasureSquare projects
    
    Automatically uses API when available, falls back to local parsing
    """
    
    def __init__(self, api_key: str = None, x_application: str = None,
                 secret_key: str = None, fez_path: str = None):
        """
        Initialize extractor
        
        Args:
            api_key: API key for cloud access
            x_application: X-Application header value
            secret_key: Secret key for X-Signature
            fez_path: Path to local FEZ file (fallback)
        """
        self.api_client = None
        self.fez_parser = None
        
        # Initialize API client if credentials provided
        if api_key:
            self.api_client = MeasureSquareAPIClient(
                api_key, x_application, secret_key
            )
        
        # Initialize local parser if FEZ path provided
        if fez_path:
            self.fez_parser = FEZFileParser(fez_path)
    
    def get_layers(self, project_id: str = None) -> List[Dict]:
        """
        Get layers from API or local file
        
        Args:
            project_id: Required for API, ignored for local file
            
        Returns:
            List of layer dictionaries
        """
        if self.api_client and project_id:
            return self.api_client.get_layers(project_id)
        elif self.fez_parser:
            return self.fez_parser.get_layers()
        else:
            raise ValueError("No data source available")
    
    def get_products(self, project_id: str = None) -> List[Dict]:
        """Get products from API or local file"""
        if self.api_client and project_id:
            project_info = self.api_client.get_project_info(project_id)
            return project_info.get('ProductList', [])
        elif self.fez_parser:
            return self.fez_parser.get_products()
        else:
            raise ValueError("No data source available")
    
    def get_estimations(self, project_id: str = None) -> List[Dict]:
        """Get estimations from API or local file"""
        if self.api_client and project_id:
            return self.api_client.get_estimation(project_id)
        elif self.fez_parser:
            return self.fez_parser.get_estimations()
        else:
            raise ValueError("No data source available")
    
    def export_data_to_json(self, output_path: str, project_id: str = None):
        """
        Export all data to JSON file
        
        Args:
            output_path: Path to save JSON file
            project_id: Project ID (for API mode)
        """
        data = {
            'layers': self.get_layers(project_id),
            'products': self.get_products(project_id),
            'estimations': self.get_estimations(project_id),
            'exported_at': datetime.now().isoformat()
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Data exported to: {output_path}")


# =============================================================================
# Example Usage and Testing
# =============================================================================

def example_api_usage():
    """Example: Using the API client"""
    
    # Your API credentials
    API_KEY = "your_api_key_here"  # Replace with your actual key
    X_APPLICATION = "your_x_application"  # Get from MeasureSquare support
    SECRET_KEY = "your_secret_key"  # Get from MeasureSquare support
    
    # Initialize API client
    client = MeasureSquareAPIClient(API_KEY, X_APPLICATION, SECRET_KEY)
    
    # Get your MeasureSquare ID (usually your email)
    M2_ID = "your.email@company.com"
    
    # Example 1: List all projects
    print("Fetching projects...")
    projects = client.get_projects(M2_ID)
    print(f"Found {len(projects)} projects")
    
    if projects:
        # Use first project as example
        project = projects[0]
        project_id = project['ProjectId']
        
        print(f"\nWorking with project: {project['Name']}")
        
        # Example 2: Get layers and rooms
        print("\nFetching layers...")
        layers = client.get_layers(project_id)
        print(f"Found {len(layers)} layers")
        
        # Example 3: Get estimations
        print("\nFetching estimations...")
        estimation = client.get_estimation(project_id)
        print("Estimation data retrieved")
        
        # Example 4: Download images
        print("\nDownloading layer images...")
        client.download_all_images(project_id, output_dir="./project_images")
        print("Images downloaded to ./project_images")
        
        # Example 5: Download PDF
        print("\nDownloading PDF...")
        client.download_pdf(project_id, output_path="./project_report.pdf")
        print("PDF saved to ./project_report.pdf")


def example_local_usage():
    """Example: Using the local FEZ parser"""
    
    # Path to your local FEZ file
    FEZ_PATH = "/path/to/your/project.fez"
    
    # Use context manager for automatic cleanup
    with FEZFileParser(FEZ_PATH) as parser:
        
        # Example 1: Get application info
        print("Application Info:")
        app_info = parser.get_application_info()
        print(f"  Application Type: {app_info.get('ApplicationType')}")
        print(f"  Version: {app_info.get('Version')}")
        
        # Example 2: Get layers and rooms
        print("\nLayers and Rooms:")
        layers = parser.get_layers()
        for layer in layers:
            print(f"  Layer {layer['index']}:")
            for room in layer['rooms']:
                print(f"    - {room['name']}: {room['area']:.2f} sq units")
        
        # Example 3: Get products
        print("\nProducts:")
        products = parser.get_products()
        for product in products:
            print(f"  - {product['name']} ({product['type']})")
        
        # Example 4: Get estimations
        print("\nEstimations:")
        estimations = parser.get_estimations()
        for est in estimations:
            print(f"  - Product: {est['product_ref']}")
            print(f"    Rooms: {est['rooms']}")
            print(f"    Quantity: {est['usage']:.2f}")


def example_hybrid_usage():
    """Example: Using the hybrid extractor"""
    
    # Try API first, fallback to local file
    extractor = MeasureSquareExtractor(
        api_key="your_api_key",
        fez_path="/path/to/backup.fez"
    )
    
    # These methods will use API if available, otherwise local file
    layers = extractor.get_layers(project_id="123")
    products = extractor.get_products(project_id="123")
    estimations = extractor.get_estimations(project_id="123")
    
    # Export everything to JSON
    extractor.export_data_to_json("project_data.json", project_id="123")


if __name__ == "__main__":
    print("MeasureSquare Data Extractor")
    print("=" * 50)
    print("\nThis module provides three ways to extract data:")
    print("1. MeasureSquareAPIClient - For cloud API access")
    print("2. FEZFileParser - For local FEZ file parsing")
    print("3. MeasureSquareExtractor - Hybrid approach (API + fallback)")
    print("\nSee example functions for usage patterns.")
