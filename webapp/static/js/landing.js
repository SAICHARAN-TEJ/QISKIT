/* Landing page JS - QiskitML */

'use strict';

function openModal(id) {
    const el = document.getElementById(id);
    if (!el) return;
    document.body.style.overflow = 'hidden';
    el.style.display = 'flex';
    requestAnimationFrame(() => el.classList.add('active'));
}

function closeModal(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.remove('active');
    setTimeout(() => {
        el.style.display = 'none';
        document.body.style.overflow = '';
    }, 350);
}

function switchModal(from, to) {
    closeModal(from);
    setTimeout(() => openModal(to), 380);
}

document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', e => {
        if (e.target === overlay) {
            overlay.querySelectorAll('[id$="Modal"]').forEach(m => closeModal(m.id));
            closeModal(overlay.id);
        }
    });
});

document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay.active').forEach(m => closeModal(m.id));
    }
});

const nav = document.getElementById('mainNav');
if (nav) {
    window.addEventListener('scroll', () => {
        if (window.scrollY > 20) {
            nav.style.background = 'rgba(18, 18, 26, 0.95)';
            nav.style.borderColor = 'rgba(0, 212, 255, 0.2)';
        } else {
            nav.style.background = 'rgba(18, 18, 26, 0.85)';
            nav.style.borderColor = 'rgba(0, 212, 255, 0.1)';
        }
    }, { passive: true });
}

function initAnimations() {
    if (typeof Lenis !== 'undefined') {
        const lenis = new Lenis({
            duration: 1.2,
            easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
            direction: 'vertical',
            gestureDirection: 'vertical',
            smooth: true,
            mouseMultiplier: 1,
            smoothTouch: false,
            touchMultiplier: 2,
            infinite: false,
        });

        lenis.on('scroll', ScrollTrigger.update);

        gsap.ticker.add((time) => {
            lenis.raf(time * 1000);
        });

        gsap.ticker.lagSmoothing(0);
    }

    const cursor = document.querySelector('.custom-cursor');
    const follower = document.querySelector('.custom-cursor-follower');
    if (cursor && follower) {
        gsap.set(cursor, { xPercent: -50, yPercent: -50 });
        gsap.set(follower, { xPercent: -50, yPercent: -50 });

        let mX = 0, mY = 0;
        window.addEventListener('mousemove', e => {
            mX = e.clientX;
            mY = e.clientY;
            gsap.to(cursor, { x: mX, y: mY, duration: 0, ease: "none" });
            gsap.to(follower, { x: mX, y: mY, duration: 0.6, ease: "power3.out" });
        });

        const hoverTargets = document.querySelectorAll('a, button, input, .feature-card, .hiw-step');
        hoverTargets.forEach(el => {
            el.addEventListener('mouseenter', () => {
                cursor.classList.add('hover');
                follower.classList.add('hover');
            });
            el.addEventListener('mouseleave', () => {
                cursor.classList.remove('hover');
                follower.classList.remove('hover');
            });
        });
    }

    if (typeof SplitType !== 'undefined') {
        const heroTitle = new SplitType('.hero-title', { types: 'lines, words, chars' });
        gsap.from(heroTitle.chars, {
            y: 100,
            opacity: 0,
            duration: 1,
            stagger: 0.02,
            ease: "power4.out",
            delay: 0.2
        });

        const blockTitles = document.querySelectorAll('.section-title');
        blockTitles.forEach(title => {
            const split = new SplitType(title, { types: 'lines, words, chars' });
            split.lines.forEach(line => {
                const wrapper = document.createElement('div');
                wrapper.style.overflow = 'hidden';
                line.parentNode.insertBefore(wrapper, line);
                wrapper.appendChild(line);
            });

            gsap.from(split.chars, {
                scrollTrigger: {
                    trigger: title,
                    start: "top 85%",
                },
                yPercent: 120,
                duration: 0.8,
                stagger: 0.02,
                ease: "power3.out"
            });
        });
    }

    const fadeItems = document.querySelectorAll('.reveal');
    fadeItems.forEach(item => {
        gsap.from(item, {
            scrollTrigger: {
                trigger: item,
                start: "top 85%",
            },
            y: 60,
            opacity: 0,
            duration: 1,
            ease: "power3.out",
            clearProps: "all"
        });
    });

    const heroBox = document.querySelector('.hero-visual');
    if (heroBox) {
        gsap.to(heroBox, {
            yPercent: 15,
            ease: "none",
            scrollTrigger: {
                trigger: ".hero-section",
                start: "top top",
                end: "bottom top",
                scrub: true
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initAnimations();

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', e => {
            const target = document.querySelector(anchor.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
});
