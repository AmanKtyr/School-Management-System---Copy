// Advanced Responsive Sidebar with Enhanced Features
$(document).ready(function() {
    // Force AdminLTE to use our custom styles
    $.fn.overlayScrollbars = function() { return this; };

    // Configuration
    const CONFIG = {
        MOBILE_BREAKPOINT: 768,
        TABLET_BREAKPOINT: 992,
        SWIPE_THRESHOLD: 50,
        SWIPE_VELOCITY: 0.3,
        ANIMATION_DURATION: 300,
        DEBOUNCE_DELAY: 250,
        AUTO_CLOSE_DELAY: 150
    };

    // State management
    let sidebarState = {
        isOpen: false,
        isAnimating: false,
        lastTouchX: 0,
        startTouchX: 0,
        isDragging: false,
        userPreference: localStorage.getItem('sidebar-preference') || 'auto'
    };

    // Add colored icons to sidebar with enhanced animations
    function addColoredIcons() {
        const iconColors = [
            '#FF5252', '#4FC3F7', '#9C27B0', '#FFC107', '#4CAF50',
            '#FF9800', '#E91E63', '#9C27B0', '#FF5722', '#2196F3'
        ];

        $('.nav-sidebar .nav-item').each(function(index) {
            const $item = $(this);
            const color = iconColors[index % iconColors.length];
            const $icon = $item.find('.nav-link .nav-icon');

            $icon.css({
                'color': color,
                'transition': 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
            });

            // Add hover animation
            $item.find('.nav-link').hover(
                function() {
                    $icon.css('transform', 'scale(1.1) rotate(5deg)');
                },
                function() {
                    $icon.css('transform', 'scale(1) rotate(0deg)');
                }
            );
        });
    }

    // Enhanced performance monitoring
    function performanceMonitor() {
        if (window.performance && window.performance.mark) {
            window.performance.mark('sidebar-interaction-start');
        }
    }

    function performanceEnd(action) {
        if (window.performance && window.performance.mark && window.performance.measure) {
            window.performance.mark('sidebar-interaction-end');
            window.performance.measure(`sidebar-${action}`, 'sidebar-interaction-start', 'sidebar-interaction-end');
        }
    }

    // Enhanced device detection with user agent analysis
    function getDeviceInfo() {
        const width = $(window).width();
        const height = $(window).height();
        const userAgent = navigator.userAgent.toLowerCase();

        return {
            isMobile: width < CONFIG.MOBILE_BREAKPOINT,
            isTablet: width >= CONFIG.MOBILE_BREAKPOINT && width < CONFIG.TABLET_BREAKPOINT,
            isDesktop: width >= CONFIG.TABLET_BREAKPOINT,
            isMobileOrTablet: width < CONFIG.TABLET_BREAKPOINT,
            isTouch: 'ontouchstart' in window || navigator.maxTouchPoints > 0,
            isIOS: /ipad|iphone|ipod/.test(userAgent),
            isAndroid: /android/.test(userAgent),
            orientation: width > height ? 'landscape' : 'portrait',
            pixelRatio: window.devicePixelRatio || 1
        };
    }

    // Advanced overlay management with blur effect
    function createMobileOverlay() {
        if ($('.sidebar-overlay').length === 0) {
            const overlay = $('<div class="sidebar-overlay"></div>');
            overlay.css({
                'backdrop-filter': 'blur(2px)',
                '-webkit-backdrop-filter': 'blur(2px)'
            });
            $('body').append(overlay);
        }
    }

    // Enhanced overlay animations
    function showMobileOverlay() {
        const overlay = $('.sidebar-overlay');
        overlay.addClass('show');

        // Add body scroll lock
        $('body').addClass('sidebar-overlay-active');

        // Animate content blur
        $('.content-wrapper').css({
            'filter': 'blur(1px)',
            'transition': 'filter 0.3s ease'
        });
    }

    function hideMobileOverlay() {
        const overlay = $('.sidebar-overlay');
        overlay.removeClass('show');

        // Remove body scroll lock
        $('body').removeClass('sidebar-overlay-active');

        // Remove content blur
        $('.content-wrapper').css({
            'filter': 'none',
            'transition': 'filter 0.3s ease'
        });
    }

    // Swipe gesture detection
    function initSwipeGestures() {
        let startX, startY, startTime;
        const sidebar = $('.main-sidebar')[0];
        const overlay = $('.sidebar-overlay')[0];

        function handleTouchStart(e) {
            const touch = e.touches[0];
            startX = touch.clientX;
            startY = touch.clientY;
            startTime = Date.now();
            sidebarState.startTouchX = startX;
            sidebarState.isDragging = false;
        }

        function handleTouchMove(e) {
            if (!startX || !startY) return;

            const touch = e.touches[0];
            const deltaX = touch.clientX - startX;
            const deltaY = touch.clientY - startY;

            // Determine if this is a horizontal swipe
            if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 10) {
                sidebarState.isDragging = true;
                e.preventDefault();

                const deviceInfo = getDeviceInfo();
                if (deviceInfo.isMobileOrTablet) {
                    // Visual feedback during swipe
                    if (sidebarState.isOpen && deltaX < -CONFIG.SWIPE_THRESHOLD) {
                        const progress = Math.max(0, 1 + deltaX / 250);
                        $(sidebar).css('transform', `translateX(${deltaX}px)`);
                        $('.sidebar-overlay').css('opacity', progress);
                    } else if (!sidebarState.isOpen && deltaX > CONFIG.SWIPE_THRESHOLD && startX < 50) {
                        const progress = Math.min(1, deltaX / 250);
                        $(sidebar).css('transform', `translateX(${-100 + (progress * 100)}%)`);
                        $('.sidebar-overlay').css('opacity', progress);
                    }
                }
            }
        }

        function handleTouchEnd(e) {
            if (!startX || !sidebarState.isDragging) return;

            const touch = e.changedTouches[0];
            const deltaX = touch.clientX - startX;
            const deltaTime = Date.now() - startTime;
            const velocity = Math.abs(deltaX) / deltaTime;

            const deviceInfo = getDeviceInfo();
            if (deviceInfo.isMobileOrTablet) {
                // Reset transform
                $(sidebar).css('transform', '');
                $('.sidebar-overlay').css('opacity', '');

                // Determine action based on swipe
                if (velocity > CONFIG.SWIPE_VELOCITY || Math.abs(deltaX) > CONFIG.SWIPE_THRESHOLD) {
                    if (deltaX > 0 && !sidebarState.isOpen && startX < 50) {
                        openMobileSidebar();
                    } else if (deltaX < 0 && sidebarState.isOpen) {
                        closeMobileSidebar();
                    }
                }
            }

            // Reset values
            startX = startY = null;
            sidebarState.isDragging = false;
        }

        // Add touch listeners
        document.addEventListener('touchstart', handleTouchStart, { passive: false });
        document.addEventListener('touchmove', handleTouchMove, { passive: false });
        document.addEventListener('touchend', handleTouchEnd, { passive: false });
    }

    // Enhanced sidebar state management with animations
    function applySidebarStyles() {
        performanceMonitor();
        const deviceInfo = getDeviceInfo();

        if (deviceInfo.isMobileOrTablet) {
            // Mobile and tablet styles
            $('.content-wrapper, .main-footer, .main-header').css({
                'margin-left': '0',
                'width': '100%',
                'transition': 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
            });

            // Remove desktop-specific classes
            $('body').removeClass('sidebar-mini sidebar-collapse');

            // Add mobile-specific classes
            $('body').addClass('mobile-layout');

        } else {
            // Desktop styles with enhanced animations
            $('body').removeClass('mobile-layout');

            if ($('body').hasClass('sidebar-collapse')) {
                // Collapsed state with smooth animation
                $('.main-sidebar').css({
                    'width': '4.6rem',
                    'overflow': 'visible',
                    'transform': 'translateX(0)',
                    'transition': 'width 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                });

                $('.content-wrapper, .main-footer').css({
                    'margin-left': '4.6rem',
                    'width': 'calc(100% - 4.6rem)',
                    'transition': 'margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1), width 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                });
            } else {
                // Expanded state with smooth animation
                $('.main-sidebar').css({
                    'width': '250px',
                    'overflow': 'hidden',
                    'transform': 'translateX(0)',
                    'transition': 'width 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                });

                $('.content-wrapper, .main-footer').css({
                    'margin-left': '250px',
                    'width': 'calc(100% - 250px)',
                    'transition': 'margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1), width 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                });
            }

            // Hide mobile overlay on desktop
            hideMobileOverlay();
            $('body').removeClass('sidebar-open');
            sidebarState.isOpen = false;
        }

        performanceEnd('style-application');
    }

    // Enhanced mobile sidebar controls
    function openMobileSidebar() {
        if (sidebarState.isAnimating) return;

        performanceMonitor();
        sidebarState.isAnimating = true;
        sidebarState.isOpen = true;

        $('body').addClass('sidebar-open');
        showMobileOverlay();

        // Haptic feedback for supported devices
        if (navigator.vibrate) {
            navigator.vibrate(10);
        }

        setTimeout(() => {
            sidebarState.isAnimating = false;
            performanceEnd('sidebar-open');
        }, CONFIG.ANIMATION_DURATION);
    }

    function closeMobileSidebar() {
        if (sidebarState.isAnimating) return;

        performanceMonitor();
        sidebarState.isAnimating = true;
        sidebarState.isOpen = false;

        $('body').removeClass('sidebar-open');
        hideMobileOverlay();

        setTimeout(() => {
            sidebarState.isAnimating = false;
            performanceEnd('sidebar-close');
        }, CONFIG.ANIMATION_DURATION);
    }

    function toggleMobileSidebar() {
        const deviceInfo = getDeviceInfo();
        if (deviceInfo.isMobileOrTablet) {
            if (sidebarState.isOpen) {
                closeMobileSidebar();
            } else {
                openMobileSidebar();
            }
        }
    }

    // Smart auto-hide functionality
    function initAutoHide() {
        let inactivityTimer;
        const INACTIVITY_TIMEOUT = 30000; // 30 seconds

        function resetInactivityTimer() {
            clearTimeout(inactivityTimer);

            const deviceInfo = getDeviceInfo();
            if (deviceInfo.isMobileOrTablet && sidebarState.isOpen) {
                inactivityTimer = setTimeout(() => {
                    if (sidebarState.userPreference === 'auto') {
                        closeMobileSidebar();
                        showToast('Sidebar auto-hidden due to inactivity', 'info');
                    }
                }, INACTIVITY_TIMEOUT);
            }
        }

        // Track user activity
        $(document).on('touchstart mousedown keydown scroll', resetInactivityTimer);

        // Reset timer when sidebar opens
        $(document).on('sidebar-opened', resetInactivityTimer);
    }

    // Enhanced toast notifications
    function showToast(message, type = 'info', duration = 3000) {
        // Remove existing toasts
        $('.sidebar-toast').remove();

        const toast = $(`
            <div class="sidebar-toast sidebar-toast-${type}">
                <div class="sidebar-toast-content">
                    <i class="fas fa-${type === 'info' ? 'info-circle' : type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i>
                    <span>${message}</span>
                </div>
                <button class="sidebar-toast-close">&times;</button>
            </div>
        `);

        $('body').append(toast);

        // Animate in
        setTimeout(() => toast.addClass('show'), 100);

        // Auto remove
        setTimeout(() => {
            toast.removeClass('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);

        // Manual close
        toast.find('.sidebar-toast-close').on('click', () => {
            toast.removeClass('show');
            setTimeout(() => toast.remove(), 300);
        });
    }

    // Handle mobile sidebar toggle
    function toggleMobileSidebar() {
        if (getDeviceInfo().isMobileOrTablet) {
            if (sidebarState.isOpen) {
                closeMobileSidebar();
            } else {
                openMobileSidebar();
            }
        }
    }

    // Close mobile sidebar (now uses the enhanced version)
    function closeMobileSidebar() {
        const deviceInfo = getDeviceInfo();
        if (deviceInfo.isMobileOrTablet) {
            // Use the enhanced version from above
            if (sidebarState.isAnimating) return;

            performanceMonitor();
            sidebarState.isAnimating = true;
            sidebarState.isOpen = false;

            $('body').removeClass('sidebar-open');
            hideMobileOverlay();

            // Trigger custom event
            $(document).trigger('sidebar-closed');

            setTimeout(() => {
                sidebarState.isAnimating = false;
                performanceEnd('sidebar-close');
            }, CONFIG.ANIMATION_DURATION);
        }
    }

    // Smart sidebar settings panel
    function createSidebarSettings() {
        const settingsPanel = $(`
            <div class="sidebar-settings-panel">
                <div class="sidebar-settings-header">
                    <h6><i class="fas fa-cog"></i> Sidebar Settings</h6>
                    <button class="sidebar-settings-close">&times;</button>
                </div>
                <div class="sidebar-settings-content">
                    <div class="setting-group">
                        <label>Auto-hide behavior:</label>
                        <select class="sidebar-auto-hide-select">
                            <option value="auto">Smart auto-hide</option>
                            <option value="manual">Manual only</option>
                            <option value="always">Always visible</option>
                        </select>
                    </div>
                    <div class="setting-group">
                        <label>
                            <input type="checkbox" class="sidebar-animations-toggle" checked>
                            Enable animations
                        </label>
                    </div>
                    <div class="setting-group">
                        <label>
                            <input type="checkbox" class="sidebar-haptic-toggle" checked>
                            Haptic feedback
                        </label>
                    </div>
                </div>
            </div>
        `);

        $('body').append(settingsPanel);

        // Handle settings changes
        settingsPanel.find('.sidebar-auto-hide-select').on('change', function() {
            saveUserPreference($(this).val());
        });

        settingsPanel.find('.sidebar-settings-close').on('click', function() {
            settingsPanel.removeClass('show');
        });

        return settingsPanel;
    }

    // Initialize responsive sidebar with all features
    function initResponsiveSidebar() {
        // Create mobile overlay
        createMobileOverlay();

        // Add colored icons with animations
        addColoredIcons();

        // Initialize swipe gestures
        initSwipeGestures();

        // Initialize auto-hide functionality
        initAutoHide();

        // Create settings panel
        const settingsPanel = createSidebarSettings();

        // Apply initial styles
        applySidebarStyles();

        // Add smart indicator for mobile
        const deviceInfo = getDeviceInfo();
        if (deviceInfo.isMobileOrTablet) {
            $('.main-sidebar').append('<div class="sidebar-smart-indicator"></div>');
        }

        // Enhanced sidebar toggle with smart behavior
        $('[data-widget="pushmenu"]').off('click.responsive').on('click.responsive', function(e) {
            e.preventDefault();
            performanceMonitor();

            const deviceInfo = getDeviceInfo();
            if (deviceInfo.isMobileOrTablet) {
                toggleMobileSidebar();

                // Show helpful tip for first-time users
                if (!localStorage.getItem('sidebar-tip-shown')) {
                    setTimeout(() => {
                        showToast('Tip: Swipe from left edge to open sidebar, or tap outside to close', 'info', 5000);
                        localStorage.setItem('sidebar-tip-shown', 'true');
                    }, 1000);
                }
            } else {
                // Desktop behavior with enhanced animations
                $('body').toggleClass('sidebar-collapse');
                setTimeout(() => {
                    applySidebarStyles();
                    performanceEnd('desktop-toggle');
                }, CONFIG.ANIMATION_DURATION);
            }
        });

        // Enhanced overlay interactions
        $(document).off('click.overlay').on('click.overlay', '.sidebar-overlay', function(e) {
            if (e.target === this) {
                closeMobileSidebar();
            }
        });

        // Advanced keyboard shortcuts
        $(document).off('keydown.sidebar').on('keydown.sidebar', function(e) {
            const deviceInfo = getDeviceInfo();

            // ESC to close sidebar
            if (e.keyCode === 27 && sidebarState.isOpen) {
                closeMobileSidebar();
            }

            // Ctrl/Cmd + B to toggle sidebar
            if ((e.ctrlKey || e.metaKey) && e.keyCode === 66) {
                e.preventDefault();
                if (deviceInfo.isMobileOrTablet) {
                    toggleMobileSidebar();
                } else {
                    $('[data-widget="pushmenu"]').click();
                }
            }

            // Ctrl/Cmd + Shift + S to open settings
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.keyCode === 83) {
                e.preventDefault();
                settingsPanel.toggleClass('show');
            }
        });

        // Smart navigation link behavior
        $('.nav-sidebar .nav-link').off('click.mobile').on('click.mobile', function(e) {
            const deviceInfo = getDeviceInfo();
            const $link = $(this);

            if (deviceInfo.isMobileOrTablet) {
                // Add loading state
                $link.addClass('sidebar-loading');

                // Auto-close for non-treeview items
                if (!$link.parent().hasClass('has-treeview')) {
                    setTimeout(() => {
                        closeMobileSidebar();
                        $link.removeClass('sidebar-loading');
                    }, CONFIG.AUTO_CLOSE_DELAY);
                } else {
                    // Remove loading state for treeview items
                    setTimeout(() => $link.removeClass('sidebar-loading'), 300);
                }
            }
        });

        // Intelligent window resize handling
        $(window).off('resize.sidebar').on('resize.sidebar', function() {
            clearTimeout(window.sidebarResizeTimeout);
            window.sidebarResizeTimeout = setTimeout(() => {
                const oldDeviceInfo = getDeviceInfo();
                applySidebarStyles();
                const newDeviceInfo = getDeviceInfo();

                // Handle device type changes
                if (oldDeviceInfo.isMobileOrTablet !== newDeviceInfo.isMobileOrTablet) {
                    if (!newDeviceInfo.isMobileOrTablet) {
                        closeMobileSidebar();
                        showToast('Switched to desktop mode', 'info');
                    } else {
                        showToast('Switched to mobile mode', 'info');
                    }
                }

                performanceEnd('resize-handling');
            }, CONFIG.DEBOUNCE_DELAY);
        });

        // Enhanced AdminLTE event handling
        $(document).off('collapsed.lte.pushmenu shown.lte.pushmenu').on('collapsed.lte.pushmenu shown.lte.pushmenu', function(e) {
            const deviceInfo = getDeviceInfo();
            if (!deviceInfo.isMobileOrTablet) {
                setTimeout(() => {
                    applySidebarStyles();

                    // Show state change notification
                    const isCollapsed = $('body').hasClass('sidebar-collapse');
                    showToast(`Sidebar ${isCollapsed ? 'collapsed' : 'expanded'}`, 'success', 2000);
                }, CONFIG.ANIMATION_DURATION);
            }
        });

        // Advanced focus management
        $(document).on('sidebar-opened', function() {
            // Focus first navigation item for accessibility
            setTimeout(() => {
                $('.nav-sidebar .nav-link:first').focus();
            }, CONFIG.ANIMATION_DURATION);
        });

        // Performance monitoring
        if (window.performance && window.performance.mark) {
            window.performance.mark('sidebar-init-complete');
        }

        // Show initialization success
        setTimeout(() => {
            showToast('Responsive sidebar initialized successfully!', 'success', 3000);
        }, 500);
    }

    // Quick access menu functionality
    function initQuickAccess() {
        const quickAccessItems = [
            { icon: 'fas fa-tachometer-alt', text: 'Dashboard', url: '/dashboard/' },
            { icon: 'fas fa-user-graduate', text: 'Students', url: '/students/' },
            { icon: 'fas fa-users', text: 'Staff', url: '/staff/' },
            { icon: 'fas fa-calendar-check', text: 'Attendance', url: '/attendance/' }
        ];

        const quickAccess = $(`
            <div class="sidebar-quick-access">
                <div class="quick-access-header">
                    <i class="fas fa-bolt"></i> Quick Access
                </div>
                <div class="quick-access-items">
                    ${quickAccessItems.map(item => `
                        <a href="${item.url}" class="quick-access-item">
                            <i class="${item.icon}"></i>
                            <span>${item.text}</span>
                        </a>
                    `).join('')}
                </div>
            </div>
        `);

        $('.main-sidebar .sidebar').prepend(quickAccess);
    }

    // Advanced analytics and insights
    function initSidebarAnalytics() {
        const analytics = {
            sessionStart: Date.now(),
            interactions: 0,
            mostUsedItems: {},

            track(action, item = null) {
                this.interactions++;
                if (item) {
                    this.mostUsedItems[item] = (this.mostUsedItems[item] || 0) + 1;
                }

                // Send to analytics service (if available)
                if (window.gtag) {
                    window.gtag('event', 'sidebar_interaction', {
                        action: action,
                        item: item
                    });
                }
            },

            getInsights() {
                const sessionDuration = Date.now() - this.sessionStart;
                const mostUsed = Object.keys(this.mostUsedItems).reduce((a, b) =>
                    this.mostUsedItems[a] > this.mostUsedItems[b] ? a : b, null);

                return {
                    sessionDuration,
                    totalInteractions: this.interactions,
                    mostUsedItem: mostUsed,
                    averageInteractionRate: this.interactions / (sessionDuration / 60000) // per minute
                };
            }
        };

        // Track navigation clicks
        $('.nav-sidebar .nav-link').on('click', function() {
            const itemText = $(this).find('p').text().trim();
            analytics.track('navigation_click', itemText);
        });

        // Track sidebar toggles
        $('[data-widget="pushmenu"]').on('click', function() {
            analytics.track('sidebar_toggle');
        });

        return analytics;
    }

    // Initialize everything with enhanced features
    function initAdvancedSidebar() {
        // Core responsive functionality
        initResponsiveSidebar();

        // Quick access menu
        initQuickAccess();

        // Analytics tracking
        const analytics = initSidebarAnalytics();

        // Settings panel trigger
        $('#sidebar-settings-trigger').on('click', function(e) {
            e.preventDefault();
            $('.sidebar-settings-panel').toggleClass('show');
            analytics.track('settings_panel_toggle');
        });

        // Keyboard shortcuts help
        $(document).on('keydown', function(e) {
            // Ctrl/Cmd + Shift + H for help
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.keyCode === 72) {
                e.preventDefault();
                showKeyboardShortcutsHelp();
                analytics.track('help_shortcuts_shown');
            }
        });

        // Performance insights (development mode)
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            setTimeout(() => {
                const insights = analytics.getInsights();
                console.log('🚀 Sidebar Performance Insights:', insights);

                if (window.performance && window.performance.getEntriesByType) {
                    const measures = window.performance.getEntriesByType('measure');
                    const sidebarMeasures = measures.filter(m => m.name.includes('sidebar'));
                    console.log('📊 Sidebar Performance Measures:', sidebarMeasures);
                }
            }, 5000);
        }

        // Auto-save user preferences
        setInterval(() => {
            const currentState = {
                isOpen: sidebarState.isOpen,
                preference: sidebarState.userPreference,
                lastUsed: Date.now()
            };
            localStorage.setItem('sidebar-state', JSON.stringify(currentState));
        }, 30000); // Save every 30 seconds

        // Welcome message for new users
        if (!localStorage.getItem('sidebar-welcome-shown')) {
            setTimeout(() => {
                showToast('Welcome! Your sidebar is now fully responsive and smart. Try swiping or use Ctrl+B to toggle!', 'success', 6000);
                localStorage.setItem('sidebar-welcome-shown', 'true');
            }, 2000);
        }
    }

    // Keyboard shortcuts help modal
    function showKeyboardShortcutsHelp() {
        const helpModal = $(`
            <div class="sidebar-help-modal">
                <div class="sidebar-help-content">
                    <div class="sidebar-help-header">
                        <h5><i class="fas fa-keyboard"></i> Keyboard Shortcuts</h5>
                        <button class="sidebar-help-close">&times;</button>
                    </div>
                    <div class="sidebar-help-body">
                        <div class="shortcut-item">
                            <kbd>Ctrl</kbd> + <kbd>B</kbd>
                            <span>Toggle sidebar</span>
                        </div>
                        <div class="shortcut-item">
                            <kbd>Esc</kbd>
                            <span>Close sidebar (mobile)</span>
                        </div>
                        <div class="shortcut-item">
                            <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>S</kbd>
                            <span>Open settings</span>
                        </div>
                        <div class="shortcut-item">
                            <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>H</kbd>
                            <span>Show this help</span>
                        </div>
                    </div>
                </div>
            </div>
        `);

        $('body').append(helpModal);
        setTimeout(() => helpModal.addClass('show'), 100);

        helpModal.find('.sidebar-help-close').on('click', () => {
            helpModal.removeClass('show');
            setTimeout(() => helpModal.remove(), 300);
        });

        helpModal.on('click', function(e) {
            if (e.target === this) {
                helpModal.removeClass('show');
                setTimeout(() => helpModal.remove(), 300);
            }
        });
    }

    // Initialize the advanced sidebar system
    initAdvancedSidebar();

    // Reinitialize on AJAX content load
    $(document).on('DOMContentLoaded ajaxComplete', function() {
        addColoredIcons();
    });

    // Export for global access (if needed)
    window.SidebarSystem = {
        toggle: toggleMobileSidebar,
        open: openMobileSidebar,
        close: closeMobileSidebar,
        showSettings: () => $('.sidebar-settings-panel').addClass('show'),
        showHelp: showKeyboardShortcutsHelp,
        getState: () => sidebarState
    };
});
