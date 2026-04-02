# Utilise l'image Python officielle
FROM python:3.11-slim

# Définit le répertoire de travail
WORKDIR /app

# Copie les requirements
COPY requirements.txt .

# Installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le backend
COPY backend.py .

# Expose le port 5000
EXPOSE 5000

# Commande de démarrage
CMD ["python", "backend.py"]
