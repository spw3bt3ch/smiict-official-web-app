// SMIICT Institute Course Platform - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initMobileNavigation();
    initPaymentMethods();
    initFormValidation();
    initModals();
    initTooltips();
    initSmoothScrolling();
    initLoadingStates();
});

// Mobile Navigation
function initMobileNavigation() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (!mobileMenuButton || !mobileMenu) {
        return;
    }
    
    // Toggle mobile menu using event delegation
    document.addEventListener('click', function(e) {
        if (e.target.closest('#mobile-menu-button')) {
            e.preventDefault();
            e.stopPropagation();
            
            console.log('Mobile menu button clicked');
            console.log('Button innerHTML:', mobileMenuButton.innerHTML);
            console.log('Button classes:', mobileMenuButton.className);
            
            // Add ripple effect
            mobileMenuButton.classList.add('ripple');
            setTimeout(() => {
                mobileMenuButton.classList.remove('ripple');
            }, 600);
            
            const isHidden = mobileMenu.classList.contains('hidden');
            console.log('Menu is hidden:', isHidden);
            
            if (isHidden) {
                // Show menu
                console.log('Showing mobile menu');
                mobileMenu.classList.remove('hidden');
                mobileMenuButton.innerHTML = '<i class="fas fa-times text-xl"></i>';
                mobileMenuButton.classList.add('menu-open');
                mobileMenuButton.setAttribute('aria-expanded', 'true');
                
                // Add bounce animation to button
                mobileMenuButton.style.animation = 'bounce 0.6s ease-out';
                setTimeout(() => {
                    mobileMenuButton.style.animation = '';
                }, 600);
                
            } else {
                // Hide menu
                console.log('Hiding mobile menu');
                closeMobileMenu();
            }
        }
    });
    
    // Function to close mobile menu with animations
    function closeMobileMenu() {
        console.log('Closing mobile menu');
        mobileMenu.classList.add('hidden');
        mobileMenuButton.innerHTML = '<i class="fas fa-bars text-xl"></i>';
        mobileMenuButton.classList.remove('menu-open');
        mobileMenuButton.setAttribute('aria-expanded', 'false');
        console.log('Mobile menu closed');
    }
    
    // Close mobile menu when clicking on a link
    const mobileMenuLinks = mobileMenu.querySelectorAll('a');
    mobileMenuLinks.forEach(link => {
        link.addEventListener('click', function() {
            closeMobileMenu();
        });
    });
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
        const isClickInsideNav = event.target.closest('nav');
        const isClickOnButton = event.target.closest('#mobile-menu-button');
        
        if (!isClickInsideNav && !isClickOnButton && !mobileMenu.classList.contains('hidden')) {
            closeMobileMenu();
        }
    });
    
    // Close mobile menu on window resize to desktop size
    window.addEventListener('resize', function() {
        if (window.innerWidth >= 768) { // md breakpoint
            closeMobileMenu();
        }
    });
    
    // Handle escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && !mobileMenu.classList.contains('hidden')) {
            closeMobileMenu();
        }
    });
}

// Payment Method Selection
function initPaymentMethods() {
    const paymentMethods = document.querySelectorAll('.payment-method');
    const paymentInstructions = document.querySelectorAll('.payment-instructions');
    const cardForm = document.getElementById('card-form');
    
    if (paymentMethods.length === 0) return;
    
    paymentMethods.forEach(method => {
        method.addEventListener('click', function() {
            // Remove active class from all methods
            paymentMethods.forEach(m => m.classList.remove('selected'));
            // Add active class to clicked method
            this.classList.add('selected');
            
            // Hide all instructions
            paymentInstructions.forEach(instruction => instruction.classList.add('hidden'));
            
            // Show selected instruction
            const methodType = this.dataset.method;
            const selectedInstruction = document.getElementById(methodType + '-instructions');
            if (selectedInstruction) {
                selectedInstruction.classList.remove('hidden');
            }
            
            // Show/hide card form
            if (cardForm) {
                if (methodType === 'card') {
                    cardForm.style.display = 'block';
                } else {
                    cardForm.style.display = 'none';
                }
            }
        });
    });
}

// Form Validation
function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    const type = field.type;
    let isValid = true;
    let errorMessage = '';
    
    // Remove existing error styling
    field.classList.remove('is-invalid');
    const existingError = field.parentNode.querySelector('.form-error');
    if (existingError) {
        existingError.remove();
    }
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'This field is required.';
    }
    
    // Email validation
    if (type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address.';
        }
    }
    
    // Password validation
    if (type === 'password' && value) {
        if (value.length < 6) {
            isValid = false;
            errorMessage = 'Password must be at least 6 characters long.';
        }
    }
    
    // Phone validation
    if (type === 'tel' && value) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        if (!phoneRegex.test(value.replace(/\s/g, ''))) {
            isValid = false;
            errorMessage = 'Please enter a valid phone number.';
        }
    }
    
    // Apply validation result
    if (!isValid) {
        field.classList.add('is-invalid');
        showFieldError(field, errorMessage);
    } else {
        field.classList.add('is-valid');
    }
    
    return isValid;
}

function showFieldError(field, message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'form-error';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

// Modal Management
function initModals() {
    const modalTriggers = document.querySelectorAll('[data-modal]');
    const modals = document.querySelectorAll('.modal');
    const modalCloses = document.querySelectorAll('.modal-close, .modal-overlay');
    
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const modalId = this.dataset.modal;
            const modal = document.getElementById(modalId);
            if (modal) {
                showModal(modal);
            }
        });
    });
    
    modalCloses.forEach(close => {
        close.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                hideModal(modal);
            }
        });
    });
    
    // Close modal on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                hideModal(openModal);
            }
        }
    });
}

function showModal(modal) {
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
}

function hideModal(modal) {
    modal.classList.remove('show');
    document.body.style.overflow = '';
}

// Tooltip Management
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', function() {
            showTooltip(this);
        });
        
        element.addEventListener('mouseleave', function() {
            hideTooltip(this);
        });
    });
}

function showTooltip(element) {
    const text = element.dataset.tooltip;
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip-text';
    tooltip.textContent = text;
    element.appendChild(tooltip);
}

function hideTooltip(element) {
    const tooltip = element.querySelector('.tooltip-text');
    if (tooltip) {
        tooltip.remove();
    }
}

// Smooth Scrolling
function initSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Loading States
function initLoadingStates() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                showLoadingState(submitBtn);
            }
        });
    });
}

function showLoadingState(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="spinner"></span> Processing...';
    button.disabled = true;
    button.classList.add('loading');
    
    // Reset after 5 seconds (fallback)
    setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
        button.classList.remove('loading');
    }, 5000);
}

function hideLoadingState(button) {
    button.innerHTML = button.dataset.originalText || 'Submit';
    button.disabled = false;
    button.classList.remove('loading');
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// AJAX Helper
function makeRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const config = { ...defaultOptions, ...options };
    
    return fetch(url, config)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('Request failed:', error);
            throw error;
        });
}

// Notification System
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} fade-in`;
    notification.textContent = message;
    
    // Add to page
    const container = document.querySelector('.notifications') || createNotificationContainer();
    container.appendChild(notification);
    
    // Auto remove
    setTimeout(() => {
        notification.remove();
    }, duration);
}

function createNotificationContainer() {
    const container = document.createElement('div');
    container.className = 'notifications';
    container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        max-width: 400px;
    `;
    document.body.appendChild(container);
    return container;
}

// Course Card Interactions
function initCourseCards() {
    const courseCards = document.querySelectorAll('.course-card');
    
    courseCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

// Mobile menu functionality
function initMobileMenu() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        console.log('Mobile menu elements found:', { mobileMenuButton, mobileMenu });
        
        mobileMenuButton.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            console.log('Mobile menu button clicked');
            const isHidden = mobileMenu.classList.contains('hidden');
            
            if (isHidden) {
                console.log('Showing mobile menu');
                mobileMenu.classList.remove('hidden');
                mobileMenuButton.innerHTML = '<i class="fas fa-times"></i>';
            } else {
                console.log('Hiding mobile menu');
                mobileMenu.classList.add('hidden');
                mobileMenuButton.innerHTML = '<i class="fas fa-bars"></i>';
            }
        });
        
        // Close mobile menu when clicking on a link
        const mobileMenuLinks = mobileMenu.querySelectorAll('a');
        mobileMenuLinks.forEach(link => {
            link.addEventListener('click', function() {
                console.log('Mobile menu link clicked, closing menu');
                mobileMenu.classList.add('hidden');
                mobileMenuButton.innerHTML = '<i class="fas fa-bars"></i>';
            });
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!mobileMenuButton.contains(event.target) && !mobileMenu.contains(event.target)) {
                if (!mobileMenu.classList.contains('hidden')) {
                    console.log('Clicking outside, closing mobile menu');
                    mobileMenu.classList.add('hidden');
                    mobileMenuButton.innerHTML = '<i class="fas fa-bars"></i>';
                }
            }
        });
    } else {
        console.log('Mobile menu elements not found:', { mobileMenuButton, mobileMenu });
    }
}

// Initialize course cards when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initCourseCards();
    initMobileMenu();
});

// Export functions for global use
window.SMIICT = {
    showModal,
    hideModal,
    showNotification,
    makeRequest,
    showLoadingState,
    hideLoadingState
};
