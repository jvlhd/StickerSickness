from flask import Flask, url_for

app = Flask(__name__)


@app.route('/')
def index():
    return '''
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>Sticker Sickness</title>
        <!-- Bootstrap CSS -->
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        <!-- Custom CSS -->
        <link href="{}" rel="stylesheet">

        <!-- Favicon -->
        <link rel="apple-touch-icon" sizes="180x180" href="{}">
        <link rel="icon" type="image/png" sizes="32x32" href="{}">
        <link rel="icon" type="image/png" sizes="16x16" href="{}">
        <link rel="manifest" href="{}">
        <link rel="mask-icon" href="{}" color="#5bbad5">
        <meta name="msapplication-TileColor" content="#da532c">
        <meta name="theme-color" content="#ffffff">
      </head>
      <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
          <a class="navbar-brand" href="#">Sticker Sickness</a>
        </nav>
        <div class="container mt-5">
          <div class="row">
            <div class="col-md-6">
              <div class="card p-4 mb-4">
                <h2>Process TC5X Label</h2>
                <form action="/process_tc5x" method="post">
                  <div class="form-group">
                    <label for="model">Model:</label>
                    <input type="text" class="form-control" id="model" name="model">
                  </div>
                  <div class="form-group">
                    <label for="sn">SN:</label>
                    <input type="text" class="form-control" id="sn" name="sn">
                  </div>
                  <div class="form-group">
                    <label for="pn">PN:</label>
                    <input type="text" class="form-control" id="pn" name="pn">
                  </div>
                  <div class="form-group">
                    <label for="mfd">MFD:</label>
                    <input type="text" class="form-control" id="mfd" name="mfd">
                  </div>
                  <button type="submit" class="btn btn-primary">Process TC5X Label</button>
                </form>
              </div>
            </div>
            <div class="col-md-6">
              <div class="card p-4 mb-4">
                <h2>Process MC33 Label</h2>
                <form action="/process_mc33" method="post">
                  <div class="form-group">
                    <label for="pn">PN:</label>
                    <input type="text" class="form-control" id="pn" name="pn">
                  </div>
                  <div class="form-group">
                    <label for="mfd">MFD:</label>
                    <input type="text" class="form-control" id="mfd" name="mfd">
                  </div>
                  <div class="form-group">
                    <label for="sn">SN:</label>
                    <input type="text" class="form-control" id="sn" name="sn">
                  </div>
                  <button type="submit" class="btn btn-primary">Process MC33 Label</button>
                </form>
              </div>
            </div>
          </div>
        </div>
        <!-- Bootstrap JS and dependencies -->
        <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
      </body>
    </html>
    '''.format(
        url_for('static', filename='css/styles.css'),
        url_for('static', filename='apple-touch-icon.png'),
        url_for('static', filename='favicon-32x32.png'),
        url_for('static', filename='favicon-16x16.png'),
        url_for('static', filename='site.webmanifest'),
        url_for('static', filename='safari-pinned-tab.svg')
    )


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
