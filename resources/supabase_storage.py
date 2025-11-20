"""
Supabase Storage Utility Module
Handles file uploads and management with Supabase Storage
"""
import os
import uuid
from django.conf import settings
from supabase import create_client, Client
from typing import Optional, Tuple
import mimetypes


class SupabaseStorage:
    """Utility class for Supabase storage operations"""
    
    def __init__(self):
        """Initialize Supabase client"""
        # Check if Supabase credentials are configured
        supabase_url = getattr(settings, 'SUPABASE_URL', '')
        supabase_key = getattr(settings, 'SUPABASE_SERVICE_KEY', '')
        
        # Only create client if both credentials are provided, non-empty, and valid
        if supabase_url and supabase_url.strip() and supabase_key and supabase_key.strip():
            try:
                self.supabase: Client = create_client(supabase_url, supabase_key)
                self.bucket_name = getattr(settings, 'SUPABASE_BUCKET', None)
            except Exception as e:
                # If client creation fails, disable Supabase
                print(f"Warning: Failed to initialize Supabase client: {e}")
                self.supabase = None
                self.bucket_name = None
        else:
            # Supabase not configured, set to None
            self.supabase = None
            self.bucket_name = None
    
    def upload_file(self, file, folder: str = "resources") -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Upload a file to Supabase Storage
        
        Args:
            file: Django UploadedFile object
            folder: Folder path in the bucket (default: "resources")
        
        Returns:
            Tuple of (success: bool, file_url: str or None, error_message: str or None)
        """
        if not self.supabase:
            return False, None, "Supabase is not configured"
        
        try:
            # Generate unique filename
            file_extension = os.path.splitext(file.name)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = f"{folder}/{unique_filename}"
            
            # Read file content
            file_content = file.read()
            
            # Get mime type
            mime_type, _ = mimetypes.guess_type(file.name)
            if not mime_type:
                mime_type = 'application/octet-stream'
            
            # Upload to Supabase
            response = self.supabase.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=file_content,
                file_options={"content-type": mime_type}
            )
            
            # Get public URL
            file_url = self.supabase.storage.from_(self.bucket_name).get_public_url(file_path)
            
            return True, file_url, None
            
        except Exception as e:
            return False, None, str(e)
    
    def delete_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Delete a file from Supabase Storage
        
        Args:
            file_path: Path to the file in the bucket
        
        Returns:
            Tuple of (success: bool, error_message: str or None)
        """
        if not self.supabase:
            return False, "Supabase is not configured"
        
        try:
            # Extract path from URL if full URL is provided
            if file_path.startswith('http'):
                # Parse the path from the URL
                parts = file_path.split(f'/storage/v1/object/public/{self.bucket_name}/')
                if len(parts) > 1:
                    file_path = parts[1]
            
            self.supabase.storage.from_(self.bucket_name).remove([file_path])
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """
        Get file information from Supabase Storage
        
        Args:
            file_path: Path to the file in the bucket
        
        Returns:
            Dictionary with file info or None
        """
        if not self.supabase:
            return None
        
        try:
            files = self.supabase.storage.from_(self.bucket_name).list(path=file_path)
            if files and len(files) > 0:
                return files[0]
            return None
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None
    
    def list_files(self, folder: str = "") -> list:
        """
        List all files in a folder
        
        Args:
            folder: Folder path in the bucket
        
        Returns:
            List of file information dictionaries
        """
        if not self.supabase:
            return []
        
        try:
            files = self.supabase.storage.from_(self.bucket_name).list(path=folder)
            return files
        except Exception as e:
            print(f"Error listing files: {e}")
            return []


# Global instance
supabase_storage = SupabaseStorage()
