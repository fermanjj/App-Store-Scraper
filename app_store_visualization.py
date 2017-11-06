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
        
        <hr>
        
        <div class='row'>
            <h3>{{ main_results[1] }}</h3>
            <p>by <i>{{ main_results[9] }}</i></p>
            <div class='col-xs-6'>
                <h4>Information</h4>
                <div class='table-responsive'>
                    <table>
                        <tbody>
                            <tr>
                                <th>Price</th>
                                <td>{{ main_results[3] }}</td>
                            </tr>
                            <tr>
                                <th>Category</th>
                                <td>{{ main_results[4] }}</td>
                            </tr>
                            <tr>
                                <th>Date Published</th>
                                <td>{{ main_results[5] }}</td>
                            </tr>
                            <tr>
                                <th>Last Updated</th>
                                <td>{{ main_results[6] }}</td>
                            </tr>
                            <tr>
                                <th>Version</th>
                                <td>{{ main_results[7] }}</td>
                            </tr>
                            <tr>
                                <th>Size</th>
                                <td>{{ main_results[8] }}</td>
                            </tr>
                            <tr>
                                <th>Copyright</th>
                                <td>{{ main_results[10] }}</td>
                            </tr>
                            <tr>
                                <th>Rating</th>
                                <td>{{ main_results[11] }}</td>
                            </tr>
                            <tr>
                                <th>Compatibility</th>
                                <td>{{ main_results[12] }}</td>
                            </tr>
                            <tr>
                                <th>Current Version Rating</th>
                                <td>{{ main_results[13] }} from {{ main_results[14] }} ratings</td>
                            </tr>
                            <tr>
                                <th>All Versions Rating</th>
                                <td>{{ main_results[15] }} from {{ main_results[16] }} ratings</td>
                            </tr>
                            <tr>
                                <th>Languages</th>
                                <td>{% for lang in lang_results %}{{ lang[1] }}{% if not loop.last %}, {% endif %}{% endfor %}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div class='col-xs-6'>
                <h4>Description</h4>
                <p>{{ main_results[2] | replace('\n', '<br/>')|safe() }}</p>
            </div>
            
        </div>
        <div class='row'>
            <div class='col-xs-6'>
                <h4>Top In-App Purchases</h4>
                <ol>
                    {% for purc in purc_results %}
                        <li>{{ purc[2] }} - {{ purc[3] }}</li>
                    {% endfor %}
                </ol>
            </div>
            <div class='col-xs-6'>
                <h4>Customer Reviews</h4>
                {% for cust in cust_results %}
                    <div><b>{{ cust[1] }}</b> - {{ cust[2] }}, by {{ cust[3] }}<p>{{ cust[4] }}</p></div>
                    {{ cust }}
                {% endfor %}
            </div>
        </div>
        
        </div>
    </html>
    """
    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM app_store_main WHERE app_id = ?""", (id,))
        main_results = cursor.fetchone()
        cursor.execute("""SELECT * FROM app_store_languages WHERE app_id = ?""", (id,))
        language_results = cursor.fetchall()
        cursor.execute("""SELECT * FROM app_store_customer_reviews WHERE app_id = ?""", (id,))
        customer_review_results = cursor.fetchall()
        cursor.execute("""SELECT * FROM app_store_top_in_app_purchases WHERE app_id = ?""", (id,))
        in_app_purchase_results = cursor.fetchall()
    return render_template_string(
        html, main_results=main_results, lang_results=language_results,
        cust_results=customer_review_results, purc_results=in_app_purchase_results
    )


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
