from flask import Flask, render_template, request, redirect, url_for,jsonify
from utils import get_db_connection,upload_file
app = Flask(__name__)

@app.route('/')
def index():
    """
    Renders the Tailwind + glassmorphism index page (welcome page).
    """
    return render_template('index.html')


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    """
    Show a form (GET) and handle form submission (POST).
    Fields: name, role, contact, whatsapp, about,
            work_email, personal_email, linkedin, instagram,
            profile_image (file), background_image (file).
    All are required (except file uploads, see note below).
    """
    if request.method == 'POST':
        # Required text fields
        name = request.form['name']  # Required => if missing, KeyError
        role = request.form['role']  # Changed from "Position" to "Role at AwH"
        contact = request.form['contact']
        whatsapp = request.form['whatsapp']
        about = request.form['about']
        work_email = request.form.get('work_email', 'team@awhbharat.org') or "team@awhbharat.org"
        personal_email = request.form['personal_email']
        linkedin = request.form['linkedin']
        instagram = request.form['instagram']
        profile_image_url=request.form["profile_image"]
        background_image_url=request.form['background_image']
        # Insert into DB
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users
                (name, role, contact, whatsapp, about,
                 work_email, personal_email, linkedin, instagram,
                 image_url, background_image)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            name, role, contact, whatsapp, about,
            work_email, personal_email, linkedin, instagram,
            profile_image_url, background_image_url
        ))
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('profile', user_id=new_id))

    return render_template('submit.html')

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    file_url=upload_file(file)
    return jsonify({"public_url": file_url})

@app.route('/profile/<int:user_id>')
def profile(user_id):
    """
    Fetch the user from DB and display their final digital card.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            id, name, role, contact, whatsapp, about,
            work_email, personal_email, linkedin, instagram,
            image_url, background_image
        FROM users
        WHERE id = %s
    """, (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user:
        return "User not found", 404

    return render_template('profile.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)
