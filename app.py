import os
import qrcode
import smtplib
from io import BytesIO
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Flask, flash, redirect, url_for, render_template, request, jsonify
from psycopg2 import IntegrityError
from dotenv import load_dotenv
from utils import get_db_connection, upload_file

app = Flask(__name__)

app.secret_key = os.getenv('FLASK_SECRET_KEY', 'fallback‑dev‑secret')


ZOHO_USER     = os.getenv('ZOHO_USER')
ZOHO_PASSWORD = os.getenv('ZOHO_PASSWORD')
BASE_URL      = os.getenv('BASE_URL').rstrip('/')

def send_profile_email(to_addr, name, profile_id):
    profile_url = f"{BASE_URL}/profile/{profile_id}"
    update_url  = f"{BASE_URL}/update/{profile_id}"

    # Generate QR
    qr = qrcode.QRCode(box_size=4, border=2)
    qr.add_data(profile_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    qr_img = MIMEImage(buf.read(), _subtype="png")
    qr_img.add_header('Content-ID', '<qrcode>')

    # Build HTML message
    html = f"""
    <html>
      <body style="font-family: sans-serif; color: #333;">
        <h2>Hello {name},</h2>
        <p>Your AWH digital visiting card is ready!</p>
        <p><a href="{profile_url}">View Your Profile</a></p>
        <p><a href="{update_url}">Update Your Card</a></p>
        <p>Or scan this QR code:</p>
        <img src="cid:qrcode" alt="QR code to profile"/>
        <p>Cheers,<br>AWH Team</p>
        <br>
        <br>
        <p>Sent with love,</p>
        <p>IT Team, Animals With Humanity</p>
      </body>
    </html>
    """

    msg = MIMEMultipart('related')
    msg['Subject'] = "Your AWH Digital Visiting Card"
    msg['From']    = ZOHO_USER
    msg['To']      = to_addr
    msg.attach(MIMEText(html, 'html'))
    msg.attach(qr_img)

    # Send via Zoho SMTP over SSL
    with smtplib.SMTP_SSL('smtp.zoho.in', 465) as smtp:
        smtp.login(ZOHO_USER, ZOHO_PASSWORD)
        smtp.send_message(msg)

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
    Prevents duplicates, then sends the profile+QR email.
    """
    if request.method == 'POST':
        # collect form data (same as before)…
        name             = request.form['name']
        role             = request.form['role']
        contact          = request.form['contact']
        whatsapp         = request.form['whatsapp']
        about            = request.form['about']
        work_email       = request.form.get('work_email', 'team@awhbharat.org') or "team@awhbharat.org"
        personal_email   = request.form['personal_email']
        linkedin = request.form.get('linkedin', '').strip()
        if not linkedin:
            linkedin = "https://www.linkedin.com/company/animals-with-humanity/"
        instagram = request.form.get('instagram', '').strip()
        if not instagram:
            instagram = "https://www.instagram.com/animalswithhumanity_/"


        profile_image    = request.form['profile_image']
        background_image = request.form['background_image']
        # validate the form data
        if not profile_image or profile_image == "error":
            flash("Please upload a profile image before submitting.")
            return redirect(url_for('submit'))
        if not background_image or background_image == "error":
            flash("Please upload a background image before submitting.")
            return redirect(url_for('submit'))
        conn = get_db_connection()
        cur  = conn.cursor()

        # duplicate check
        cur.execute(
            "SELECT id FROM users WHERE personal_email = %s AND contact = %s",
            (personal_email, contact)
        )
        if cur.fetchone():
            cur.close(); conn.close()
            flash(f"A profile with email “{personal_email}” and contact “{contact}” already exists.")
            return redirect(url_for('submit'))

        try:
            # insert
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
                profile_image, background_image
            ))
            new_id = cur.fetchone()[0]
            conn.commit()

            # send the email with QR code
            try:
                send_profile_email(personal_email, name, new_id)
                flash("Visiting Card created, please check your personal email.")
            except Exception as e:
                app.logger.error(f"Email send failed: {e}")
                flash("Profile created but email could not be sent.")

            cur.close(); conn.close()
            return redirect(url_for('profile', user_id=new_id))

        except IntegrityError:
            conn.rollback()
            cur.close(); conn.close()
            flash("Duplicate profile detected—unable to create.")
            return redirect(url_for('submit'))

        except Exception as e:
            conn.rollback()
            cur.close(); conn.close()
            app.logger.error(f"DB error on submit: {e}")
            flash("An error occurred while submitting your details.")
            return redirect(url_for('submit'))

    return render_template('submit.html')

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file part", "public_url":"error"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file", "public_url":"error"}), 400
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

@app.route('/update/<int:user_id>', methods=['GET', 'POST'])
def update(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        # Retrieve updated details from the form
        name = request.form['name']
        role = request.form['role']
        contact = request.form['contact']
        whatsapp = request.form['whatsapp']
        about = request.form['about']
        work_email = request.form.get('work_email', 'team@awhbharat.org') or "team@awhbharat.org"
        personal_email = request.form['personal_email']
        linkedin = request.form['linkedin']
        instagram = request.form['instagram']
        profile_image_url = request.form["profile_image"]
        background_image_url = request.form['background_image']

        # Update the user details in the database
        cur.execute("""
            UPDATE users
            SET name=%s, role=%s, contact=%s, whatsapp=%s, about=%s,
                work_email=%s, personal_email=%s, linkedin=%s, instagram=%s,
                image_url=%s, background_image=%s
            WHERE id=%s
        """, (
            name, role, contact, whatsapp, about,
            work_email, personal_email, linkedin, instagram,
            profile_image_url, background_image_url, user_id
        ))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('profile', user_id=user_id))
    else:
        # GET: Retrieve the existing user details to pre-populate the form
        cur.execute("""
            SELECT id, name, role, contact, whatsapp, about,
                   work_email, personal_email, linkedin, instagram,
                   image_url, background_image
            FROM users WHERE id=%s
        """, (user_id,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if not user:
            return "User not found", 404

        return render_template('update.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)
