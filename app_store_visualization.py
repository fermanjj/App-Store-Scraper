import sqlite3
from flask import Flask, render_template_string, jsonify, request


app = Flask(__name__)
db = 'app_store_db'


@app.route('/ajax_apps', methods=["POST"])
def ajax_apps():
    string = request.form['string']
    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """select app_id, app_name from app_store_main
            WHERE app_name like ?
            """, ('%'+string+'%',)
        )
        r = cursor.fetchall()
    return jsonify(r)


@app.route('/app_id/<id>')
def app_id(id):
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <title>App Store App</title>
      <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
      <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
      <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
    
    </head>
    <body>
        <div class='container'>
        
        <h1>App Store App</h1>
        
        
        </div>
    </html>
    """
    return render_template_string(html)


@app.route('/')
def index():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <title>App Store Apps</title>
      <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
      <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
      <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
    
    </head>
    <body>
        <div class='container'>
        
        <h1>App Store Apps</h1>
        <p>Start by searching for an app</p>
        <form>
          <div class="input-group">
            <input type="text" class="form-control" placeholder="Search">
            <div class="input-group-btn">
              <button class="btn btn-default" type="submit" onclick='search(); return false'>
                <i class="glyphicon glyphicon-search"></i>
              </button>
            </div>
          </div>
        </form>
        <div class='table-responsive'>
            <table class='table'>
                <thead>
                <tr>
                    <th>App</th>
                </tr>
                </thead>
                <tbody>
                    <tr>
                        <td></td>
                    </tr>
                </tbody>
            </table>
        </div>
        </div>
    </body>
    <script>
        function successAjax(d){
            var tbody = $('tbody');
            for (i = 0; i < d.length; i++) { 
                tbody.append("<tr><td><a href='/app_id/"+d[i][0]+"'>"+d[i][1]+"</a></td></tr>")
            }
        }
        function search() {
          var tbody = $('tbody');
          tbody.html('');
          $.ajax({
            url: '/ajax_apps',
            type: 'POST',
            data: {'string': $('input').val()},
            success: successAjax
          })
        }
    </script>
    </html>
    """
    return render_template_string(html)


if __name__ == '__main__':
    app.run('0.0.0.0', 5000, True)
