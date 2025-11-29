import os
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils.deconstruct import deconstructible
from supabase import create_client, Client
import mimetypes

@deconstructible
class SupabaseMediaStorage(Storage):
    """
    Custom Django Storage backend for Supabase Storage.
    """
    def __init__(self):
        self.supabase_url = getattr(settings, 'SUPABASE_URL', None)
        # Try Service Key first (for uploads), then Anon Key/Key
        self.supabase_key = (
            getattr(settings, 'SUPABASE_SERVICE_KEY', None) or 
            getattr(settings, 'SUPABASE_ANON_KEY', None) or 
            getattr(settings, 'SUPABASE_KEY', None)
        )
        self.bucket_name = getattr(settings, 'SUPABASE_BUCKET', 'papertrail-storage')
        
        if self.supabase_url and self.supabase_key:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        else:
            self.supabase = None

    def _open(self, name, mode='rb'):
        # Supabase doesn't support opening files like a filesystem.
        # We would need to download the file to a temporary location or memory.
        # For now, we'll raise NotImplementedError as most image serving is done via URL.
        raise NotImplementedError("Opening files directly from Supabase is not supported yet.")

    def _save(self, name, content):
        """
        Uploads the file to Supabase Storage.
        """
        if not self.supabase:
            raise Exception("Supabase credentials not configured in settings.")

        # Clean the name (remove leading slashes)
        name = name.lstrip('/')
        
        # Read content
        content_bytes = content.read()
        
        # Guess mime type
        content_type, _ = mimetypes.guess_type(name)
        if not content_type:
            content_type = 'application/octet-stream'
            
        file_options = {"content-type": content_type}

        # Upload
        # Note: upsert=True overwrites existing files with same name
        res = self.supabase.storage.from_(self.bucket_name).upload(
            path=name,
            file=content_bytes,
            file_options=file_options
        )
        
        return name

    def exists(self, name):
        """
        Checks if a file exists in Supabase.
        """
        if not self.supabase:
            return False
            
        name = name.lstrip('/')
        # Supabase list method to check existence
        # This is a bit expensive, so we might want to optimize or assume False for unique names
        # But for correctness:
        directory = os.path.dirname(name)
        filename = os.path.basename(name)
        
        try:
            files = self.supabase.storage.from_(self.bucket_name).list(directory)
            for f in files:
                if f['name'] == filename:
                    return True
        except Exception:
            pass
            
        return False

    def url(self, name):
        """
        Returns the public URL for the file.
        """
        if not self.supabase:
            return name
            
        name = name.lstrip('/')
        return self.supabase.storage.from_(self.bucket_name).get_public_url(name)

    def delete(self, name):
        """
        Deletes the file from Supabase.
        """
        if not self.supabase:
            return
            
        name = name.lstrip('/')
        self.supabase.storage.from_(self.bucket_name).remove([name])
