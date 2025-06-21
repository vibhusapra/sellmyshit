from PIL import Image, ImageDraw, ImageFont
import os

# Create a simple test image
img = Image.new('RGB', (800, 600), color='white')
draw = ImageDraw.Draw(img)

# Draw a simple coffee grinder representation
draw.rectangle([200, 100, 600, 400], fill='black', outline='gray')
draw.rectangle([250, 150, 550, 250], fill='lightgray', outline='black')
draw.text((300, 450), "Test Coffee Grinder", fill='black')

# Save the image
os.makedirs("uploads", exist_ok=True)
img.save("uploads/test_coffee_grinder.jpg", "JPEG", quality=85)
print("✅ Test image created: uploads/test_coffee_grinder.jpg")