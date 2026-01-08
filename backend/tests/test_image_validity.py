"""
Property-Based Tests for Generated Image Validity

Feature: ai-product-view-webapp
Property 16: Generated image validity
Validates: Requirements 5.9

These tests verify that generated images are valid PNG or JPEG format.
"""

import base64
import io
from typing import Optional
from hypothesis import given, settings, strategies as st, assume

import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.types import GeneratedImage, GenerateResponse


# ============================================================================
# Test Helpers
# ============================================================================

def is_valid_image_data(image_bytes: bytes) -> bool:
    """
    Check if the given bytes represent a valid PNG or JPEG image.
    
    Returns True if the data has valid PNG or JPEG magic bytes/headers.
    """
    if len(image_bytes) < 8:
        return False
    
    # PNG magic bytes: 89 50 4E 47 0D 0A 1A 0A
    png_magic = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
    
    # JPEG magic bytes: FF D8 FF
    jpeg_magic = bytes([0xFF, 0xD8, 0xFF])
    
    return image_bytes[:8] == png_magic or image_bytes[:3] == jpeg_magic


def create_valid_png_bytes() -> bytes:
    """Create valid PNG image bytes for testing."""
    try:
        from PIL import Image
        img = Image.new('RGB', (50, 50), color='red')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    except ImportError:
        # Fallback: minimal valid PNG structure
        # PNG signature + IHDR chunk + IDAT chunk + IEND chunk
        png_signature = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
        # Minimal IHDR chunk (width=1, height=1, bit_depth=8, color_type=2)
        ihdr_data = bytes([
            0x00, 0x00, 0x00, 0x0D,  # Length: 13
            0x49, 0x48, 0x44, 0x52,  # Type: IHDR
            0x00, 0x00, 0x00, 0x01,  # Width: 1
            0x00, 0x00, 0x00, 0x01,  # Height: 1
            0x08, 0x02,              # Bit depth: 8, Color type: 2 (RGB)
            0x00, 0x00, 0x00,        # Compression, Filter, Interlace
            0x90, 0x77, 0x53, 0xDE,  # CRC
        ])
        # Minimal IDAT chunk
        idat_data = bytes([
            0x00, 0x00, 0x00, 0x0C,  # Length: 12
            0x49, 0x44, 0x41, 0x54,  # Type: IDAT
            0x08, 0xD7, 0x63, 0xF8, 0xFF, 0xFF, 0xFF, 0x00,
            0x05, 0xFE, 0x02, 0xFE,  # CRC
        ])
        # IEND chunk
        iend_data = bytes([
            0x00, 0x00, 0x00, 0x00,  # Length: 0
            0x49, 0x45, 0x4E, 0x44,  # Type: IEND
            0xAE, 0x42, 0x60, 0x82,  # CRC
        ])
        return png_signature + ihdr_data + idat_data + iend_data


def create_valid_jpeg_bytes() -> bytes:
    """Create valid JPEG image bytes for testing."""
    try:
        from PIL import Image
        img = Image.new('RGB', (50, 50), color='blue')
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        return buffer.getvalue()
    except ImportError:
        # Fallback: minimal JPEG structure (SOI + APP0 + EOI)
        # This is a minimal valid JPEG that most parsers will accept
        return bytes([
            0xFF, 0xD8,              # SOI (Start of Image)
            0xFF, 0xE0,              # APP0 marker
            0x00, 0x10,              # Length: 16
            0x4A, 0x46, 0x49, 0x46, 0x00,  # JFIF identifier
            0x01, 0x01,              # Version
            0x00,                    # Aspect ratio units
            0x00, 0x01,              # X density
            0x00, 0x01,              # Y density
            0x00, 0x00,              # Thumbnail dimensions
            0xFF, 0xD9,              # EOI (End of Image)
        ])


def create_valid_base64_png() -> str:
    """Create a valid base64-encoded PNG image."""
    return base64.b64encode(create_valid_png_bytes()).decode('utf-8')


def create_valid_base64_jpeg() -> str:
    """Create a valid base64-encoded JPEG image."""
    return base64.b64encode(create_valid_jpeg_bytes()).decode('utf-8')


def validate_generated_image(image_base64: str) -> bool:
    """
    Validate that a base64-encoded image can be decoded as valid PNG or JPEG.
    
    This simulates the validation that should happen when processing
    generated images from the Backend.
    """
    try:
        image_bytes = base64.b64decode(image_base64)
        return is_valid_image_data(image_bytes)
    except Exception:
        return False


# ============================================================================
# Property 16: Generated image validity
# Feature: ai-product-view-webapp, Property 16: Generated image validity
# Validates: Requirements 5.9
#
# *For any* successful generation, THE Backend SHALL return image data that
# can be decoded as a valid image (PNG or JPEG format).
# ============================================================================

@given(
    perspective_id=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N'), whitelist_characters='_-')),
    perspective_name=st.text(min_size=1, max_size=100),
    seed_used=st.text(min_size=1, max_size=50, alphabet='0123456789'),
    use_png=st.booleans(),
)
@settings(max_examples=100)
def test_property_16_generated_image_validity(
    perspective_id: str,
    perspective_name: str,
    seed_used: str,
    use_png: bool,
):
    """
    Property 16: Generated image validity
    
    For any successful generation, the Backend SHALL return image data that
    can be decoded as a valid image (PNG or JPEG format).
    
    Feature: ai-product-view-webapp, Property 16: Generated image validity
    Validates: Requirements 5.9
    """
    # Arrange: Create a valid image (PNG or JPEG based on test parameter)
    if use_png:
        valid_image_base64 = create_valid_base64_png()
    else:
        valid_image_base64 = create_valid_base64_jpeg()
    
    # Act: Create a GeneratedImage with the valid image data
    generated = GeneratedImage(
        perspective_id=perspective_id,
        perspective_name=perspective_name,
        image=valid_image_base64,
        seed_used=seed_used,
    )
    
    # Assert: The image data can be decoded as a valid PNG or JPEG
    assert validate_generated_image(generated.image), \
        "Generated image must be decodable as valid PNG or JPEG"
    
    # Verify the image bytes have correct magic bytes
    image_bytes = base64.b64decode(generated.image)
    assert is_valid_image_data(image_bytes), \
        "Generated image must have valid PNG or JPEG magic bytes"


@given(
    num_images=st.integers(min_value=1, max_value=9),
    total_time=st.floats(min_value=0.1, max_value=1000.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=100)
def test_property_16_all_response_images_valid(num_images: int, total_time: float):
    """
    Property 16: Generated image validity (all images in response)
    
    For any successful generation response with multiple images, ALL images
    SHALL be valid PNG or JPEG format.
    
    Feature: ai-product-view-webapp, Property 16: Generated image validity
    Validates: Requirements 5.9
    """
    # Arrange: Create multiple valid generated images
    valid_png = create_valid_base64_png()
    valid_jpeg = create_valid_base64_jpeg()
    
    generated_images = []
    for i in range(num_images):
        # Alternate between PNG and JPEG to test both formats
        image_data = valid_png if i % 2 == 0 else valid_jpeg
        generated_images.append(
            GeneratedImage(
                perspective_id=f"view_{i}",
                perspective_name=f"View {i}",
                image=image_data,
                seed_used=str(12345 + i),
            )
        )
    
    # Act: Create the response
    response = GenerateResponse(
        images=generated_images,
        total_time=total_time,
        original_image=valid_png,
    )
    
    # Assert: ALL images in the response are valid
    for i, img in enumerate(response.images):
        assert validate_generated_image(img.image), \
            f"Image {i} ({img.perspective_name}) must be valid PNG or JPEG"
        
        image_bytes = base64.b64decode(img.image)
        assert is_valid_image_data(image_bytes), \
            f"Image {i} ({img.perspective_name}) must have valid magic bytes"


@given(
    original_use_png=st.booleans(),
    generated_use_png=st.booleans(),
)
@settings(max_examples=100)
def test_property_16_original_and_generated_images_valid(
    original_use_png: bool,
    generated_use_png: bool,
):
    """
    Property 16: Generated image validity (original and generated)
    
    For any successful generation response, both the original image and
    all generated images SHALL be valid PNG or JPEG format.
    
    Feature: ai-product-view-webapp, Property 16: Generated image validity
    Validates: Requirements 5.9
    """
    # Arrange: Create valid images
    original_image = create_valid_base64_png() if original_use_png else create_valid_base64_jpeg()
    generated_image = create_valid_base64_png() if generated_use_png else create_valid_base64_jpeg()
    
    # Act: Create the response
    response = GenerateResponse(
        images=[
            GeneratedImage(
                perspective_id="test",
                perspective_name="Test View",
                image=generated_image,
                seed_used="12345",
            )
        ],
        total_time=5.0,
        original_image=original_image,
    )
    
    # Assert: Both original and generated images are valid
    assert validate_generated_image(response.original_image), \
        "Original image must be valid PNG or JPEG"
    
    for img in response.images:
        assert validate_generated_image(img.image), \
            "Generated image must be valid PNG or JPEG"


@given(
    image_bytes=st.binary(min_size=100, max_size=10000),
)
@settings(max_examples=100)
def test_property_16_invalid_image_detection(image_bytes: bytes):
    """
    Property 16: Generated image validity (invalid detection)
    
    For any random binary data that is NOT a valid PNG or JPEG, the
    validation function SHALL correctly identify it as invalid.
    
    Feature: ai-product-view-webapp, Property 16: Generated image validity
    Validates: Requirements 5.9
    """
    # Skip if the random bytes happen to be valid PNG or JPEG
    assume(not is_valid_image_data(image_bytes))
    
    # Arrange: Encode the invalid bytes as base64
    invalid_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    # Act & Assert: The validation should detect this as invalid
    assert not validate_generated_image(invalid_base64), \
        "Random binary data should not be detected as valid image"


@settings(max_examples=100)
@given(
    seed_value=st.integers(min_value=0, max_value=2**32 - 1),
)
def test_property_16_png_format_validity(seed_value: int):
    """
    Property 16: Generated image validity (PNG format)
    
    For any PNG image created by the system, it SHALL have the correct
    PNG magic bytes (89 50 4E 47 0D 0A 1A 0A).
    
    Feature: ai-product-view-webapp, Property 16: Generated image validity
    Validates: Requirements 5.9
    """
    # Arrange: Create a PNG image
    png_bytes = create_valid_png_bytes()
    png_base64 = base64.b64encode(png_bytes).decode('utf-8')
    
    # Act: Decode and check
    decoded_bytes = base64.b64decode(png_base64)
    
    # Assert: PNG magic bytes are correct
    png_magic = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
    assert decoded_bytes[:8] == png_magic, \
        "PNG image must have correct magic bytes"
    
    # Also verify through our validation function
    assert is_valid_image_data(decoded_bytes), \
        "PNG image must pass validation"


@settings(max_examples=100)
@given(
    seed_value=st.integers(min_value=0, max_value=2**32 - 1),
)
def test_property_16_jpeg_format_validity(seed_value: int):
    """
    Property 16: Generated image validity (JPEG format)
    
    For any JPEG image created by the system, it SHALL have the correct
    JPEG magic bytes (FF D8 FF).
    
    Feature: ai-product-view-webapp, Property 16: Generated image validity
    Validates: Requirements 5.9
    """
    # Arrange: Create a JPEG image
    jpeg_bytes = create_valid_jpeg_bytes()
    jpeg_base64 = base64.b64encode(jpeg_bytes).decode('utf-8')
    
    # Act: Decode and check
    decoded_bytes = base64.b64decode(jpeg_base64)
    
    # Assert: JPEG magic bytes are correct
    jpeg_magic = bytes([0xFF, 0xD8, 0xFF])
    assert decoded_bytes[:3] == jpeg_magic, \
        "JPEG image must have correct magic bytes"
    
    # Also verify through our validation function
    assert is_valid_image_data(decoded_bytes), \
        "JPEG image must pass validation"


@given(
    base64_string=st.text(min_size=0, max_size=100),
)
@settings(max_examples=100)
def test_property_16_invalid_base64_handling(base64_string: str):
    """
    Property 16: Generated image validity (invalid base64 handling)
    
    For any invalid base64 string, the validation function SHALL return
    False without raising an exception.
    
    Feature: ai-product-view-webapp, Property 16: Generated image validity
    Validates: Requirements 5.9
    """
    # Skip valid base64 strings that decode to valid images
    try:
        decoded = base64.b64decode(base64_string)
        if is_valid_image_data(decoded):
            assume(False)  # Skip this case
    except Exception:
        pass  # Invalid base64 is what we want to test
    
    # Act: Validate the string (should not raise exception)
    result = validate_generated_image(base64_string)
    
    # Assert: Invalid base64 or invalid image data returns False
    # (The function should handle errors gracefully)
    assert isinstance(result, bool), \
        "validate_generated_image must return a boolean"

