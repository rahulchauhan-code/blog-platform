// Language selector functionality
function changeLanguage(lang) {
    const url = new URL(window.location.href);
    url.searchParams.set('lang', lang);
    window.location.href = url.toString();
}

// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const password = form.querySelector('input[name="password"]');
    const confirmPassword = form.querySelector('input[name="confirm_password"]');
    
    if (password && confirmPassword) {
        if (password.value !== confirmPassword.value) {
            alert('Passwords do not match!');
            return false;
        }
        
        if (password.value.length < 6) {
            alert('Password must be at least 6 characters long!');
            return false;
        }
    }
    
    return true;
}

// Confirm delete actions
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this item?');
}

// Copy post link
function copyPostLink() {
    const url = window.location.href;
    navigator.clipboard.writeText(url).then(() => {
        alert('Link copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy: ', err);
    });
}

// Smooth scroll to top
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Show scroll to top button when scrolling down
window.addEventListener('scroll', function() {
    const scrollBtn = document.getElementById('scrollTopBtn');
    if (scrollBtn) {
        if (window.pageYOffset > 300) {
            scrollBtn.style.display = 'block';
        } else {
            scrollBtn.style.display = 'none';
        }
    }
});

// Character counter for textareas
function addCharacterCounter(textareaId, maxLength) {
    const textarea = document.getElementById(textareaId);
    if (!textarea) return;
    
    const counter = document.createElement('div');
    counter.className = 'character-counter';
    counter.style.textAlign = 'right';
    counter.style.fontSize = '0.9rem';
    counter.style.color = '#7f8c8d';
    
    textarea.parentNode.appendChild(counter);
    
    function updateCounter() {
        const length = textarea.value.length;
        counter.textContent = `${length}${maxLength ? ' / ' + maxLength : ''} characters`;
        
        if (maxLength && length > maxLength) {
            counter.style.color = '#e74c3c';
        } else {
            counter.style.color = '#7f8c8d';
        }
    }
    
    textarea.addEventListener('input', updateCounter);
    updateCounter();
}

// Initialize character counters on post forms
document.addEventListener('DOMContentLoaded', function() {
    addCharacterCounter('content', 5000);
    addCharacterCounter('bio', 500);
});

// Mobile menu toggle
function toggleMobileMenu() {
    const navMenu = document.querySelector('.nav-menu');
    if (navMenu) {
        navMenu.classList.toggle('active');
    }
}

// New responsive nav toggle (controls aria and .nav-open)
function toggleNav(button) {
    const navbar = document.querySelector('.navbar') || document.getElementById('site-nav');
    if (!navbar) return;
    const expanded = button && button.getAttribute && button.getAttribute('aria-expanded') === 'true';
    if (button && button.setAttribute) button.setAttribute('aria-expanded', String(!expanded));
    if (navbar.classList) navbar.classList.toggle('nav-open');
}

// Close responsive nav (used when clicking a link)
function closeNav() {
    const navbar = document.querySelector('.navbar') || document.getElementById('site-nav');
    const toggle = document.querySelector('.nav-toggle') || document.getElementById('nav-toggle');
    if (!navbar) return;
    if (navbar.classList) navbar.classList.remove('nav-open');
    if (toggle && toggle.setAttribute) toggle.setAttribute('aria-expanded', 'false');
}

// Close mobile nav when a nav link is clicked
document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('.nav-menu a');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            const width = window.innerWidth || document.documentElement.clientWidth;
            if (width <= 768) closeNav();
        });
    });
});

// Image preview for profile pictures (if implemented)
function previewImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('imagePreview');
            if (preview) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            }
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Search functionality (for future implementation)
function searchPosts(query) {
    // This can be implemented to filter posts client-side
    // or trigger a server-side search
    console.log('Searching for:', query);
}

// Export functions for use in HTML
window.changeLanguage = changeLanguage;
window.validateForm = validateForm;
window.confirmDelete = confirmDelete;
window.copyPostLink = copyPostLink;
window.scrollToTop = scrollToTop;
window.toggleMobileMenu = toggleMobileMenu;
window.previewImage = previewImage;
window.searchPosts = searchPosts;
