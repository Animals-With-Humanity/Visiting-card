from flask import Flask, render_template, request, redirect, url_for
from utils import upload_image,get_db_connection

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        image = request.files['image']

        if image:
            image_url=upload_image(image)
        else:
            image_url = ""

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, email, phone, image_url) VALUES (%s, %s, %s, %s) RETURNING id", (name, email, phone, image_url))
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        return redirect(url_for('profile', user_id=user_id))
    
    return render_template('submit.html')

@app.route('/<int:user_id>')
def profile(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, phone, image_url FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    
    if user:
        return render_template('profile.html', user=user)
    else:
        return "User not found", 404

if __name__ == '__main__':
    app.run(debug=True)
