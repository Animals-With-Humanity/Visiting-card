from flask import Flask, render_template, request, redirect, url_for
from utils import get_db_connection, upload_image

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

        # Handle profile (avatar) image
        profile_img_file = request.files.get('profile_image')
        if profile_img_file and profile_img_file.filename:
            profile_image_url = upload_image(profile_img_file)
        else:
            # If no file uploaded, store an empty string or a default if you want
            profile_image_url = ""

        # Handle background/cover image
        background_img_file = request.files.get('background_image')
        if background_img_file and background_img_file.filename:
            background_image_url = upload_image(background_img_file)
        else:
            # Use the new placeholder by default
            background_image_url = "https://images.pexels.com/photos/30861264/pexels-photo-30861264.jpeg"

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
