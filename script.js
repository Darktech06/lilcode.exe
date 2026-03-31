//animation 
var typed = new Typed("#typed", {
    strings: ["Informaticien", "Développeur Web", "Graphiste", "Etudiant en informatique"],
    typeSpeed: 50,
    backSpeed: 20,
    backDelay: 3000,
    showCursor: false,
    loop: true
});

//Initialize theme from localStorage
window.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.body.classList.add('light');
        updateThemeButtons();
    }
    
    // Add keyboard support for theme toggle
    const themeBtn = document.querySelector('.box.them');
    if (themeBtn) {
        themeBtn.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                theme();
            }
        });
    }
});

//couleur de theme
function theme() {
    const lightBtn = document.getElementById("lightBtn");
    const darkBtn = document.getElementById("darkBtn");
    
    document.body.classList.toggle('light');
    
    if (document.body.classList.contains('light')) {
        localStorage.setItem('theme', 'light');
        updateThemeButtons();
    } else {
        localStorage.setItem('theme', 'dark');
        updateThemeButtons();
    }
}

function updateThemeButtons() {
    const lightBtn = document.getElementById("lightBtn");
    const darkBtn = document.getElementById("darkBtn");
    
    if (document.body.classList.contains('light')) {
        darkBtn.style.display = "block";
        lightBtn.style.display = "none";
    } else {
        darkBtn.style.display = "none";
        lightBtn.style.display = "block";
    }
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ===== CONTACT MODAL FUNCTIONS =====

function openContactModal(event) {
    event.preventDefault();
    const modal = document.getElementById('contactModal');
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeContactModal() {
    const modal = document.getElementById('contactModal');
    modal.classList.add('hidden');
    document.body.style.overflow = 'auto';
}

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    const modal = document.getElementById('contactModal');
    if (event.target === modal) {
        closeContactModal();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeContactModal();
    }
});

// Handle form submission
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const name = document.getElementById('name').value.trim();
            const email = document.getElementById('email').value.trim();
            const phone = document.getElementById('phone').value.trim();
            const subject = document.getElementById('subject').value.trim();
            const message = document.getElementById('message').value.trim();

            // Validation des champs
            if (!name || !email || !phone || !subject || !message) {
                showMessage('❌ Tous les champs sont obligatoires!', 'error');
                return;
            }

            // Validation email
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                showMessage('❌ Veuillez entrer une adresse email valide!', 'error');
                return;
            }

            // Validation téléphone (au moins 8 caractères)
            const phoneRegex = /^[\d\s\-\+()]{8,}$/;
            if (!phoneRegex.test(phone)) {
                showMessage('❌ Veuillez entrer un numéro de téléphone valide!', 'error');
                return;
            }

            // Confirmation avant d'envoyer
            if (!confirm('Êtes-vous sûr de vouloir envoyer ce message?\n\nNom: ' + name + '\nEmail: ' + email + '\nTéléphone: ' + phone)) {
                return; // L'utilisateur a annulé
            }

            const formData = {
                name: name,
                email: email,
                phone: phone,
                subject: subject,
                message: message
            };

            try {
                const response = await fetch('http://localhost:5000/api/contact', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();

                if (response.ok) {
                    showMessage('✅ Message envoyé avec succès!\n\nVous allez recevoir une confirmation par email.', 'success');
                    contactForm.reset();
                    setTimeout(() => {
                        closeContactModal();
                    }, 3000);
                } else {
                    showMessage('❌ Erreur: ' + (data.error || 'Impossible d\'envoyer le message'), 'error');
                }
            } catch (error) {
                console.error('Erreur:', error);
                showMessage('❌ Erreur de connexion. Assure-toi que le serveur est actif (python backend.py)', 'error');
            }
        });
    }
});

function showMessage(message, type) {
    const messageDisplay = document.getElementById('messageDisplay');
    messageDisplay.innerHTML = `<div class="message ${type}">${message}</div>`;
    messageDisplay.style.display = 'block';

    if (type === 'success') {
        setTimeout(() => {
            messageDisplay.style.display = 'none';
        }, 3000);
    }
}