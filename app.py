from flask import Flask, render_template, request, send_file, jsonify
import tc5x
import mc33
import ck3
import os
import svgutils.transform as sg
import random

app = Flask(__name__)

# Bufor przechowujący etykiety
buffered_labels = []

# Wymiary etykiet (szerokość i wysokość w mm)
LABEL_SIZES = {
    'tc5x': {'width': 55.590, 'height': 45.701},
    'mc33': {'width': 47.047, 'height': 20.205},
    'ck3': {'width': 62.021, 'height': 19.545}
}

# Wymiary obszaru roboczego (szerokość x wysokość w mm)
WORKSPACE_WIDTH = 430.0
WORKSPACE_HEIGHT = 900.0

# Margines pomiędzy etykietami w mm
MARGIN = 5.0

def generate_unique_filename(base_name):
    """Dodaje losową liczbę do nazwy pliku, aby była unikalna."""
    random_number = random.randint(1000, 9999)
    return base_name.replace('.svg', f'_{random_number}.svg')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_tc5x', methods=['POST'])
def process_tc5x():
    try:
        new_model = request.form['model']
        new_sn = request.form['sn']
        new_pn = request.form['pn']
        new_mfd = request.form['mfd']
        output_path = generate_unique_filename('static/edited_tc5x.svg')
        tc5x.edit_tc5x_label('tc5x.svg', output_path, new_model, new_sn, new_pn, new_mfd)

        if request.form.get('buffer') == 'true':
            buffered_labels.append((output_path, 'tc5x'))
            return jsonify(message="Etykieta dodana do bufora."), 200
        else:
            return send_file(output_path, as_attachment=True)
    except Exception as e:
        return f"An error occurred: {e}", 500

@app.route('/process_mc33', methods=['POST'])
def process_mc33():
    try:
        new_pn = request.form['pn']
        new_mfd = request.form['mfd']
        new_sn = request.form['sn']
        output_path = generate_unique_filename('static/edited_label.svg')
        mc33.edit_svg_label('label.svg', output_path, new_pn, new_mfd, new_sn)

        if request.form.get('buffer') == 'true':
            buffered_labels.append((output_path, 'mc33'))
            return jsonify(message="Etykieta dodana do bufora."), 200
        else:
            return send_file(output_path, as_attachment=True)
    except Exception as e:
        return f"An error occurred: {e}", 500

@app.route('/process_ck3', methods=['POST'])
def process_ck3():
    try:
        new_cn = request.form['cn']
        new_sn = request.form['sn']
        output_path = generate_unique_filename('static/edited_ck3.svg')
        ck3.edit_ck3_label('ck3.svg', output_path, new_cn, new_sn)

        if request.form.get('buffer') == 'true':
            buffered_labels.append((output_path, 'ck3'))
            return jsonify(message="Etykieta dodana do bufora."), 200
        else:
            return send_file(output_path, as_attachment=True)
    except Exception as e:
        return f"An error occurred: {e}", 500

@app.route('/download_all_labels', methods=['GET'])
def download_all_labels():
    try:
        if not buffered_labels:
            return "Brak etykiet do pobrania.", 400

        final_output = 'static/final_labels.svg'
        current_x = 0.0
        current_y = 0.0
        row_height = 0.0
        elements = []

        for label_path, label_type in buffered_labels:
            label_width = LABEL_SIZES[label_type]['width']
            label_height = LABEL_SIZES[label_type]['height']

            # Dodanie marginesu do szerokości etykiety
            label_width_with_margin = label_width + MARGIN
            label_height_with_margin = label_height + MARGIN

            # Sprawdź, czy etykieta zmieści się w obecnym rzędzie
            if current_x + label_width_with_margin > WORKSPACE_WIDTH:
                # Przenieś do nowego rzędu
                current_x = 0.0
                current_y += row_height  # Przesunięcie w pionie
                row_height = 0.0  # Reset row height for new row

            # Sprawdź, czy etykieta zmieści się na wysokości obszaru roboczego
            if current_y + label_height_with_margin > WORKSPACE_HEIGHT:
                return "Nie można umieścić więcej etykiet na obszarze roboczym.", 400

            # Przesuń element na odpowiednią pozycję
            root = sg.fromfile(label_path).getroot()
            root.moveto(current_x + MARGIN / 2, current_y + MARGIN / 2)
            elements.append(root)

            # Zaktualizuj pozycję poziomą i maksymalną wysokość wiersza
            current_x += label_width_with_margin
            row_height = max(row_height, label_height_with_margin)  # Ustawienie wysokości rzędu na podstawie najwyższej etykiety

        # Stworzenie finalnego pliku SVG z ustaloną szerokością i wysokością
        figure = sg.SVGFigure(f"{WORKSPACE_WIDTH}mm", f"{WORKSPACE_HEIGHT}mm")
        figure.append([*elements])  # Dodanie wszystkich elementów do figury
        figure.save(final_output)

        # Czyszczenie bufora
        buffered_labels.clear()

        return send_file(final_output, as_attachment=True)
    except Exception as e:
        return f"An error occurred: {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
