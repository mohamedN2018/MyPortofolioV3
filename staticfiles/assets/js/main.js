/**
 * Template Name: SnapFolio
 * Simplified & Fixed - Header Only Fix
 */

(function() {
    "use strict";

    // --- Helper function to get current direction (RTL/LTR) ---
    const getCurrentDirection = () => {
        const htmlDir = document.documentElement.getAttribute('dir');
        if (htmlDir === 'rtl') return 'rtl';
        const bodyDir = document.body.getAttribute('dir');
        if (bodyDir === 'rtl') return 'rtl';
        return 'ltr';
    };

    // --- Preloader - FIXED ---
    const preloader = document.querySelector('#preloader');
    if (preloader) {
        const hidePreloader = () => {
            preloader.style.opacity = '0';
            preloader.style.visibility = 'hidden';
            setTimeout(() => {
                if (preloader && preloader.parentNode) {
                    preloader.remove();
                }
            }, 300);
        };

        if (document.readyState === 'complete') {
            hidePreloader();
        } else {
            window.addEventListener('load', hidePreloader);
            setTimeout(hidePreloader, 3000);
        }
    }

    // --- Header Toggle (Mobile Menu) ---
    const header = document.querySelector('#header');
    const headerToggleBtn = document.querySelector('.header-toggle');
    const mobileMenuOverlay = document.querySelector('.mobile-menu-overlay');

    function headerToggle() {
        if (!header) return;
        header.classList.toggle('header-show');
        document.body.classList.toggle('menu-open');

        if (headerToggleBtn) {
            const toggleIcon = headerToggleBtn.querySelector('i');
            if (header.classList.contains('header-show')) {
                if (toggleIcon) {
                    toggleIcon.classList.remove('bi-list');
                    toggleIcon.classList.add('bi-x');
                }
                document.body.style.overflow = 'hidden';
            } else {
                if (toggleIcon) {
                    toggleIcon.classList.remove('bi-x');
                    toggleIcon.classList.add('bi-list');
                }
                document.body.style.overflow = '';
            }
        }
    }

    if (headerToggleBtn) {
        headerToggleBtn.addEventListener('click', headerToggle);
    }

    if (mobileMenuOverlay) {
        mobileMenuOverlay.addEventListener('click', () => {
            if (header && header.classList.contains('header-show')) {
                headerToggle();
            }
        });
    }

    document.querySelectorAll('#navmenu a').forEach(navmenu => {
        navmenu.addEventListener('click', () => {
            if (window.innerWidth <= 1199 && header && header.classList.contains('header-show')) {
                headerToggle();
            }
        });
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && header && header.classList.contains('header-show')) {
            headerToggle();
        }
    });

    window.addEventListener('resize', () => {
        if (window.innerWidth > 1199 && header && header.classList.contains('header-show')) {
            headerToggle();
            document.body.style.overflow = '';
        }
    });

    // --- Scroll top button ---
    let scrollTop = document.querySelector('.scroll-top');
    if (scrollTop) {
        function toggleScrollTop() {
            window.scrollY > 100 ? scrollTop.classList.add('active') : scrollTop.classList.remove('active');
        }
        scrollTop.addEventListener('click', (e) => {
            e.preventDefault();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
        window.addEventListener('load', toggleScrollTop);
        document.addEventListener('scroll', toggleScrollTop);
    }

    // --- Animation on scroll (AOS) ---
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 600,
            easing: 'ease-in-out',
            once: true,
            mirror: false
        });
    }

    // --- Typed.js ---
    const selectTyped = document.querySelector('.typed');
    if (selectTyped && typeof Typed !== 'undefined') {
        let typed_strings = selectTyped.getAttribute('data-typed-items');
        if (typed_strings) {
            typed_strings = typed_strings.split(',');
            new Typed('.typed', {
                strings: typed_strings,
                loop: true,
                typeSpeed: 100,
                backSpeed: 50,
                backDelay: 2000
            });
        }
    }

    // --- Pure Counter ---
    if (typeof PureCounter !== 'undefined') {
        new PureCounter();
    }

    // --- Skills Animation ---
    let skillsAnimation = document.querySelectorAll('.skills-animation');
    if (skillsAnimation.length > 0 && typeof Waypoint !== 'undefined') {
        skillsAnimation.forEach((item) => {
            new Waypoint({
                element: item,
                offset: '80%',
                handler: function(direction) {
                    let progress = item.querySelectorAll('.progress .progress-bar');
                    progress.forEach(el => {
                        el.style.width = el.getAttribute('aria-valuenow') + '%';
                    });
                }
            });
        });
    }

    // --- Glightbox ---
    if (typeof GLightbox !== 'undefined') {
        GLightbox({ selector: '.glightbox' });
    }

    // --- Navmenu Scrollspy ---
    let navmenulinks = document.querySelectorAll('.navmenu a');

    function navmenuScrollspy() {
        navmenulinks.forEach(navmenulink => {
            if (!navmenulink.hash) return;
            let section = document.querySelector(navmenulink.hash);
            if (!section) return;
            let position = window.scrollY + 200;
            if (position >= section.offsetTop && position <= (section.offsetTop + section.offsetHeight)) {
                document.querySelectorAll('.navmenu a.active').forEach(link => link.classList.remove('active'));
                navmenulink.classList.add('active');
            } else {
                navmenulink.classList.remove('active');
            }
        });
    }
    window.addEventListener('load', navmenuScrollspy);
    document.addEventListener('scroll', navmenuScrollspy);

    // --- Fix for hash links on page load ---
    window.addEventListener('load', function() {
        if (window.location.hash) {
            const targetElement = document.querySelector(window.location.hash);
            if (targetElement) {
                setTimeout(() => {
                    let scrollMarginTop = getComputedStyle(targetElement).scrollMarginTop;
                    window.scrollTo({
                        top: targetElement.offsetTop - parseInt(scrollMarginTop),
                        behavior: 'smooth'
                    });
                }, 100);
            }
        }
    });

})();