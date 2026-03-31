from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration MySQL
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', '')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'portfolio_db')

mysql = MySQL(app)

# Initialiser la base de données
def init_db():
    cursor = mysql.connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            phone VARCHAR(20) NOT NULL,
            subject VARCHAR(200) NOT NULL,
            message TEXT NOT NULL,
            date_sent TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT FALSE
        )
    ''')
    mysql.connection.commit()
    cursor.close()
    print("Base de données initialisée avec succès!")

with app.app_context():
    init_db()

# Configuration emails
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'your_email@gmail.com')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', 'your_password')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL', 'your_email@gmail.com')

@app.route('/api/contact', methods=['POST'])
def send_contact():
    """Endpoint pour recevoir les messages de contact"""
    try:
        data = request.get_json()
        
        # Validation
        if not all(k in data for k in ['name', 'email', 'phone', 'subject', 'message']):
            return jsonify({'error': 'Données manquantes'}), 400
        
        # Insérer en base de données
        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO messages (name, email, phone, subject, message)
            VALUES (%s, %s, %s, %s, %s)
        ''', (data['name'], data['email'], data['phone'], data['subject'], data['message']))
        mysql.connection.commit()
        
        message_id = cursor.lastrowid
        cursor.close()
        
        # Envoyer l'email
        send_email(data)
        
        return jsonify({
            'success': True,
            'message': 'Votre message a été envoyé avec succès!',
            'id': message_id
        }), 200
    
    except Exception as e:
        print(f"Erreur: {str(e)}")
        return jsonify({'error': str(e)}), 500

def send_email(data):
    """Envoyer l'email au propriétaire"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = f"Nouveau message: {data['subject']}"
        
        body = f"""
Nouveau message de contact reçu:

Nom: {data['name']}
Email: {data['email']}
Téléphone: {data['phone']}
Sujet: {data['subject']}

Message:
{data['message']}

---
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        print("Email envoyé!")
        
    except Exception as e:
        print(f"Erreur email: {str(e)}")

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Récupérer tous les messages"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM messages ORDER BY date_sent DESC')
        columns = [desc[0] for desc in cursor.description]
        messages = []
        
        for row in cursor.fetchall():
            msg_dict = dict(zip(columns, row))
            msg_dict['date_sent'] = msg_dict['date_sent'].strftime('%Y-%m-%d %H:%M:%S')
            messages.append(msg_dict)
        
        cursor.close()
        return jsonify(messages), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages/<int:msg_id>', methods=['PUT'])
def mark_as_read(msg_id):
    """Marquer un message comme lu"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE messages SET is_read = TRUE WHERE id = %s', (msg_id,))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'success': True, 'message': 'Message marqué comme lu'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages/<int:msg_id>', methods=['DELETE'])
def delete_message(msg_id):
    """Supprimer un message"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM messages WHERE id = %s', (msg_id,))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'success': True, 'message': 'Message supprimé'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return jsonify({'message': 'Portfolio API running!'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
