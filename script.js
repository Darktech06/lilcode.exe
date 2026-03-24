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