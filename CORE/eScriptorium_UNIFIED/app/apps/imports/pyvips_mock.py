# Mock pyvips for development without libvips
"""
This is a temporary mock to allow eScriptorium to run without libvips installed.
PDF/TIFF advanced import features will be disabled.
For full functionality, install libvips: see FIX_LIBVIPS_GUIDE.md
"""

class Image:
    """Mock Image class"""
    
    @staticmethod
    def new_from_file(*args, **kwargs):
        raise NotImplementedError(
            "libvips not installed - PDF/TIFF import requires libvips. "
            "See FIX_LIBVIPS_GUIDE.md for installation instructions."
        )
    
    def write_to_file(self, *args, **kwargs):
        raise NotImplementedError("libvips not installed")
    
    def write_to_buffer(self, *args, **kwargs):
        raise NotImplementedError("libvips not installed")

def __getattr__(name):
    """Catch-all for other pyvips attributes"""
    return lambda *args, **kwargs: None

# Provide some basic constants that might be referenced
BAND_FORMAT_UCHAR = 0
INTERPRETATION_RGB = 1
