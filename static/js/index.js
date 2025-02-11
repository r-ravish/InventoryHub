    // Utility Functions
    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Show notification
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Remove notification after 3 seconds
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
            // Remove active class from all items
            document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
            
            // Add active class to clicked item
            this.classList.add('active');
            
            // Show notification for navigation
            showNotification(`Navigated to ${this.textContent.trim()}`);
            
            // Simulate content loading
            const content = document.querySelector('.content');
            content.classList.add('loading');
            
            setTimeout(() => {
                content.classList.remove('loading');
            }, 1000);
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
        const change = Math.floor(Math.random() * 20) - 10; // Random change between -10 and +10
        const newValue = currentValue + change;
        
        randomStat.textContent = formatNumber(newValue);
        
        const trend = randomStat.nextElementSibling;
        if (trend) {
            const percentage = ((change / currentValue) * 100).toFixed(1);
            trend.textContent = `${percentage > 0 ? '↑' : '↓'} ${Math.abs(percentage)}% vs last week`;
            trend.style.color = percentage > 0 ? '#16a34a' : '#dc2626';
        }
    }

    // Update stats every 5 seconds
    setInterval(updateRandomStat, 5000);

    // Button Interactions
    document.querySelectorAll('.button').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const isSignup = this.textContent.includes('Started');
            
            if (isSignup) {
                showNotification('Starting sign up process...', 'success');
            } else {
                showNotification('Loading demo account...', 'success');
            }
        });
    });

    // Rating Interactions
    document.querySelectorAll('.rating-item').forEach(rating => {
        rating.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
        });
        
        rating.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
        
        rating.addEventListener('click', function() {
            const source = this.textContent.split(' ').pop();
            showNotification(`Viewing ${source} reviews...`);
        });
    });

    // Initialize with loading animation
    window.addEventListener('load', () => {
        document.body.style.opacity = '0';
        setTimeout(() => {
            document.body.style.opacity = '1';
            document.body.style.transition = 'opacity 0.3s ease';
            showNotification('Welcome to InvenTrack!', 'success');
        }, 100);
    });

    // Mobile Navigation
    if (window.innerWidth <= 768) {
        const navList = document.querySelector('.nav-list');
        let isScrolling = false;

        navList.addEventListener('scroll', () => {
            if (!isScrolling) {
                navList.classList.add('scrolling');
            }
            
            isScrolling = true;
            clearTimeout(window.scrollTimeout);
            
            window.scrollTimeout = setTimeout(() => {
                navList.classList.remove('scrolling');
                isScrolling = false;
            }, 150);
        });
    }

    // Add keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('.stat-item.active').forEach(stat => {
                stat.classList.remove('active');
            });
        }
    });
    function addSearchBar() {
    const sidebar = document.querySelector('.sidebar');
    const searchDiv = document.createElement('div');
    searchDiv.innerHTML = `
        <div style="padding: 16px;">
            <input type="search" 
                   placeholder="Search..." 
                   style="width: 100%; padding: 8px; border-radius: 4px; border: none;">
        </div>
    `;
    sidebar.insertBefore(searchDiv, sidebar.firstChild);
}
addSearchBar();