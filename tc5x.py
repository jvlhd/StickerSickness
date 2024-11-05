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
                # Opcjonalnie dostosuj pozycję `transform`, aby skorygować wyrównanie tekstu
                transform = elem.attrib.get('transform')
                if transform:
                    # Skoryguj wartość `transform` lub dostosuj według potrzeb
                    corrected_transform = transform.replace('translate(', 'matrix(1,0,0,1,') # Przykład poprawki
                    elem.set('transform', corrected_transform)
                found = True
            if not found:
                print(f"Element with id '{element_id}' not found.")

        replace_text('text14478-6-3-4', new_model)
        replace_text('text14478-6-7', f'R-C-ZTC-{new_model}')
        replace_text('text14478-6-3-49', f'P/N: {new_pn}')
        replace_text('text14478-6-3-49-6', f'(S) S/N: {new_sn}')

        def replace_barcode(group_id, new_barcode_data, module_width, module_height, fg_color, transform_matrix):
            found = False
            for group in root.findall(f".//svg:g[@id='{group_id}']", namespaces):
                found = True
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

        # Replacing barcode with correct module width and height
        replace_barcode('barcode1', new_sn, 0.2, 8.2, '#000000', 'matrix(0.264583,0,0,0.08456667,25.433834,27.050066)')

        def replace_datamatrix(group_id, new_data, size):
            found = False
            for group in root.findall(f".//svg:g[@id='{group_id}']", namespaces):
                found = True
                for elem in list(group):
                    group.remove(elem)

                datamatrix_image = generate_datamatrix_svg(new_data, size)
                if datamatrix_image is None:
                    print("Failed to generate datamatrix image.")
                    return

                datamatrix_b64 = base64.b64encode(datamatrix_image).decode('utf-8')
                image_href = f"data:image/png;base64,{datamatrix_b64}"
                image_elem = ET.Element('{http://www.w3.org/2000/svg}image', {
                    'id': f'{group_id}_image',
                    'x': '10',
                    'y': '13',
                    'width': '64',
                    'height': '64',
                    'href': image_href,
                    'preserveAspectRatio': 'xMidYMid meet'
                })
                group.append(image_elem)
            if not found:
                print(f"Element with id '{group_id}' not found.")

        replace_datamatrix('g12032-5', new_mfd, (32, 32))
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
