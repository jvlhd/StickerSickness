import xml.etree.ElementTree as ET
import barcode
from barcode.writer import ImageWriter
import base64
from io import BytesIO
from PIL import Image, ImageChops

# Custom writer class to avoid text rendering below the barcode
class ImageWithoutTextWriter(ImageWriter):
    def _paint_text(self, xpos, ypos):
        pass

def trim_whitespace(image, bg_color):
    """Trim the specified background color from an image."""
    bg = Image.new(image.mode, image.size, bg_color)
    diff = ImageChops.difference(image, bg)
    bbox = diff.getbbox()
    if bbox:
        return image.crop(bbox)
    return image

def generate_barcode_image(data, width, height, fg_color, bg_color):
    CODE128 = barcode.get_barcode_class('code128')
    writer = ImageWithoutTextWriter()
    barcode_obj = CODE128(data, writer=writer)
    buffer = BytesIO()
    barcode_obj.write(buffer, {'module_width': 0.2, 'module_height': 15.0, 'quiet_zone': 1.0, 'font_size': 0, 'text_distance': 1.0, 'background': bg_color, 'foreground': fg_color})
    buffer.seek(0)
    img = Image.open(buffer)

    # Trim whitespace with background color
    img = trim_whitespace(img, bg_color)

    # Resize the image to the desired width and height using LANCZOS resampling
    img = img.resize((width, height), Image.LANCZOS)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

def edit_ck3_label(svg_file_path, output_svg_file_path, new_cn, new_sn):
    try:
        # Load the SVG file
        print("Loading SVG file...")
        tree = ET.parse(svg_file_path)
        root = tree.getroot()

        # Define namespaces (modify if your SVG uses different namespaces)
        namespaces = {'svg': 'http://www.w3.org/2000/svg'}

        # Function to replace text in an element
        def replace_text(element_id, new_text):
            found = False
            for elem in root.findall(f".//svg:text[@id='{element_id}']", namespaces):
                for tspan in elem.findall(f".//svg:tspan", namespaces):
                    tspan.text = new_text
                found = True
            if not found:
                print(f"Element with id '{element_id}' not found.")

        # Replace CN and SN
        print("Replacing CN...")
        replace_text('text4393-4-8', f'CN:{new_cn}')
        print("Replacing SN...")
        replace_text('text4389-8-2', f'SN:{new_sn}')

        # Function to replace barcode
        def replace_barcode(group_id, new_barcode_data, width, height, fg_color, bg_color, transform_matrix):
            found = False
            for group in root.findall(f".//svg:g[@id='{group_id}']", namespaces):
                found = True
                original_id = group.attrib.get('id')
                # Remove all existing barcode elements within the group
                for elem in list(group):
                    group.remove(elem)

                # Generate new barcode image
                print(f"Generating new barcode image for {group_id}...")
                barcode_image = generate_barcode_image(new_barcode_data, width, height, fg_color, bg_color)
                if barcode_image is None:
                    print("Failed to generate barcode image.")
                    return
                barcode_b64 = base64.b64encode(barcode_image).decode('utf-8')
                image_href = f"data:image/png;base64,{barcode_b64}"

                # Insert new barcode image
                image_elem = ET.Element('{http://www.w3.org/2000/svg}image', {
                    'id': f'{original_id}_image',
                    'x': '0',  # Adjusted position x
                    'y': '0',  # Adjusted position y
                    'width': str(width),  # Desired width in SVG
                    'height': str(height),  # Desired height in SVG
                    'href': image_href,
                    'preserveAspectRatio': 'none'
                })
                group.append(image_elem)
                group.set('transform', transform_matrix)
            if not found:
                print(f"Element with id '{group_id}' not found.")

        # Replace CN barcode with the same size as SN barcode
        print("Replacing CN barcode...")
        cn_transform_matrix = "matrix(0.22984615,0,0,0.1411,15.198503,22.832505)"  # Adjusted y position to move up
        replace_barcode('g2', new_cn, 150, 30, fg_color='#ffffff', bg_color='#00112b', transform_matrix=cn_transform_matrix)

        # Replace SN barcode
        print("Replacing SN barcode...")
        sn_transform_matrix = "matrix(0.22984615,0,0,0.1411,15.198503,26.832505)"  # Use the same matrix as before
        replace_barcode('barcode1-8-7', new_sn, 150, 30, fg_color='#ffffff', bg_color='#00112b', transform_matrix=sn_transform_matrix)

        # Write the modified SVG to a new file
        print("Saving the modified SVG file...")
        tree.write(output_svg_file_path)

        print("Done.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    new_cn = input("Enter new CN: ")
    new_sn = input("Enter new SN: ")

    edit_ck3_label('ck3.svg', 'edited_ck3.svg', new_cn, new_sn)
