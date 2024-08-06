import xml.etree.ElementTree as ET
import barcode
from barcode.writer import SVGWriter
from io import BytesIO
import base64
from PIL import Image
from pylibdmtx.pylibdmtx import encode

class CustomSVGWriter(SVGWriter):
    def _init(self, code):
        super()._init(code)
        self._code = code

    def _paint_background(self, code):
        pass

def generate_barcode_svg(data, module_width, module_height, fg_color):
    CODE128 = barcode.get_barcode_class('code128')
    writer = CustomSVGWriter()

    barcode_obj = CODE128(data, writer=writer)
    buffer = BytesIO()
    barcode_obj.write(buffer, {
        'module_width': module_width,
        'module_height': module_height,
        'quiet_zone': 1.0,
        'font_size': 0,
        'text_distance': 1.0,
        'background': None,
        'foreground': fg_color,
    })
    buffer.seek(0)
    svg_data = buffer.getvalue().decode('utf-8')

    # Remove any rect elements
    svg_data = svg_data.replace('<rect width="100%" height="100%" style="fill:none"/>', '')
    svg_data = svg_data.replace('<rect width="100%" height="100%" style="fill:None"/>', '')

    return svg_data

def generate_datamatrix_svg(data, size):
    encoded = encode(data.encode('utf-8'))
    img = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    img = Image.open(buffer)
    img = img.resize(size, Image.LANCZOS)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

def edit_ck3_label(svg_file_path, output_svg_file_path, new_cn, new_sn):
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

        replace_text('text4393-4-8', f'CN:{new_cn}')
        replace_text('text4389-8-2', f'SN:{new_sn}')

        def replace_barcode(group_id, new_barcode_data, module_width, module_height, fg_color, transform_matrix):
            found = False
            for group in root.findall(f".//svg:g[@id='{group_id}']", namespaces):
                found = True
                original_id = group.attrib.get('id')
                for elem in list(group):
                    group.remove(elem)

                barcode_svg = generate_barcode_svg(new_barcode_data, module_width, module_height, fg_color)
                if barcode_svg is None:
                    print("Failed to generate barcode image.")
                    return

                barcode_elem = ET.fromstring(barcode_svg)
                for element in barcode_elem:
                    group.append(element)
                group.set('transform', transform_matrix)
            if not found:
                print(f"Element with id '{group_id}' not found.")

        # Replace CN barcode with adjusted dimensions
        print("Replacing CN barcode...")
        cn_transform_matrix = "matrix(0.15,0,0,0.1,15.198503,19.832505)"  # Adjusted transformation matrix for size
        replace_barcode('g2', new_cn, 0.45, 10.0, fg_color='#ffffff', transform_matrix=cn_transform_matrix)

        # Replace SN barcode with adjusted dimensions
        print("Replacing SN barcode...")
        sn_transform_matrix = "matrix(0.15,0,0,0.1,15.198503,26.832505)"  # Adjusted transformation matrix for size
        replace_barcode('barcode1-8-7', new_sn, 0.45, 10.0, fg_color='#ffffff', transform_matrix=sn_transform_matrix)

        # Write the modified SVG to a new file
        tree.write(output_svg_file_path)

        print("Done.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    new_cn = input("Enter new CN: ")
    new_sn = input("Enter new SN: ")

    edit_ck3_label('ck3.svg', 'edited_ck3.svg', new_cn, new_sn)
