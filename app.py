from flask import Flask, render_template, request, send_file
import tc5x
import mc33
import ck3
import os

app = Flask(__name__)

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
        output_path = 'static/edited_tc5x.svg'
        tc5x.edit_tc5x_label('tc5x.svg', output_path, new_model, new_sn, new_pn, new_mfd)
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return f"An error occurred: {e}", 500

@app.route('/process_mc33', methods=['POST'])
def process_mc33():
    try:
        new_pn = request.form['pn']
        new_mfd = request.form['mfd']
        new_sn = request.form['sn']
        output_path = 'static/edited_label.svg'
        mc33.edit_svg_label('label.svg', output_path, new_pn, new_mfd, new_sn)
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return f"An error occurred: {e}", 500

@app.route('/process_ck3', methods=['POST'])
def process_ck3():
    try:
        new_cn = request.form['cn']
        new_sn = request.form['sn']
        output_path = 'static/edited_ck3.svg'
        ck3.edit_ck3_label('ck3.svg', output_path, new_cn, new_sn)
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return f"An error occurred: {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
