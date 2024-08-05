from flask import Flask, render_template, request, send_file
import tc5x
import mc33
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_tc5x', methods=['POST'])
def process_tc5x():
    new_model = request.form['model']
    new_sn = request.form['sn']
    new_pn = request.form['pn']
    new_mfd = request.form['mfd']
    tc5x.edit_tc5x_label('tc5x.svg', 'edited_tc5x.svg', new_model, new_sn, new_pn, new_mfd)
    return send_file('edited_tc5x.svg', as_attachment=True)

@app.route('/process_mc33', methods=['POST'])
def process_mc33():
    new_pn = request.form['pn']
    new_mfd = request.form['mfd']
    new_sn = request.form['sn']
    mc33.edit_svg_label('label.svg', 'edited_label.svg', new_pn, new_mfd, new_sn)
    return send_file('edited_label.svg', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
