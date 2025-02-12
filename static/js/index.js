// Utility Functions
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => notification.classList.add('show'), 100);
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function formatNumber(num) {
    return new Intl.NumberFormat('en-IN').format(num);
}

// Navigation Handling
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function() {
        document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
        this.classList.add('active');
        showNotification(`Navigated to ${this.textContent.trim()}`);
        
        const content = document.querySelector('.content');
        content.classList.add('loading');
        setTimeout(() => content.classList.remove('loading'), 1000);
    });
});

// Stats Interaction
document.querySelectorAll('.stat-item').forEach(stat => {
    stat.addEventListener('click', function() {
        this.classList.toggle('active');
        const label = this.querySelector('.stat-label').textContent;
        const value = this.querySelector('.stat-value').textContent;
        showNotification(`Selected ${label}: ${value}`);
    });
});

// Simulate Real-time Updates
function updateRandomStat() {
    const stats = document.querySelectorAll('.stat-value');
    const randomStat = stats[Math.floor(Math.random() * stats.length)];
    const currentValue = parseInt(randomStat.textContent.replace(/,/g, ''));
    const change = Math.floor(Math.random() * 20) - 10;
    const newValue = currentValue + change;
    
    randomStat.textContent = formatNumber(newValue);
    
    const trend = randomStat.nextElementSibling;
    if (trend) {
        const percentage = ((change / currentValue) * 100).toFixed(1);
        trend.textContent = `${percentage > 0 ? '↑' : '↓'} ${Math.abs(percentage)}% vs last week`;
        trend.style.color = percentage > 0 ? '#16a34a' : '#dc2626';
    }
}
setInterval(updateRandomStat, 5000);

// Button Interactions
document.querySelectorAll('.button').forEach(button => {
    button.addEventListener('click', function(e) {
        e.preventDefault();
        const isSignup = this.textContent.includes('Started');
        showNotification(isSignup ? 'Starting sign up process...' : 'Loading demo account...', 'success');
    });
});

// Rating Interactions
document.querySelectorAll('.rating-item').forEach(rating => {
    rating.addEventListener('mouseenter', () => rating.style.transform = 'scale(1.05)');
    rating.addEventListener('mouseleave', () => rating.style.transform = 'scale(1)');
    rating.addEventListener('click', function() {
        const source = this.textContent.split(' ').pop();
        showNotification(`Viewing ${source} reviews...`);
    });
});

// Initialize with Loading Animation
window.addEventListener('load', () => {
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.opacity = '1';
        document.body.style.transition = 'opacity 0.3s ease';
        showNotification('Welcome to InvenTrack!', 'success');
    }, 100);
});

// Mobile Navigation Handling
if (window.innerWidth <= 768) {
    const navList = document.querySelector('.nav-list');
    let isScrolling = false;
    
    navList.addEventListener('scroll', () => {
        if (!isScrolling) navList.classList.add('scrolling');
        isScrolling = true;
        clearTimeout(window.scrollTimeout);
        
        window.scrollTimeout = setTimeout(() => {
            navList.classList.remove('scrolling');
            isScrolling = false;
        }, 150);
    });
}

// Keyboard Navigation
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.stat-item.active').forEach(stat => stat.classList.remove('active'));
    }
});

// Search Bar
document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.querySelector('.sidebar');
    const searchDiv = document.createElement('div');
    searchDiv.innerHTML = `
        <div style="padding: 16px;">
            <input type="search" placeholder="Search..." style="width: 100%; padding: 8px; border-radius: 4px; border: none;">
        </div>`;
    sidebar.insertBefore(searchDiv, sidebar.firstChild);
    startNumberAnimations();
});

// Number Animation Function
function animateValue(element, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        element.textContent = Math.floor(progress * (end - start) + start).toLocaleString();
        if (progress < 1) window.requestAnimationFrame(step);
    };
    window.requestAnimationFrame(step);
}

// Start Number Animations
function startNumberAnimations() {
    document.querySelectorAll('.stat-value').forEach(element => {
        const finalValue = parseInt(element.textContent.replace(/,/g, ''));
        element.textContent = '0';
        animateValue(element, 0, finalValue, 2000);
    });
}
