// Navbar scroll effect
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// Scroll animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, observerOptions);

document.querySelectorAll('section').forEach(section => {
    observer.observe(section);
});

// Hero title animation
document.addEventListener('DOMContentLoaded', () => {
    const heroTitle = document.getElementById('hero-title');
    const text = heroTitle.textContent;
    heroTitle.textContent = '';
    
    let i = 0;
    const typeWriter = () => {
        if (i < text.length) {
            heroTitle.textContent += text.charAt(i);
            i++;
            setTimeout(typeWriter, 100);
        }
    };
    typeWriter();
});

// Zodiac wheel interaction
document.querySelectorAll('.zodiac-sign').forEach(sign => {
    sign.addEventListener('click', () => {
        const signName = sign.dataset.sign;
        const infoDiv = document.getElementById('zodiac-info');
        
        // Sample zodiac info - you can expand this
        const zodiacData = {
            Aries: { prediction: "Today brings energy and new beginnings.", strengths: "Courageous, determined", weak: "Impatient", color: "Red", number: "1" },
            Taurus: { prediction: "Stability and comfort are your focus today.", strengths: "Reliable, patient", weak: "Stubborn", color: "Green", number: "2" },
            // Add more zodiac data
        };
        
        const data = zodiacData[signName] || { prediction: "Select a sign for insights", strengths: "", weak: "", color: "", number: "" };
        
        infoDiv.innerHTML = `
            <h3 id="sign-title">${signName}</h3>
            <p><strong>Daily Prediction:</strong> ${data.prediction}</p>
            <p><strong>Strengths:</strong> ${data.strengths}</p>
            <p><strong>Weak Graha:</strong> ${data.weak}</p>
            <p><strong>Lucky Color:</strong> ${data.color} | <strong>Number:</strong> ${data.number}</p>
        `;
    });
});

// Kundli form steps
let currentStep = 1;
const totalSteps = 3;

document.querySelectorAll('.next-step').forEach(btn => {
    btn.addEventListener('click', () => {
        if (currentStep < totalSteps) {
            document.querySelector(`.step[data-step="${currentStep}"]`).classList.remove('active');
            currentStep++;
            document.querySelector(`.step[data-step="${currentStep}"]`).classList.add('active');
        }
    });
});

document.querySelectorAll('.prev-step').forEach(btn => {
    btn.addEventListener('click', () => {
        if (currentStep > 1) {
            document.querySelector(`.step[data-step="${currentStep}"]`).classList.remove('active');
            currentStep--;
            document.querySelector(`.step[data-step="${currentStep}"]`).classList.add('active');
        }
    });
});

// Generate Kundli button
document.querySelector('.generate-kundli')?.addEventListener('click', () => {
    // Add loading animation
    const btn = document.querySelector('.generate-kundli');
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Generating...';
    btn.disabled = true;
    
    setTimeout(() => {
        // Simulate generation complete
        btn.innerHTML = 'View Kundli';
        btn.disabled = false;
        // You can redirect to kundli result page here
    }, 3000);
});

// Parallax effect for galaxy
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const galaxy = document.querySelector('.galaxy');
    if (galaxy) {
        galaxy.style.transform = `translate(-50%, -50%) rotate(${scrolled * 0.1}deg)`;
    }
});

// Smooth scrolling for navigation
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

// Micro interactions
document.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('mouseenter', () => {
        btn.style.transform = 'translateY(-2px)';
    });
    
    btn.addEventListener('mouseleave', () => {
        btn.style.transform = 'translateY(0)';
    });
});

// Input focus effects
document.querySelectorAll('input').forEach(input => {
    input.addEventListener('focus', () => {
        input.style.boxShadow = '0 0 10px rgba(255, 215, 0, 0.5)';
    });
    
    input.addEventListener('blur', () => {
        input.style.boxShadow = 'none';
    });
});