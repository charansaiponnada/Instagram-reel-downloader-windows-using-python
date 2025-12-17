#!/usr/bin/env python3
"""
Create an Instagram-themed icon for the app
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Create a new image with Instagram's gradient colors
width, height = 256, 256
image = Image.new('RGB', (width, height), color='white')
draw = ImageDraw.Draw(image, 'RGBA')

# Instagram gradient: purple to pink/orange
# Create a gradient background
for y in range(height):
    # Purple (#833AB4) to Red (#FD1D1D) gradient
    r = int(253 - (253 - 131) * (y / height))  # 253 to 131
    g = int(29 - (29 - 58) * (y / height))     # 29 to 58
    b = int(29 + (180 - 29) * (y / height))    # 29 to 180
    draw.rectangle([(0, y), (width, y+1)], fill=(r, g, b, 255))

# Draw a white rounded rectangle in the center for the symbol
margin = 30
rect_coords = [(margin, margin), (width - margin, height - margin)]
draw.rounded_rectangle(rect_coords, radius=40, fill=(255, 255, 255, 255), outline=(255, 255, 255, 255))

# Draw a play button (triangle) in the center for video/reel concept
play_margin = 80
play_x1 = width // 2 - 20
play_y1 = height // 2 - 30
play_x2 = width // 2 - 20
play_y2 = height // 2 + 30
play_x3 = width // 2 + 30
play_y3 = height // 2

# Draw play button triangle
draw.polygon([(play_x1, play_y1), (play_x2, play_y2), (play_x3, play_y3)], 
             fill=(253, 29, 29, 255), outline=(253, 29, 29, 255))

# Draw a musical note for audio
# Note head
note_x = width // 2 + 50
note_y = height // 2 - 20
draw.ellipse([(note_x - 8, note_y - 8), (note_x + 8, note_y + 8)], 
             fill=(131, 58, 180, 255), outline=(131, 58, 180, 255))

# Note stem
draw.line([(note_x + 8, note_y - 8), (note_x + 8, note_y - 35)], 
          fill=(131, 58, 180, 255), width=3)

# Note flag
draw.arc([(note_x + 8, note_y - 40), (note_x + 25, note_y - 20)], 
         0, 180, fill=(131, 58, 180, 255), width=3)

# Save as ICO
icon_path = os.path.join(os.path.dirname(__file__), 'app_icon.ico')
image.save(icon_path)
print(f"Icon created: {icon_path}")
