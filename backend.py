from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import logging

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Check DATABASE_URL
print("=" * 50)
print("CONFIGURATION STARTUP")
print("=" * 50)
db_url = os.getenv('DATABASE_URL', '')
if db_url:
    masked_url = db_url[:30] + "***" + db_url[-10:]
    print(f"✅ DATABASE_URL configurée: {masked_url}")
else:
    print("❌ DATABASE_URL NON TROUVÉE!")
print("=" * 50)

# Configuration Flask
app = Flask(__name__)

# Configuration CORS pour accepter les requêtes de Vercel
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Configuration PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL', '')

# Fix Neon SSL connection
if DATABASE_URL and DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg2://')
    if '?sslmode' not in DATABASE_URL:
        DATABASE_URL += '?sslmode=require'

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# Initialiser SQLAlchemy
db = SQLAlchemy(app)

# ===== MODELE DE DONNEES =====
class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        """Convertir le modèle en dictionnaire JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'subject': self.subject,
            'message': self.message,
            'date_sent': self.date_sent.strftime('%Y-%m-%d %H:%M:%S'),
            'is_read': self.is_read
        }

# Initialiser la base de données
with app.app_context():
    db.create_all()
    print("✅ Base de données PostgreSQL initialisée avec succès!")

# ===== CONFIGURATION EMAIL - SENDGRID =====
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'your_email@gmail.com')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL', 'your_email@gmail.com')

if not SENDGRID_API_KEY:
    print("⚠️  SENDGRID_API_KEY non configurée!")
else:
    print("✅ SendGrid configuré")

# ===== FONCTION POUR ENVOYER EMAIL =====
def send_email(message_data):
    """Envoyer un email via SendGrid"""
    try:
        if not SENDGRID_API_KEY:
            print("❌ SendGrid API key manquante!")
            return False

        # Créer le message
        message = Mail(
            from_email=SENDER_EMAIL,
            to_emails=RECIPIENT_EMAIL,
            subject=f"📧 Nouveau message: {message_data['subject']}",
            plain_text_content=f"""
Nouveau message de contact reçu:

👤 Nom: {message_data['name']}
📧 Email: {message_data['email']}
☎️ Téléphone: {message_data['phone']}
📌 Sujet: {message_data['subject']}

💬 Message:
{message_data['message']}

---
⏰ Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
        )
        
        # Envoyer via SendGrid
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        print(f"✅ Email envoyé via SendGrid! (Status: {response.status_code})")
        return True
        
    except Exception as e:
        print(f"❌ Erreur SendGrid: {str(e)}")
        return False

# ===== ROUTES API =====

@app.route('/', methods=['GET'])
def home():
    """Route de base"""
    return jsonify({
        'message': '✅ Portfolio API is running!',
        'version': '2.0',
        'database': 'PostgreSQL'
    }), 200

@app.route('/api/contact', methods=['POST'])
def send_contact():
    """Créer un nouveau message"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['name', 'email', 'phone', 'subject', 'message']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Données manquantes'}), 400
        
        # Créer le message
        new_message = Message(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            subject=data['subject'],
            message=data['message']
        )
        
        # Sauvegarder en base de données
        db.session.add(new_message)
        db.session.commit()
        
        # Envoyer l'email
        send_email(data)
        
        return jsonify({
            'success': True,
            'message': 'Votre message a été envoyé avec succès!',
            'id': new_message.id
        }), 200
    
    except Exception as e:
        db.session.rollback()
        error_msg = f"❌ Erreur: {str(e)}"
        print(error_msg)
        print(f"Type d'erreur: {type(e).__name__}")
        return jsonify({'error': 'Erreur serveur. Veuillez réessayer.', 'details': str(e)}), 500

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Récupérer tous les messages"""
    try:
        messages = Message.query.order_by(Message.date_sent.desc()).all()
        return jsonify([msg.to_dict() for msg in messages]), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages/<int:msg_id>', methods=['GET'])
def get_message(msg_id):
    """Récupérer un message spécifique"""
    try:
        message = Message.query.get(msg_id)
        if not message:
            return jsonify({'error': 'Message non trouvé'}), 404
        return jsonify(message.to_dict()), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages/<int:msg_id>', methods=['PUT'])
def mark_as_read(msg_id):
    """Marquer un message comme lu"""
    try:
        message = Message.query.get(msg_id)
        if not message:
            return jsonify({'error': 'Message non trouvé'}), 404
        
        message.is_read = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Message marqué comme lu'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages/<int:msg_id>', methods=['DELETE'])
def delete_message(msg_id):
    """Supprimer un message"""
    try:
        message = Message.query.get(msg_id)
        if not message:
            return jsonify({'error': 'Message non trouvé'}), 404
        
        db.session.delete(message)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Message supprimé'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages/<int:msg_id>', methods=['PATCH'])
def update_message(msg_id):
    """Mettre à jour un message"""
    try:
        data = request.get_json()
        message = Message.query.get(msg_id)
        
        if not message:
            return jsonify({'error': 'Message non trouvé'}), 404
        
        # Mettre à jour les champs fournis
        if 'is_read' in data:
            message.is_read = data['is_read']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Message mis à jour',
            'data': message.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Obtenir les statistiques"""
    try:
        total = Message.query.count()
        unread = Message.query.filter_by(is_read=False).count()
        read = Message.query.filter_by(is_read=True).count()
        
        return jsonify({
            'total': total,
            'unread': unread,
            'read': read
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== GESTION DES ERREURS =====
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Route non trouvée'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erreur serveur interne'}), 500

# ===== LANCER LE SERVEUR =====
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
