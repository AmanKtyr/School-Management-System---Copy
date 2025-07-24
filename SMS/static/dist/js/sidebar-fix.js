// Simple Sidebar fix script
$(document).ready(function() {
    // Force AdminLTE to use our custom styles
    $.fn.overlayScrollbars = function() { return this; };

    // Add colored icons to sidebar
    function addColoredIcons() {
        // Define colors for icons
        var iconColors = [
            '#FF5252', // red
            '#4FC3F7', // blue
            '#9C27B0', // purple
            '#FFC107', // yellow
            '#4CAF50', // green
            '#FF9800', // orange
            '#E91E63', // pink
            '#9C27B0', // purple
            '#FF5722', // deep orange
            '#2196F3'  // blue
        ];

        // Apply colors to icons
        $('.nav-sidebar .nav-item').each(function(index) {
            var color = iconColors[index % iconColors.length];
            $(this).find('.nav-link .nav-icon').css('color', color);
        });
    }

    // Apply sidebar styles based on current state
    function applySidebarStyles() {
        if ($('body').hasClass('sidebar-collapse')) {
            // Collapsed state
            $('.main-sidebar').css({
                'width': '4.6rem',
                'overflow': 'visible'
            });

            $('.content-wrapper').css({
                'margin-left': '4.6rem',
                'width': 'calc(100% - 4.6rem)'
            });

            $('.main-footer').css({
                'margin-left': '4.6rem',
                'width': 'calc(100% - 4.6rem)'
            });
        } else {
            // Expanded state
            $('.main-sidebar').css({
                'width': '250px',
                'overflow': 'hidden'
            });

            $('.content-wrapper').css({
                'margin-left': '250px',
                'width': 'calc(100% - 250px)'
            });

            $('.main-footer').css({
                'margin-left': '250px',
                'width': 'calc(100% - 250px)'
            });
        }
    }

    // Add colored icons
    addColoredIcons();

    // Apply styles on page load
    applySidebarStyles();

    // Handle sidebar toggle
    $('[data-widget="pushmenu"]').on('click', function() {
        // Let AdminLTE handle the toggle, then apply our styles
        setTimeout(function() {
            applySidebarStyles();
        }, 300);
    });

    // Handle window resize events
    $(window).resize(function() {
        applySidebarStyles();
    });

    // Fix for any AdminLTE events that might interfere
    $(document).on('collapsed.lte.pushmenu shown.lte.pushmenu', function() {
        setTimeout(function() {
            applySidebarStyles();
        }, 300);
    });
});
