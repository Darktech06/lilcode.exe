// Charger les messages au chargement de la page
document.addEventListener('DOMContentLoaded', loadMessages);

// Auto-refresh toutes les 30 secondes
setInterval(loadMessages, 30000);

async function loadMessages() {
    const container = document.getElementById('messagesContainer');
    
    try {
        const response = await fetch('http://localhost:5000/api/messages');
        const messages = await response.json();

        if (!response.ok) {
            throw new Error('Erreur lors du chargement');
        }

        // Calculer les stats
        const total = messages.length;
        const unread = messages.filter(m => !m.is_read).length;
        const read = messages.filter(m => m.is_read).length;

        document.getElementById('totalCount').textContent = total;
        document.getElementById('unreadCount').textContent = unread;
        document.getElementById('readCount').textContent = read;

        // Afficher les messages
        if (messages.length === 0) {
            container.innerHTML = '<div class="no-messages">Aucun message reçu pour le moment</div>';
        } else {
            container.innerHTML = messages.map(msg => `
                <div class="message-card ${msg.is_read ? '' : 'unread'}">
                    <div class="message-header">
                        <div class="message-info">
                            <h3>${escapeHtml(msg.name)}</h3>
                            <div style="margin: 5px 0;">
                                <a href="mailto:${escapeHtml(msg.email)}" class="message-email">
                                    <ion-icon name="mail-outline"></ion-icon>
                                    ${escapeHtml(msg.email)}
                                </a>
                                <br>
                                <a href="tel:${escapeHtml(msg.phone)}" class="message-phone">
                                    <ion-icon name="call-outline"></ion-icon>
                                    ${escapeHtml(msg.phone)}
                                </a>
                                <span class="message-date">
                                    ${msg.date_sent}
                                </span>
                            </div>
                        </div>
                        ${!msg.is_read ? '<span class="message-badge">Non Lu</span>' : ''}
                    </div>

                    <div class="message-subject">
                        Sujet: ${escapeHtml(msg.subject)}
                    </div>

                    <div class="message-body">
                        ${escapeHtml(msg.message).replace(/\n/g, '<br>')}
                    </div>

                    <div class="message-actions">
                        ${!msg.is_read ? `
                            <button class="action-btn mark-read-btn" onclick="markAsRead(${msg.id})">
                                <ion-icon name="checkmark-outline"></ion-icon>
                                Marquer comme lu
                            </button>
                        ` : ''}
                        <button class="action-btn delete-btn" onclick="deleteMessage(${msg.id})">
                            <ion-icon name="trash-outline"></ion-icon>
                            Supprimer
                        </button>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Erreur:', error);
        container.innerHTML = `<div class="no-messages">Erreur: ${error.message}</div>`;
    }
}

async function markAsRead(messageId) {
    try {
        const response = await fetch(`http://localhost:5000/api/messages/${messageId}`, {
            method: 'PUT'
        });

        if (response.ok) {
            loadMessages();
        }
    } catch (error) {
        console.error('Erreur:', error);
    }
}

async function deleteMessage(messageId) {
    if (confirm('Êtes-vous sûr de vouloir supprimer ce message?')) {
        try {
            const response = await fetch(`http://localhost:5000/api/messages/${messageId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                loadMessages();
            }
        } catch (error) {
            console.error('Erreur:', error);
        }
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
