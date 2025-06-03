(function($) {
  "use strict"; // Start of use strict

  // Hide control sidebar
  $(document).ready(function() {
    $('.control-sidebar').remove();
    $('[data-widget="control-sidebar"]').remove();
    $('body').removeClass('control-sidebar-slide-open');
  });

  // Toggle the side navigation
  $("#sidebarToggle, #sidebarToggleTop").on('click', function(e) {
    $("body").toggleClass("sidebar-toggled");
    $(".sidebar").toggleClass("toggled");
    if ($(".sidebar").hasClass("toggled")) {
      $('.sidebar .collapse').collapse('hide');
    };
  });

  // Close any open menu accordions when window is resized below 768px
  $(window).resize(function() {
    if ($(window).width() < 768) {
      $('.sidebar .collapse').collapse('hide');
    };
  });

  // Prevent the content wrapper from scrolling when the fixed side navigation hovered over
  $('body.fixed-nav .sidebar').on('mousewheel DOMMouseScroll wheel', function(e) {
    if ($(window).width() > 768) {
      var e0 = e.originalEvent,
        delta = e0.wheelDelta || -e0.detail;
      this.scrollTop += (delta < 0 ? 1 : -1) * 30;
      e.preventDefault();
    }
  });

  // Scroll to top button appear
  $(document).on('scroll', function() {
    var scrollDistance = $(this).scrollTop();
    if (scrollDistance > 100) {
      $('.scroll-to-top').fadeIn();
    } else {
      $('.scroll-to-top').fadeOut();
    }
  });

  // Smooth scrolling using jQuery easing
  $(document).on('click', 'a.scroll-to-top', function(e) {
    var $anchor = $(this);
    $('html, body').stop().animate({
      scrollTop: ($($anchor.attr('href')).offset().top)
    }, 1000, 'easeInOutExpo');
    e.preventDefault();
  });

  // Make table rows clickable
  $('.clickable-row').css('cursor', 'pointer');
  $(".clickable-row").click(function () {
    window.location = $(this).data("href");
  });

  // Loader functions
  function showLoader() {
    document.querySelector('.loader-wrapper').classList.remove('loader-hidden');
  }

  function hideLoader() {
    document.querySelector('.loader-wrapper').classList.add('loader-hidden');
  }

  // Show loader when page starts loading
  document.addEventListener('DOMContentLoaded', function() {
    hideLoader();
  });

  // Show loader before page unload
  window.addEventListener('beforeunload', function() {
    showLoader();
  });

  // For AJAX requests
  $(document).ajaxStart(function() {
    showLoader();
  });

  $(document).ajaxStop(function() {
    hideLoader();
  });

})(jQuery); // End of use strict
