import csv
import os
import sqlite3
import smtplib
from datetime import datetime
from email.message import EmailMessage
from flask import Flask, request, send_file, jsonify

app = Flask(__name__, static_folder='.', static_url_path='')
DATABASE_PATH = os.path.join(app.root_path, 'sales.db')
LEADS_CSV = os.path.join(app.root_path, 'leads.csv')

EMAIL_SETTINGS = {
    'host': os.environ.get('SALES_EMAIL_HOST'),
    'port': int(os.environ.get('SALES_EMAIL_PORT', '587')),
    'user': os.environ.get('SALES_EMAIL_USER'),
    'password': os.environ.get('SALES_EMAIL_PASSWORD'),
    'from': os.environ.get('SALES_EMAIL_FROM'),
    'to': os.environ.get('SALES_EMAIL_TO'),
}


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db_connection() as conn:
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                email TEXT NOT NULL,
                source TEXT,
                created_at TEXT NOT NULL
            );
            '''
        )
        conn.commit()


def append_lead_csv(nombre, email, source, created_at):
    exists = os.path.exists(LEADS_CSV)
    with open(LEADS_CSV, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['nombre', 'email', 'source', 'created_at']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerow({
            'nombre': nombre,
            'email': email,
            'source': source,
            'created_at': created_at,
        })


def save_lead(nombre, email, source=None):
    created_at = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        conn.execute(
            'INSERT INTO leads (nombre, email, source, created_at) VALUES (?, ?, ?, ?)',
            (nombre, email, source, created_at)
        )
    append_lead_csv(nombre, email, source, created_at)
    return {
        'nombre': nombre,
        'email': email,
        'source': source,
        'created_at': created_at,
    }


def send_sales_notification(lead):
    if not EMAIL_SETTINGS['host'] or not EMAIL_SETTINGS['user'] or not EMAIL_SETTINGS['password'] or not EMAIL_SETTINGS['to']:
        return False

    message = EmailMessage()
    message['Subject'] = f"Nuevo lead capturado: {lead['nombre']}"
    message['From'] = EMAIL_SETTINGS['from'] or EMAIL_SETTINGS['user']
    message['To'] = EMAIL_SETTINGS['to']
    message.set_content(
        f"Nuevo lead:\n\nNombre: {lead['nombre']}\nEmail: {lead['email']}\nFuente: {lead['source']}\nFecha: {lead['created_at']}"
    )

    with smtplib.SMTP(EMAIL_SETTINGS['host'], EMAIL_SETTINGS['port']) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_SETTINGS['user'], EMAIL_SETTINGS['password'])
        smtp.send_message(message)

    return True


@app.before_first_request
def startup():
    init_db()


@app.route('/')
def home():
    return send_file('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    nombre = request.form.get('nombre')
    email = request.form.get('email')
    
    # Aquí puedes usar Python para:
    # 1. Enviar un correo automático al cliente con SendGrid
    # 2. Guardar en un Excel con Pandas
    # 3. Notificarte por Telegram
    
    nuevo_lead = {"nombre": nombre, "email": email}
    leads.append(nuevo_lead)
    
    print(f"🔥 ¡Nuevo Lead Capturado!: {nuevo_lead}")
    
    return "<h1>¡Gracias! Tu sistema se está configurando. Te contactaremos en breve.</h1>"

if __name__ == '__main__':
    app.run(debug=True)