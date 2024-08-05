import xml.etree.ElementTree as ET
import barcode
from barcode.writer import ImageWriter
import base64
from io import BytesIO
from PIL import Image, ImageChops

class ImageWithoutTextWriter(ImageWriter):
    def _paint_text(self, xpos, ypos):
        pass

def trim_whitespace(image):
    bg = Image.new(image.mode, image.size, (255, 255, 255))
    diff = ImageChops.difference(image, bg)
    bbox = diff.getbbox()
    if bbox:
        return image.crop(bbox)
    return image

def generate_barcode_image(data, width, height):
    CODE128 = barcode.get_barcode_class('code128')
    writer = ImageWithoutTextWriter()
    barcode_obj = CODE128(data, writer=writer)
    buffer = BytesIO()
    barcode_obj.write(buffer)
    buffer.seek(0)
    img = Image.open(buffer)
    img = trim_whitespace(img)
    img = img.resize((width, height), Image.LANCZOS)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

def edit_svg_label(svg_file_path, output_svg_file_path, new_pn, new_data, new_sn):
    try:
        tree = ET.parse(svg_file_path)
        root = tree.getroot()
        namespaces = {'svg': 'http://www.w3.org/2000/svg'}

        def replace_text(element_id, new_text):
            found = False
            for elem in root.findall(f".//svg:text[@id='{element_id}']", namespaces):
                for tspan in elem.findall(f".//svg:tspan", namespaces):
                    tspan.text = new_text
                    original_size = float(tspan.get('style').split('font-size:')[1].split('px')[0])
                    new_size = original_size * 0.9
                    tspan.set('style', tspan.get('style').replace(f'font-size:{original_size}px', f'font-size:{new_size}px'))
                found = True
            if not found:
                print(f"Element with id '{element_id}' not found.")

        replace_text('text6389-4-3-7-1-1-47-8-8-4', f'P/N: {new_pn}')
        replace_text('text6389-4-3-7-1-1-47-8-6-9', f'MFD : {new_data}')
        replace_text('text6389-4-3-7-1-1-47-8-69-9', f'(S)S/N: {new_sn}')

        def replace_barcode(group_id, new_barcode_data):
            found = False
            for group in root.findall(f".//svg:g[@id='{group_id}']", namespaces):
                found = True
                for elem in list(group):
                    group.remove(elem)
                barcode_image = generate_barcode_image(new_barcode_data, width=800, height=100)
                if barcode_image is None:
                    print("Failed to generate barcode image.")
                    return
                barcode_b64 = base64.b64encode(barcode_image).decode('utf-8')
                image_href = f"data:image/png;base64,{barcode_b64}"
                image_elem = ET.Element('{http://www.w3.org/2000/svg}image', {
                    'id': f'{group_id}_image',
                    'x': '0',
                    'y': '0',
                    'width': '100',
                    'height': '15',
                    'href': image_href,
                    'preserveAspectRatio': 'none'
                })
                group.append(image_elem)
            if not found:
                print(f"Element with id '{group_id}' not found.")

        replace_barcode('barcode4', new_sn)
        tree.write(output_svg_file_path)
        print("Done.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    new_pn = input("Enter new PN: ")
    new_data = input("Enter new MFD: ")
    new_sn = input("Enter new SN: ")
    edit_svg_label('label.svg', 'edited_label.svg', new_pn, new_data, new_sn)
