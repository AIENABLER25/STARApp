/**
 * Document Link Manager - JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(flash => {
        setTimeout(() => {
            flash.style.opacity = '0';
            flash.style.transform = 'translateY(-10px)';
            setTimeout(() => flash.remove(), 300);
        }, 5000);
    });

    // Confirm before deleting
    const deleteForms = document.querySelectorAll('.delete-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to delete this entry?')) {
                e.preventDefault();
            }
        });
    });

    // Focus quick add input on page load (dashboard only)
    const quickAddInput = document.querySelector('.quick-add-input');
    if (quickAddInput && window.location.pathname === '/') {
        // Don't auto-focus on mobile
        if (window.innerWidth > 768) {
            quickAddInput.focus();
        }
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Press 'n' to go to add new link (when not in input)
        if (e.key === 'n' && !isInputFocused()) {
            window.location.href = '/add';
        }

        // Press '/' to focus quick add
        if (e.key === '/' && !isInputFocused()) {
            e.preventDefault();
            const quickAdd = document.querySelector('.quick-add-input');
            if (quickAdd) {
                quickAdd.focus();
            }
        }

        // Press 'Escape' to close dropdowns
        if (e.key === 'Escape') {
            document.activeElement.blur();
        }
    });

    // Handle dropdown positioning for overflow
    const dropdowns = document.querySelectorAll('.move-dropdown, .nav-dropdown');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('mouseenter', function() {
            const menu = this.querySelector('.dropdown-menu');
            if (menu) {
                const rect = menu.getBoundingClientRect();
                if (rect.right > window.innerWidth) {
                    menu.style.left = 'auto';
                    menu.style.right = '0';
                }
            }
        });
    });

    // Smooth scroll to section when clicking section headers
    const sectionHeaders = document.querySelectorAll('.section-header');
    sectionHeaders.forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            const section = this.closest('.section');
            const entries = section.querySelector('.entries-list');
            if (entries) {
                entries.classList.toggle('collapsed');
            }
        });
    });

    // Auto-generate title from URL (on add page)
    const urlInput = document.getElementById('url');
    const titleInput = document.getElementById('title');

    if (urlInput && titleInput) {
        urlInput.addEventListener('blur', function() {
            if (this.value && !titleInput.value) {
                // Extract a basic title from the URL
                const url = this.value;
                let title = '';

                try {
                    const urlObj = new URL(url);
                    const hostname = urlObj.hostname;

                    // Platform-specific title generation
                    if (hostname.includes('linkedin.com')) {
                        if (url.includes('/posts/')) {
                            title = 'LinkedIn Post';
                        } else if (url.includes('/pulse/')) {
                            title = 'LinkedIn Article';
                        } else {
                            title = 'LinkedIn Content';
                        }
                    } else if (hostname.includes('twitter.com') || hostname.includes('x.com')) {
                        title = 'Tweet';
                    } else if (hostname.includes('youtube.com') || hostname.includes('youtu.be')) {
                        title = 'YouTube Video';
                    } else {
                        // Use pathname for title
                        const path = urlObj.pathname;
                        const segments = path.split('/').filter(s => s);
                        if (segments.length > 0) {
                            title = segments[segments.length - 1]
                                .replace(/-/g, ' ')
                                .replace(/_/g, ' ')
                                .replace(/\.\w+$/, '')
                                .split(' ')
                                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                                .join(' ');
                        } else {
                            title = `Content from ${hostname}`;
                        }
                    }

                    titleInput.value = title;
                    titleInput.placeholder = title;
                } catch (e) {
                    // Invalid URL, ignore
                }
            }
        });
    }

    // Tags input helper - convert spaces to commas
    const tagsInput = document.getElementById('tags');
    if (tagsInput) {
        tagsInput.addEventListener('input', function() {
            // Optional: auto-convert spaces to commas for tags
        });
    }

    // Form validation feedback
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        inputs.forEach(input => {
            input.addEventListener('invalid', function() {
                this.classList.add('invalid');
            });
            input.addEventListener('input', function() {
                this.classList.remove('invalid');
            });
        });
    });
});

/**
 * Check if an input element is currently focused
 */
function isInputFocused() {
    const activeElement = document.activeElement;
    return activeElement && (
        activeElement.tagName === 'INPUT' ||
        activeElement.tagName === 'TEXTAREA' ||
        activeElement.tagName === 'SELECT' ||
        activeElement.isContentEditable
    );
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

/**
 * Show a temporary notification
 */
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `flash flash-${type}`;
    notification.innerHTML = `
        ${message}
        <button class="flash-close" onclick="this.parentElement.remove()">&times;</button>
    `;

    const container = document.querySelector('.flash-messages') || document.querySelector('.container');
    container.insertBefore(notification, container.firstChild);

    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * API helper for making fetch requests
 */
const api = {
    async get(url) {
        const response = await fetch(url);
        return response.json();
    },

    async post(url, data) {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        return response.json();
    }
};
