from PIL import Image, ImageDraw

def create_simple_map(path):
    # Create a blank white image
    width, height = 500, 500
    image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Draw grid lines
    for i in range(0, width, 50):
        draw.line((i, 0, i, height), fill=(0, 0, 0))
    for i in range(0, height, 50):
        draw.line((0, i, width, i), fill=(0, 0, 0))

    # Draw some obstacles
    draw.rectangle((100, 100, 150, 150), fill=(0, 0, 0))
    draw.rectangle((300, 300, 350, 350), fill=(0, 0, 0))

    # Save the image
    image.save(path)

create_simple_map('simple_map.png')
