from flask import Flask, render_template, request, redirect, url_for, send_file, session, Response
import sqlite3
import pandas as pd
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'secret_admin_key'  # Required for session management
DATABASE = "team_data.db"

# Initialize SQLite database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS teams')  # Drop the existing table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_name TEXT NOT NULL,
                team_lead_name TEXT NOT NULL,
                team_lead_email TEXT NOT NULL,
                team_lead_phone TEXT NOT NULL,
                team_lead_reg_no TEXT NOT NULL,
                member1_name TEXT NOT NULL,
                member1_email TEXT NOT NULL,
                member1_reg_no TEXT NOT NULL,
                member2_name TEXT,
                member2_email TEXT,
                member2_reg_no TEXT,
                member3_name TEXT,
                member3_email TEXT,
                member3_reg_no TEXT
            )
        ''')
        conn.commit()



# Route: Homepage
@app.route('/')
def home():
    return render_template('home.html')

# Route: Registration Form
@app.route('/team_register', methods=['GET', 'POST'])
def team_register():
    if request.method == 'POST':
        # Collect form data including registration numbers for team lead and members
        data = (
            request.form['team_name'],
            request.form['team_lead_name'],
            request.form['team_lead_email'],
            request.form['team_lead_phone'],
            request.form['team_lead_reg_no'],  # New registration number for team lead
            request.form['member_1_name'],
            request.form['member_1_email'],
            request.form['member_1_reg_no'],  # Registration number for member 1
            request.form['member_2_name'],
            request.form['member_2_email'],
            request.form['member_2_reg_no'],  # Registration number for member 2
            request.form['member_3_name'],
            request.form['member_3_email'],
            request.form['member_3_reg_no']   # Registration number for member 3
        )
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO teams (
                    team_name, team_lead_name, team_lead_email, team_lead_phone, team_lead_reg_no,
                    member1_name, member1_email, member1_reg_no,
                    member2_name, member2_email, member2_reg_no,
                    member3_name, member3_email, member3_reg_no
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', data)
            conn.commit()

        return render_template('download_info.html', data=request.form)  # Provide download option
    return render_template('team_register.html')

# Route: Admin Login
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == "admin" and password == "acmvitap":  # Simple authentication
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        return "Invalid credentials. Try again."
    return render_template('admin_login.html')

# Route: Admin Dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' in session:
        return render_template('admin_dashboard.html')
    return redirect(url_for('admin_login'))

# Route: View Registered Teams
@app.route('/view_registered_teams')
def view_registered_teams():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teams")
        teams = cursor.fetchall()
    
    return render_template('registered_details.html', teams=teams)

# Route: Export to Excel
@app.route('/export_excel')
def export_excel():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    with sqlite3.connect(DATABASE) as conn:
        df = pd.read_sql_query("SELECT * FROM teams", conn)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Teams')
    output.seek(0)
    return send_file(output, download_name="team_details.xlsx", as_attachment=True)

# Route: Admin Logout
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

# Route: Download Info
@app.route('/download_info', methods=['POST'])
def download_info():
    # You can either generate a file dynamically or save the team data in a file.
    # Here, we generate a plain text file with the team registration details.

    team_info = request.form  # The form data from the registration

    # Create a downloadable file (e.g., plain text)
    download_content = f"""
    Team Name: {team_info['team_name']}
    Team Lead: {team_info['team_lead_name']}
    Team Lead Email: {team_info['team_lead_email']}
    Team Lead Phone: {team_info['team_lead_phone']}
    Team Lead Registration Number: {team_info['team_lead_reg_no']}
    Member 1: {team_info['member_1_name']} ({team_info['member_1_email']}) | Reg No: {team_info['member_1_reg_no']}
    Member 2: {team_info['member_2_name']} ({team_info['member_2_email']}) | Reg No: {team_info['member_2_reg_no']}
    Member 3: {team_info['member_3_name']} ({team_info['member_3_email']}) | Reg No: {team_info['member_3_reg_no']}
    """

    # Create the file in memory
    return Response(
        download_content,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment;filename=team_registration.txt"}
    )

# Route: Upcoming Events
@app.route('/upcoming_events')
def upcoming_events():
    return render_template('upcoming_events.html')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
