// Mobile Navbar Toggle
document.addEventListener('DOMContentLoaded', function() {
    const toggler = document.querySelector('.navbar-toggler');
    const collapse = document.querySelector('#navbarNav');
    
    toggler.addEventListener('click', function() {
        toggler.classList.toggle('collapsed');
    });
    
    // Smooth Scrolling
    document.querySelectorAll('a[href^=\"#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({ behavior: 'smooth' });
        });
    });
});

// Testimonial Slider
function initSlider() {
    const items = document.querySelectorAll('.testimonial-item');
    let current = 0;
    
    function showSlide(index) {
        items.forEach((item, i) => {
            item.classList.toggle('active', i === index);
        });
    }
    
    setInterval(() => {
        current = (current + 1) % items.length;
        showSlide(current);
    }, 5000);
    
    showSlide(current);
}

// Form Validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    form.addEventListener('submit', function(e) {
        // Basic validation
        const email = form.querySelector('input[type=\"email\"]');
        const password = form.querySelector('input[type=\"password\"]');
        
        if (!email.value.includes('@')) {
            alert('Please enter valid email');
            e.preventDefault();
            return false;
        }
        
        if (password.value.length < 6) {
            alert('Password must be at least 6 characters');
            e.preventDefault();
            return false;
        }
        
        return true;
    });
}

// Razorpay Payment Init (to be called from payment.html)
function initPayment(amount, courseId, studentId) {
    const options = {
        key: 'rzp_test_your_key',  // Replace with real key
        amount: amount * 100,  // Paisa
        currency: 'INR',
        name: 'Gravity Teaching',
        description: 'Course Enrollment',
        handler: function(response) {
            // Verify & save payment
            fetch('/verify-payment', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    razorpay_payment_id: response.razorpay_payment_id,
                    course_id: courseId,
                    student_id: studentId
                })
            }).then(res => res.json()).then(data => {
                if (data.success) {
                    showPopup('Payment successful! Access granted.');
                    setTimeout(() => window.location.href = '/student-dashboard', 2000);
                }
            });
        }
    };
    
    const rzp = new Razorpay(options);
    rzp.open();
}

// Success Popup
function showPopup(message) {
    const popup = document.createElement('div');
    popup.className = 'alert alert-success position-fixed top-50 start-50 translate-middle';
    popup.style.zIndex = '9999';
    popup.innerHTML = message;
    document.body.appendChild(popup);
    setTimeout(() => popup.remove(), 3000);
}

// Course Filter
function filterCourses(category) {
    const cards = document.querySelectorAll('.course-card');
    cards.forEach(card => {
        if (category === 'all' || card.dataset.category === category) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Init
if (document.querySelector('.testimonial-slider')) initSlider();
if (document.getElementById('contact-form')) validateForm('contact-form');
