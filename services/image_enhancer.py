from PIL import Image
from io import BytesIO
import os
from typing import Tuple, Optional
from services.bfl_client import BFLClient
from app.config import settings
import uuid


class ImageEnhancer:
    def __init__(self):
        self.client = BFLClient()
        self.upload_dir = "uploads"
        self.enhanced_dir = "enhanced"
        
        # Create directories if they don't exist
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.enhanced_dir, exist_ok=True)
    
    def validate_image(self, image_data: bytes) -> Tuple[bool, Optional[str]]:
        """Validate image format and size."""
        try:
            img = Image.open(BytesIO(image_data))
            
            # Check format
            format = img.format.lower()
            allowed_formats = settings.allowed_extensions_list
            if format not in allowed_formats and format != 'jpeg' and 'jpg' not in allowed_formats:
                return False, f"Unsupported format: {format}"
            
            # Check size
            size_mb = len(image_data) / (1024 * 1024)
            if size_mb > settings.max_upload_size_mb:
                return False, f"Image too large: {size_mb:.1f}MB (max {settings.max_upload_size_mb}MB)"
            
            return True, None
            
        except Exception as e:
            return False, f"Invalid image: {str(e)}"
    
    def save_image(self, image_data: bytes, directory: str, filename: Optional[str] = None) -> str:
        """Save image to disk and return the path."""
        if not filename:
            filename = f"{uuid.uuid4()}.png"
        
        filepath = os.path.join(directory, filename)
        
        # Save the image
        img = Image.open(BytesIO(image_data))
        img.save(filepath, 'PNG')
        
        return filepath
    
    async def enhance_image(self, image_data: bytes, enhancement_type: str = "background_removal") -> Tuple[bytes, str]:
        """Enhance image using FLUX.1 and return enhanced image data and path."""
        # Validate image
        valid, error = self.validate_image(image_data)
        if not valid:
            raise ValueError(error)
        
        # Save original image
        original_path = self.save_image(image_data, self.upload_dir)
        
        # Enhance image using BFL
        prompt = "Product on clean white background, professional lighting" if enhancement_type == "background_removal" else "Enhanced product image with improved quality and lighting"
        enhanced_data = await self.client.generate_image_edit(image_data, prompt)
        
        # Save enhanced image
        enhanced_filename = f"enhanced_{os.path.basename(original_path)}"
        enhanced_path = self.save_image(enhanced_data, self.enhanced_dir, enhanced_filename)
        
        return enhanced_data, enhanced_path
    
    def resize_for_upload(self, image_data: bytes, max_size: Tuple[int, int] = (1024, 1024)) -> bytes:
        """Resize image for optimal upload to Replicate."""
        img = Image.open(BytesIO(image_data))
        
        # Calculate new size maintaining aspect ratio
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Convert back to bytes
        output = BytesIO()
        img.save(output, format='PNG')
        output.seek(0)
        
        return output.read()
    
    def get_image_path(self, image_path: str) -> str:
        """Get absolute path for the image."""
        return os.path.abspath(image_path)