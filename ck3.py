import xml.etree.ElementTree as ET
import barcode
from barcode.writer import SVGWriter
from io import BytesIO

# Custom writer class to avoid adding background rect
class CustomSVGWriter(SVGWriter):
    def _init(self, code):
        super()._init(code)
        self._code = code

    def _paint_background(self, code):
        # Override to do nothing and avoid adding the background rect
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

    # Remove the unnecessary rect element if it exists
    svg_data = svg_data.replace('<rect width="100%" height="100%" style="fill:#00112b"/>', '')
    return svg_data

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
        def replace_barcode(group_id, new_barcode_data, module_width, module_height, fg_color, transform_matrix):
            found = False
            for group in root.findall(f".//svg:g[@id='{group_id}']", namespaces):
                found = True
                original_id = group.attrib.get('id')
                # Remove all existing barcode elements within the group
                for elem in list(group):
                    group.remove(elem)

                # Generate new barcode image
                print(f"Generating new barcode image for {group_id}...")
                barcode_svg = generate_barcode_svg(new_barcode_data, module_width, module_height, fg_color)
                if barcode_svg is None:
                    print("Failed to generate barcode image.")
                    return

                # Insert new barcode SVG
                barcode_elem = ET.fromstring(barcode_svg)
                for element in barcode_elem:
                    group.append(element)
                group.set('transform', transform_matrix)
            if not found:
                print(f"Element with id '{group_id}' not found.")

        # Replace CN barcode with adjusted dimensions
        print("Replacing CN barcode...")
        cn_transform_matrix = "matrix(0.15,0,0,0.1,15.198503,19.832505)"  # Adjusted transformation matrix for size
        replace_barcode('g2', new_cn, 0.35, 10.0, fg_color='#ffffff', transform_matrix=cn_transform_matrix)

        # Replace SN barcode with adjusted dimensions
        print("Replacing SN barcode...")
        sn_transform_matrix = "matrix(0.15,0,0,0.1,15.198503,26.832505)"  # Adjusted transformation matrix for size
        replace_barcode('barcode1-8-7', new_sn, 0.35, 10.0, fg_color='#ffffff', transform_matrix=sn_transform_matrix)

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
