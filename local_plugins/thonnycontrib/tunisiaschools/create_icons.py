from PIL import Image
import os

# Paths
plugin_res = r"c:\Users\Walid\Desktop\thonnySc\local_plugins\thonnycontrib\tunisiaschools\res"

# Resize function to create square icons with padding
def resize_to_square(input_path, output_path, size):
    img = Image.open(input_path)
    
    # Create a square canvas with transparent background
    square_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    
    # Calculate scaling to fit within the square while maintaining aspect ratio
    img.thumbnail((size, size), Image.Resampling.LANCZOS)
    
    # Center the image on the square canvas
    offset = ((size - img.width) // 2, (size - img.height) // 2)
    square_img.paste(img, offset)
    
    # Save as PNG
    square_img.save(output_path, 'PNG', optimize=True)
    print(f"Created: {output_path} ({size}x{size})")

# Process Code PyQt icons
qt_input = os.path.join(plugin_res, "qt_32.png")
resize_to_square(qt_input, os.path.join(plugin_res, "code-pyqt.png"), 32)
resize_to_square(qt_input, os.path.join(plugin_res, "code-pyqt_2x.png"), 64)

# Process QT Designer icons
designer_input = os.path.join(plugin_res, "designer_32.png")
resize_to_square(designer_input, os.path.join(plugin_res, "qt-designer.png"), 32)
resize_to_square(designer_input, os.path.join(plugin_res, "qt-designer_2x.png"), 64)

print("\nAll icons created successfully!")
