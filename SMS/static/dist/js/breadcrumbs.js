/**
 * Professional Breadcrumbs Functionality
 * This script enhances breadcrumb navigation with consistent styling and behavior:
 * 1. Formats text for better readability (replaces hyphens with spaces, capitalizes words)
 * 2. Adds appropriate icons based on breadcrumb content
 * 3. Applies consistent styling to all breadcrumbs
 * 4. Adds subtle animation effects for a professional look
 * 5. Ensures proper navigation between related pages
 */

document.addEventListener('DOMContentLoaded', function() {
    // Ensure all breadcrumb containers have consistent styling
    const breadcrumbContainers = document.querySelectorAll('.breadcrumb-container, .container nav[aria-label="breadcrumb"]');
    breadcrumbContainers.forEach(container => {
        // If the container is not already a breadcrumb-container, wrap its contents
        if (!container.classList.contains('breadcrumb-container')) {
            const parent = container.parentNode;
            const wrapper = document.createElement('div');
            wrapper.className = 'breadcrumb-container';
            parent.insertBefore(wrapper, container);
            wrapper.appendChild(container);
        }

        // Ensure all breadcrumb lists have the professional class
        const breadcrumbList = container.querySelector('.breadcrumb');
        if (breadcrumbList && !breadcrumbList.classList.contains('breadcrumb-chevron')) {
            breadcrumbList.classList.add('breadcrumb-chevron');
        }
    });

    // Format breadcrumb text (replace hyphens with spaces and capitalize)
    const breadcrumbItems = document.querySelectorAll('.breadcrumb-item');

    breadcrumbItems.forEach(item => {
        // Skip items with manually set icons
        if (!item.querySelector('i') && item.textContent.trim() !== 'Home') {
            const text = item.textContent.trim();
            // Format text: replace hyphens with spaces and capitalize each word
            const formattedText = text
                .replace(/-/g, ' ')
                .replace(/\w\S*/g, txt => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase());

            // Update text content
            if (item.querySelector('a')) {
                // For links, preserve the link but update text
                const link = item.querySelector('a');
                if (!link.querySelector('i')) {
                    link.textContent = formattedText;
                }
            } else {
                item.textContent = formattedText;
            }
        }
    });

    // Add appropriate icons based on breadcrumb content if not already present
    breadcrumbItems.forEach(item => {
        const text = item.textContent.trim().toLowerCase();
        const link = item.querySelector('a');
        const isActive = item.classList.contains('active');

        // Function to add icon
        const addIcon = (element, iconClass) => {
            if (!element.querySelector('i')) {
                const icon = document.createElement('i');
                icon.className = iconClass;
                icon.style.marginRight = '0.5rem';
                element.insertBefore(icon, element.firstChild);
            }
        };

        // Determine icon based on text content
        let iconClass = 'fas fa-link'; // Default icon

        if (text.includes('student')) {
            iconClass = 'fas fa-user-graduate';
        } else if (text.includes('staff') || text.includes('teacher')) {
            iconClass = 'fas fa-chalkboard-teacher';
        } else if (text.includes('class')) {
            iconClass = 'fas fa-school';
        } else if (text.includes('subject')) {
            iconClass = 'fas fa-book';
        } else if (text.includes('attendance')) {
            iconClass = 'fas fa-calendar-check';
        } else if (text.includes('result') || text.includes('exam')) {
            iconClass = 'fas fa-clipboard-list';
        } else if (text.includes('fee') || text.includes('finance')) {
            iconClass = 'fas fa-money-bill-wave';
        } else if (text.includes('setting')) {
            iconClass = 'fas fa-cog';
        } else if (text.includes('session')) {
            iconClass = 'fas fa-calendar-alt';
        } else if (text.includes('term')) {
            iconClass = 'fas fa-clock';
        } else if (text.includes('dashboard')) {
            iconClass = 'fas fa-tachometer-alt';
        } else if (text.includes('management')) {
            iconClass = 'fas fa-copy';
        } else if (text.includes('list')) {
            iconClass = 'fas fa-list';
        } else if (text.includes('detail')) {
            iconClass = 'fas fa-info-circle';
        } else if (text.includes('form') || text.includes('create') || text.includes('add')) {
            iconClass = 'fas fa-plus-circle';
        } else if (text.includes('edit') || text.includes('update')) {
            iconClass = 'fas fa-edit';
        } else if (text.includes('delete')) {
            iconClass = 'fas fa-trash-alt';
        }

        // Add icon to link or active item
        if (link) {
            addIcon(link, iconClass);
        } else if (isActive) {
            addIcon(item, iconClass);
        }
    });

    // Ensure all breadcrumb links have consistent styling
    const breadcrumbLinks = document.querySelectorAll('.breadcrumb-item a');
    breadcrumbLinks.forEach(link => {
        if (!link.classList.contains('text-decoration-none')) {
            link.classList.add('text-decoration-none');
        }
        if (!link.classList.contains('fw-bold')) {
            link.classList.add('fw-bold');
        }
    });

    // Add animation effect to breadcrumb items
    breadcrumbItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transition = 'opacity 0.3s ease';

        setTimeout(() => {
            item.style.opacity = '1';
        }, 100 * (index + 1));
    });

    // Fix navigation for fee-related pages
    // This ensures proper breadcrumb navigation between related fee pages
    const currentPath = window.location.pathname;

    // Helper function to check if we're on a specific page
    const isOnPage = (urlPattern) => currentPath.includes(urlPattern);

    // Fix navigation for fee-related pages
    if (isOnPage('/fees/')) {
        // Make sure fee management links are properly connected
        const feeManagementLinks = document.querySelectorAll('a[href*="fee_list"]');
        feeManagementLinks.forEach(link => {
            // Ensure the link is properly styled
            link.classList.add('text-decoration-none', 'fw-bold');

            // Make sure it has the correct icon
            if (!link.querySelector('i.fas.fa-money-bill-wave')) {
                const existingIcon = link.querySelector('i');
                if (existingIcon) {
                    existingIcon.className = 'fas fa-money-bill-wave';
                } else {
                    const icon = document.createElement('i');
                    icon.className = 'fas fa-money-bill-wave me-2';
                    link.insertBefore(icon, link.firstChild);
                }
            }
        });

        // Fix student fee history links
        if (isOnPage('/fees/history/')) {
            const historyLinks = document.querySelectorAll('a[href*="student_fee_history"]');
            historyLinks.forEach(link => {
                link.classList.add('text-decoration-none', 'fw-bold');

                if (!link.querySelector('i.fas.fa-history')) {
                    const existingIcon = link.querySelector('i');
                    if (existingIcon) {
                        existingIcon.className = 'fas fa-history';
                    } else {
                        const icon = document.createElement('i');
                        icon.className = 'fas fa-history me-2';
                        link.insertBefore(icon, link.firstChild);
                    }
                }
            });
        }

        // Fix add payment links
        if (isOnPage('/fees/add-payment/')) {
            const paymentLinks = document.querySelectorAll('a[href*="add_fee_payment"]');
            paymentLinks.forEach(link => {
                link.classList.add('text-decoration-none', 'fw-bold');

                if (!link.querySelector('i.fas.fa-credit-card')) {
                    const existingIcon = link.querySelector('i');
                    if (existingIcon) {
                        existingIcon.className = 'fas fa-credit-card';
                    } else {
                        const icon = document.createElement('i');
                        icon.className = 'fas fa-credit-card me-2';
                        link.insertBefore(icon, link.firstChild);
                    }
                }
            });
        }

        // Fix receipt links
        if (isOnPage('/fees/receipt/')) {
            const receiptLinks = document.querySelectorAll('a[href*="generate_receipt"]');
            receiptLinks.forEach(link => {
                link.classList.add('text-decoration-none', 'fw-bold');

                if (!link.querySelector('i.fas.fa-file-invoice')) {
                    const existingIcon = link.querySelector('i');
                    if (existingIcon) {
                        existingIcon.className = 'fas fa-file-invoice';
                    } else {
                        const icon = document.createElement('i');
                        icon.className = 'fas fa-file-invoice me-2';
                        link.insertBefore(icon, link.firstChild);
                    }
                }
            });
        }
    }
});
