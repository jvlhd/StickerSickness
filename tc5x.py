import xml.etree.ElementTree as ET
import barcode
from barcode.writer import ImageWriter
import base64
from io import BytesIO
from PIL import Image, ImageChops
from pylibdmtx.pylibdmtx import encode

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

def generate_datamatrix_image(data, size):
    encoded = encode(data.encode('utf-8'))
    img = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
    img = img.resize(size, Image.LANCZOS)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

def edit_tc5x_label(svg_file_path, output_svg_file_path, new_model, new_sn, new_pn, new_mfd):
    try:
        tree = ET.parse(svg_file_path)
        root = tree.getroot()
        namespaces = {'svg': 'http://www.w3.org/2000/svg'}

        def replace_text(element_id, new_text):
            found = False
            for elem in root.findall(f".//svg:text[@id='{element_id}']", namespaces):
                for tspan in elem.findall(f".//svg:tspan", namespaces):
                    tspan.text = new_text
                found = True
            if not found:
                print(f"Element with id '{element_id}' not found.")

        replace_text('text14478-6-3-4', new_model)
        replace_text('text14478-6-7', f'R-C-ZTC-{new_model}')
        replace_text('text14478-6-3-49', f'P/N: {new_pn}')
        replace_text('text14478-6-3-49-6', f'(S) S/N: {new_sn}')

        def replace_barcode(group_id, new_barcode_data):
            found = False
            for group in root.findall(f".//svg:g[@id='{group_id}']", namespaces):
                found = True
                for elem in list(group):
                    group.remove(elem)
                barcode_image = generate_barcode_image(new_barcode_data, width=200, height=50)
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
                    'height': '25',
                    'href': image_href,
                    'preserveAspectRatio': 'none'
                })
                group.append(image_elem)
            if not found:
                print(f"Element with id '{group_id}' not found.")

        replace_barcode('barcode1', new_sn)

        def replace_datamatrix(group_id, new_data):
            found = False
            for group in root.findall(f".//svg:g[@id='{group_id}']", namespaces):
                found = True
                for elem in list(group):
                    group.remove(elem)
                datamatrix_image = generate_datamatrix_image(new_data, (64, 64))
                if datamatrix_image is None:
                    print("Failed to generate datamatrix image.")
                    return
                datamatrix_b64 = base64.b64encode(datamatrix_image).decode('utf-8')
                image_href = f"data:image/png;base64,{datamatrix_b64}"
                image_elem = ET.Element('{http://www.w3.org/2000/svg}image', {
                    'id': f'{group_id}_image',
                    'x': '10',
                    'y': '10',
                    'width': '64',
                    'height': '64',
                    'href': image_href,
                    'preserveAspectRatio': 'xMidYMid meet'
                })
                group.append(image_elem)
            if not found:
                print(f"Element with id '{group_id}' not found.")

        replace_datamatrix('g12032-5', new_mfd)
        tree.write(output_svg_file_path)
        print("Done.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    new_model = input("Enter new Model: ")
    new_sn = input("Enter new SN: ")
    new_pn = input("Enter new PN: ")
    new_mfd = input("Enter new MFD: ")
    edit_tc5x_label('tc5x.svg', 'edited_tc5x.svg', new_model, new_sn, new_pn, new_mfd)
