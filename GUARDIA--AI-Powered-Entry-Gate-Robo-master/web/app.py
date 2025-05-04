from flask import Flask, render_template, session, redirect, url_for, request, flash
import mysql.connector
from mysql.connector import pooling
from config import DATABASE, APP_SECRET_KEY
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='user_images/')
app.secret_key = APP_SECRET_KEY
# Database configuration
connection_pool = mysql.connector.pooling.MySQLConnectionPool(**DATABASE, pool_name='web_pool', pool_size=5)

# Function to fetch all users from the database
def fetch_all_users():
    conn = connection_pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, name, mobile FROM users')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users

# Route to display the home page
@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('show_users'))
    return render_template('home.html')

# Route to handle user login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['email']
    password = request.form['password']
    conn = connection_pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM super_users WHERE email = %s', (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user and check_password_hash(user['password'], password):
        session['user'] = username
        return redirect(url_for('show_users'))
    else:
        flash('Invalid credentials', 'error')
        return redirect(url_for('home'))

# Route to handle user logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

# Route to display all users
@app.route('/users')
def show_users():
    if 'user' not in session:
        return redirect(url_for('home'))
    users = fetch_all_users()
    return render_template('users.html', users=users)

# Route to display a user's entry logs
@app.route('/user_entries/<int:user_id>')
def show_user_entries(user_id):
    if 'user' not in session:
        return redirect(url_for('home'))
    conn = connection_pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    query = '''
        SELECT entries.*, users.name, users.mobile 
        FROM entries 
        JOIN users ON entries.user_id = users.id 
        WHERE entries.user_id = %s
    '''
    cursor.execute(query, (user_id,))
    entries_with_user_details = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('entries.html', entries=entries_with_user_details, title='User Entries')

@app.route('/entries')
def show_entries():
    if 'user' not in session:
        return redirect(url_for('home'))
    conn = connection_pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    query = '''
        SELECT entries.*, users.name, users.mobile 
        FROM entries 
        JOIN users ON entries.user_id = users.id
    '''
    cursor.execute(query)
    entries_with_user_details = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('entries.html', entries=entries_with_user_details, title='All Entries')

@app.route('/user_images/<path:path>')
def get_user_image(path):
    return app.send_static_file(path)

if __name__ == '__main__':
    app.run(debug=True)
