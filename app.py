from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, send_from_directory
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mysqldb import MySQL


app = Flask(__name__)

app.secret_key = 'cekson123'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'dbcrud'
app.config['UPLOAD_FOLDER'] = 'static/upload'
mysql = MySQL(app)

@app.route('/', methods=['GET'])
def start():
    return render_template('start.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user_data WHERE username=%s', [username])
        akun = cursor.fetchone()
        if akun is None:
            cursor.execute('INSERT INTO user_data(username, password) VALUES (%s,%s)', ([username], generate_password_hash(password)))
            mysql.connection.commit()
            return redirect(url_for('login'))
        else:
            flash('Username sudah diambil, silahkan pilih username lain', 'danger')
    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user_data WHERE username=%s', ([username]))
        akun  = cursor.fetchone()
        if akun is None:
            flash('Login Gagal, Cek Username anda', 'danger')
        elif not check_password_hash(akun[2], password):
            flash('Login Gagal, Cek Password anda', 'danger')
        else:
            session['loggedin'] = True
            session['username'] = akun[1]
            session['user_id'] = akun[0]
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/home', methods=['GET','POST'])
def home():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        if request.method == 'POST':
            new_task = request.form['task']
            cursor.execute('INSERT INTO user_task(user_id,task) VALUES ( %s, %s )',(session['user_id'], new_task))
            mysql.connection.commit()
            flash('Penambahan Berhasil','success')
        cursor.execute('SELECT * FROM user_task WHERE user_id=%s ORDER BY date_created DESC', ([session['user_id']]))
        user_tasks = cursor.fetchall()
        username = session['username']
        return render_template('home.html', user_tasks = user_tasks, username = username)
    else:
        flash('Harap Login Dahulu','danger')
        return redirect(url_for('login'))

@app.route('/delete/<int:id>')
def delete(id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        try:
            cursor.execute('DELETE FROM user_task WHERE task_id=%s', ([id]))
            mysql.connection.commit()
            flash('Penghapusan Berhasil', category='success')
            return redirect(url_for('home'))
        except:
            flash('Penghapusan Tidak berhasil', 'danger')
            return redirect(url_for('home'))

@app.route('/update/<int:tid>', methods=['GET','POST'])
def update(tid):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user_task WHERE task_id=%s', ([tid]))
        task_to_update = cursor.fetchone()
        if request.method == 'POST':
            updated_task = request.form['task']
            cursor.execute('UPDATE user_task SET task = %s WHERE task_id=%s',(updated_task, [id]))
            mysql.connection.commit()
            flash('Pengubahan Berhasil', category='success')
            return redirect(url_for('home'))
        else:
            return render_template('update.html', task = task_to_update)
    else:
        flash('Harap Login Dahulu', 'danger')
        return redirect(url_for('login'))

@app.route('/logout', methods=['GET','POST'])
def logout():
    if 'loggedin' in session:
        session.pop('username', default=None)
        session.pop('user_id', default=None)
        session.pop('loggedin')
        return redirect(url_for('start'))
    else:
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
