import xml.etree.ElementTree as ET
import barcode
from barcode.writer import SVGWriter
from io import BytesIO

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

def edit_svg_label(svg_file_path, output_svg_file_path, new_pn, new_mfd, new_sn):
    try:
        print("Loading SVG file...")
        tree = ET.parse(svg_file_path)
        root = tree.getroot()

        namespaces = {'svg': 'http://www.w3.org/2000/svg'}

        def replace_text(tspan_id, new_text):
            found = False
            for elem in root.findall(f".//svg:tspan[@id='{tspan_id}']", namespaces):
                elem.text = new_text
                found = True
            if not found:
                print(f"Element with id '{tspan_id}' not found.")

        print("Replacing PN...")
        replace_text('tspan6387-8-4-6-1-7-9-9-9-3', f'P/N: {new_pn}')
        print("Replacing MFD...")
        replace_text('tspan6387-8-4-6-1-7-9-9-6-7', f'MFD: {new_mfd}')
        print("Replacing SN...")
        replace_text('tspan6387-8-4-6-1-7-9-9-8-0', f'S/N: {new_sn}')

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

        print("Replacing barcode...")
        barcode_transform_matrix = "matrix(0.25220536,0,0,0.1,11.935956,20.979793)"  # Adjusting the matrix for smaller size
        replace_barcode('barcode4', new_sn, 0.28, 7.0, '#000000', barcode_transform_matrix)

        print("Saving the modified SVG file...")
        tree.write(output_svg_file_path)

        print("Done.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    new_pn = input("Enter new PN: ")
    new_mfd = input("Enter new MFD: ")
    new_sn = input("Enter new SN: ")

    edit_svg_label('label.svg', 'edited_label.svg', new_pn, new_mfd, new_sn)
