"""
Cloud Text Editor - Edit project text data in MeasureSquare Cloud
=================================================================

This module provides the ability to:
1. Edit project names directly via API
2. Edit project metadata (contact info, notes, address) via API
3. Edit room names via download-edit-reupload workflow
4. View current room names from cloud projects

Why download-edit-reupload for rooms?
The MeasureSquare API does not expose endpoints for editing room names
directly. The workaround is to download the FEZ file, modify the XML
inside it, and re-upload the modified file.
"""

import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from cloud_api_complete_workflow import CloudAPIWorkflow
from probuildiq_fez_editor import FEZFileEditor


class CloudTextEditor:
    """
    Edit text fields in MeasureSquare Cloud projects.

    Supports:
    - Project name (direct API)
    - Project metadata: contact, address, phone, email, notes (direct API)
    - Room names (download FEZ -> edit -> re-upload)
    """

    def __init__(self, api_key: str, m2_id: str,
                 x_application: str = None, secret_key: str = None):
        self.workflow = CloudAPIWorkflow(
            api_key=api_key,
            m2_id=m2_id,
            x_application=x_application,
            secret_key=secret_key
        )
        self.m2_id = m2_id

    # =========================================================================
    # Project Listing
    # =========================================================================

    def list_projects(self, search: str = None) -> List[Dict]:
        """
        List all projects with names and IDs.

        Args:
            search: Optional filter by project name

        Returns:
            List of project dicts with 'Name' and 'ProjectId' keys
        """
        return self.workflow.get_all_projects(search=search)

    # =========================================================================
    # Direct API Updates (project name and metadata)
    # =========================================================================

    def update_project_name(self, project_id: str, new_name: str) -> Dict:
        """
        Rename a project in the cloud.

        Args:
            project_id: Project ID
            new_name: New project name

        Returns:
            API response dict
        """
        print(f"Renaming project {project_id} to: {new_name}")
        return self.workflow.update_project_metadata(project_id, {
            'Name': new_name,
            'ProjectName': new_name,
        })

    def update_project_info(self, project_id: str, fields: Dict) -> Dict:
        """
        Update project metadata fields.

        Supported fields:
            ContactName, Email, Phone, Street, City, State, ZipCode, ProjectNote

        Args:
            project_id: Project ID
            fields: Dict of field names to new values

        Returns:
            API response dict
        """
        print(f"Updating project {project_id} metadata...")
        return self.workflow.update_project_metadata(project_id, fields)

    # =========================================================================
    # Room Name Operations (download-edit-reupload)
    # =========================================================================

    def get_room_names(self, project_id: str) -> List[Dict[str, str]]:
        """
        Get all room names from a cloud project by downloading its FEZ file.

        Args:
            project_id: Project ID

        Returns:
            List of dicts with 'id' and 'name' keys
        """
        temp_dir = tempfile.mkdtemp(prefix="ms_rooms_")
        try:
            fez_path = self.workflow.download_fez(
                project_id,
                save_path=str(Path(temp_dir) / f"{project_id}.fez")
            )
            with FEZFileEditor(fez_path) as editor:
                return editor.get_all_room_names()
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def rename_rooms(self, project_id: str, rename_map: Dict[str, str]) -> bool:
        """
        Rename rooms in a cloud project.

        Workflow: download FEZ -> rename rooms -> re-upload.

        Args:
            project_id: Project ID
            rename_map: Dict of {old_name: new_name}

        Returns:
            True if successful
        """
        if not rename_map:
            print("No renames specified.")
            return False

        temp_dir = tempfile.mkdtemp(prefix="ms_edit_")
        try:
            # Step 1: Download FEZ
            print("Step 1/3: Downloading project FEZ file...")
            fez_path = self.workflow.download_fez(
                project_id,
                save_path=str(Path(temp_dir) / f"{project_id}.fez")
            )

            # Step 2: Edit room names
            print("Step 2/3: Editing room names...")
            modified_path = str(Path(temp_dir) / f"{project_id}_modified.fez")
            with FEZFileEditor(fez_path) as editor:
                count = editor.batch_rename_rooms(rename_map)
                if count == 0:
                    print("   No matching rooms found to rename.")
                    return False
                print(f"   Renamed {count} room(s)")
                editor.save(modified_path)

            # Step 3: Re-upload
            print("Step 3/3: Re-uploading modified project...")
            self.workflow.upload_fez_file(
                modified_path,
                project_name=None  # Keeps existing name
            )
            print("   Done! Room names updated in cloud.")
            return True

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def rename_rooms_interactive(self, project_id: str) -> bool:
        """
        Interactive room renaming - shows current rooms and prompts for new names.

        Args:
            project_id: Project ID

        Returns:
            True if any rooms were renamed
        """
        # Get current room names
        print("\nFetching current room names...")
        rooms = self.get_room_names(project_id)

        if not rooms:
            print("No rooms found in this project.")
            return False

        print(f"\nFound {len(rooms)} room(s):")
        print("-" * 50)
        for i, room in enumerate(rooms, 1):
            print(f"  {i}. {room['name']}")
        print("-" * 50)

        # Collect renames
        rename_map = {}
        print("\nEnter new names for rooms you want to rename.")
        print("Press Enter to skip a room (keep current name).\n")

        for i, room in enumerate(rooms, 1):
            new_name = input(f"  {room['name']} -> ").strip()
            if new_name and new_name != room['name']:
                rename_map[room['name']] = new_name

        if not rename_map:
            print("\nNo changes made.")
            return False

        # Confirm
        print(f"\nChanges to apply ({len(rename_map)}):")
        for old, new in rename_map.items():
            print(f"  {old} -> {new}")

        confirm = input("\nApply these changes? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Cancelled.")
            return False

        return self.rename_rooms(project_id, rename_map)


# =============================================================================
# Standalone Usage
# =============================================================================

def main():
    """Interactive standalone usage"""
    import json

    print("=" * 60)
    print("MeasureSquare Cloud Text Editor")
    print("=" * 60)

    # Load config
    try:
        with open("config.json") as f:
            config = json.load(f)
        api_key = config['api']['api_key']
        m2_id = config['api']['m2_id']
        x_app = config['api'].get('x_application')
        secret = config['api'].get('secret_key')
    except FileNotFoundError:
        print("config.json not found. Please create it first.")
        return

    editor = CloudTextEditor(api_key, m2_id, x_app, secret)

    while True:
        print("\nOptions:")
        print("  1. List projects")
        print("  2. Rename a project")
        print("  3. Update project metadata")
        print("  4. View room names")
        print("  5. Rename rooms (interactive)")
        print("  0. Exit")

        choice = input("\nChoice: ").strip()

        if choice == '1':
            projects = editor.list_projects()
            for i, p in enumerate(projects, 1):
                print(f"  {i}. {p['Name']}  (ID: {p['ProjectId']})")

        elif choice == '2':
            pid = input("Project ID: ").strip()
            new_name = input("New project name: ").strip()
            if pid and new_name:
                editor.update_project_name(pid, new_name)

        elif choice == '3':
            pid = input("Project ID: ").strip()
            print("Enter fields to update (leave blank to skip):")
            fields = {}
            for field in ['ContactName', 'Email', 'Phone', 'Street',
                          'City', 'State', 'ZipCode', 'ProjectNote']:
                val = input(f"  {field}: ").strip()
                if val:
                    fields[field] = val
            if fields:
                editor.update_project_info(pid, fields)

        elif choice == '4':
            pid = input("Project ID: ").strip()
            if pid:
                rooms = editor.get_room_names(pid)
                for i, r in enumerate(rooms, 1):
                    print(f"  {i}. {r['name']}")

        elif choice == '5':
            pid = input("Project ID: ").strip()
            if pid:
                editor.rename_rooms_interactive(pid)

        elif choice == '0':
            break


if __name__ == "__main__":
    main()
