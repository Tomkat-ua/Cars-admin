from flask import Flask, render_template, request, redirect, url_for,flash
import fbextract,os, platform, requests,json
from gevent.pywsgi import WSGIServer

app = Flask(__name__)
app.secret_key = os.getenv("PUSH_KEY")

local_ip         = os.getenv('LOCAL_IP','192.168.10.9')
server_port      = os.getenv('SERVER_PORT',3001)
url_to_cloud     = os.getenv('URL_TO_CLOUD')

@app.context_processor
def inject_globals():
    return dict(app_version=os.getenv("APP_VERSION"))

def get_db_connection():
    return fbextract.get_connection()

@app.route('/')
def index():
    q = request.args.get('q', '').strip()
    con = get_db_connection()
    cur = con.cursor()
    print(q)
    if q:
        cur.execute("""
            SELECT CAR_ID, MIL_NUM, CARTYPE_NAME, BRAND, DIVISION_NAME,
                   STATUS_NAME, STATE_NAME, SEATS, W_FORM, DRIVER, LOCATION, NOTES
            FROM V_CARS
            WHERE UPPER(MIL_NUM) LIKE UPPER(?)
            ORDER BY CAR_ID
            """, (f'{q}',))
    else:
        cur.execute("""
    select
    c.car_id,  c.mil_num,  t.cartype_name,  c.brand,  d.division_name, sta.status_name, ste.state_name,
    c.seats,  c.w_form, c.driver, c.location, c.notes
    from cars c
        inner join d_cartype t  on t.cartype_id = c.car_type_id
        inner join d_division d on d.division_id = c.division_id
        inner join d_status sta on sta.status_id = c.status_id
        inner join d_state  ste on ste.state_id  = c.state_id
     ORDER BY c.CAR_ID
            """)
    cars = cur.fetchall()
    con.close()

    return render_template('index.html', cars=cars)


@app.route('/add', methods=['GET', 'POST'])
def add_car():
    con = get_db_connection()
    cur = con.cursor()

    if request.method == 'POST':
        mil_num = request.form['mil_num']
        car_type_id = request.form['car_type_id']
        division_id = request.form['division_id']
        status_id = request.form['status_id']
        state_id = request.form['state_id']
        seats = request.form.get('seats', '')
        brand = request.form.get('brand', '')
        w_form = request.form.get('w_form', '')
        driver = request.form.get('driver', '')
        location = request.form.get('location', '')
        notes = request.form.get('notes', '')

        # Автоінкремент ID припустимо в базі, інакше треба отримати MAX+1
        cur.execute("""
            INSERT INTO CARS (MIL_NUM, CAR_TYPE_ID, DIVISION_ID, STATUS_ID, STATE_ID,
                              SEATS, BRAND, W_FORM, DRIVER, LOCATION, NOTES)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (mil_num, car_type_id, division_id, status_id, state_id,
              seats, brand, w_form, driver, location, notes))
        con.commit()
        con.close()
        return redirect(url_for('index'))

    # GET: отримати довідники для списків
    cur.execute("SELECT CARTYPE_ID, CARTYPE_NAME FROM D_CARTYPE ORDER BY CARTYPE_NAME")
    car_types = cur.fetchall()

    cur.execute("SELECT DIVISION_ID, DIVISION_NAME FROM D_DIVISION ORDER BY DIVISION_NAME")
    divisions = cur.fetchall()

    cur.execute("SELECT STATUS_ID, STATUS_NAME FROM  D_STATUS ORDER BY STATUS_NAME")
    statuses = cur.fetchall()

    cur.execute("SELECT STATE_ID, STATE_NAME FROM D_STATE  ORDER BY STATE_NAME")
    states = cur.fetchall()

    con.close()
    return render_template('edit_car.html', car=None,
                           car_types=car_types, divisions=divisions,
                           statuses=statuses, states=states)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_car(id):
    con = get_db_connection()
    cur = con.cursor()

    if request.method == 'POST':
        mil_num = request.form['mil_num']
        car_type_id = request.form['car_type_id']
        division_id = request.form['division_id']
        status_id = request.form['status_id']
        state_id = request.form['state_id']
        seats = request.form.get('seats', '')
        brand = request.form.get('brand', '')
        w_form = request.form.get('w_form', '')
        driver = request.form.get('driver', '')
        location = request.form.get('location', '')
        notes = request.form.get('notes', '')

        cur.execute("""
            UPDATE CARS SET
                MIL_NUM = ?, CAR_TYPE_ID = ?, DIVISION_ID = ?, STATUS_ID = ?, STATE_ID = ?,
                SEATS = ?, BRAND = ?, W_FORM = ?, DRIVER = ?, LOCATION = ?, NOTES = ?
            WHERE CAR_ID = ?
        """, (mil_num, car_type_id, division_id, status_id, state_id,
              seats, brand, w_form, driver, location, notes, id))
        con.commit()
        con.close()
        return redirect(url_for('index'))

    cur.execute("""
        SELECT MIL_NUM, CAR_TYPE_ID, DIVISION_ID, STATUS_ID, STATE_ID,
               SEATS, BRAND, W_FORM, DRIVER, LOCATION, NOTES
        FROM CARS WHERE CAR_ID = ?
    """, (id,))
    car = cur.fetchone()

    cur.execute("SELECT CARTYPE_ID, CARTYPE_NAME FROM D_CARTYPE ORDER BY CARTYPE_NAME")
    car_types = cur.fetchall()

    cur.execute("SELECT DIVISION_ID, DIVISION_NAME FROM D_DIVISION ORDER BY DIVISION_NAME")
    divisions = cur.fetchall()

    cur.execute("SELECT STATUS_ID, STATUS_NAME FROM  D_STATUS ORDER BY STATUS_NAME")
    statuses = cur.fetchall()

    cur.execute("SELECT STATE_ID, STATE_NAME FROM D_STATE  ORDER BY STATE_NAME")
    states = cur.fetchall()

    con.close()
    return render_template('edit_car.html', car=car,
                           car_types=car_types, divisions=divisions,
                           statuses=statuses, states=states)


@app.route('/delete/<int:id>', methods=['POST', 'GET'])
def delete_car(id):
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM CARS WHERE CAR_ID = ?", (id,))
    con.commit()
    con.close()
    return redirect(url_for('index'))

@app.route('/run-external')
def run_external():
    try:
        r = requests.get(url_to_cloud, timeout=20)
        result = json.loads(r.text) if r.text.startswith("[") else [r.text]
        for line in result:
            flash(line, "success")
    except Exception as e:
        flash(f"❌ Помилка: {e}", "danger")
    return redirect(url_for('index'))

if __name__ == "__main__":
    if platform.system() == 'Windows':
        http_server = WSGIServer((local_ip, int(server_port)), app)
        print(f"Running HTTP-SERVER on port - http://" + local_ip + ':' + str(server_port))
    else:
        http_server = WSGIServer(('', int(server_port)), app)
        print(f"Running HTTP-SERVER on port :" + str(server_port))
    http_server.serve_forever()
