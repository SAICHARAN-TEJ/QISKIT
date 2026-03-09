/* Landing page JS — ResQbit */

'use strict';

// ─── Modal logic ─────────────────────────────────────────────
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

// Close modal on overlay click
document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', e => {
        if (e.target === overlay) {
            overlay.querySelectorAll('[id$="Modal"]').forEach(m => closeModal(m.id));
            closeModal(overlay.id);
        }
    });
});

// Close on Escape
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay.active').forEach(m => closeModal(m.id));
    }
});

// ─── Nav scroll effect ────────────────────────────────────────
const nav = document.getElementById('mainNav');
if (nav) {
    window.addEventListener('scroll', () => {
        if (window.scrollY > 20) {
            nav.style.background = 'rgba(10, 10, 12, 0.75)';
            nav.style.borderColor = 'rgba(255,255,255,0.10)';
        } else {
            nav.style.background = 'rgba(10, 10, 12, 0.4)';
            nav.style.borderColor = 'rgba(255,255,255,0.08)';
        }
    }, { passive: true });
}

// ─── Animations & Smooth Scroll ──────────────────────────────────
function initAnimations() {
    // 1. Initialize Lenis Smooth Scroll
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

        // Get scroll value
        lenis.on('scroll', ScrollTrigger.update);

        gsap.ticker.add((time) => {
            lenis.raf(time * 1000);
        });

        gsap.ticker.lagSmoothing(0);
    }

    // 2. Custom Cursor Tracking
    const cursor = document.querySelector('.custom-cursor');
    const follower = document.querySelector('.custom-cursor-follower');
    if (cursor && follower) {
        gsap.set(cursor, { xPercent: -50, yPercent: -50 });
        gsap.set(follower, { xPercent: -50, yPercent: -50 });

        let mX = 0, mY = 0;
        window.addEventListener('mousemove', e => {
            mX = e.clientX;
            mY = e.clientY;
            // Immediate
            gsap.to(cursor, { x: mX, y: mY, duration: 0, ease: "none" });
            // Delayed follower
            gsap.to(follower, { x: mX, y: mY, duration: 0.6, ease: "power3.out" });
        });

        // Hover states
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

    // 3. Text Reveal Animations (SplitType)
    if (typeof SplitType !== 'undefined') {
        // Hero Title stagger
        const heroTitle = new SplitType('.hero-title', { types: 'lines, words, chars' });
        gsap.from(heroTitle.chars, {
            y: 100,
            opacity: 0,
            duration: 1,
            stagger: 0.02,
            ease: "power4.out",
            delay: 0.2
        });

        // Section Titles mask-up (Obsidian style)
        const blockTitles = document.querySelectorAll('.section-title');
        blockTitles.forEach(title => {
            const split = new SplitType(title, { types: 'lines, words, chars' });
            // wrap lines in overflow hidden for masking
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

    // 4. Parallax & Fade (General .reveal items)
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

    // 5. Image Parallax (Hero Visual Box)
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

// ─── Login ────────────────────────────────────────────────────
async function handleLogin(e) {
    e.preventDefault();
    const btn = document.getElementById('loginSubmitBtn');
    const errEl = document.getElementById('loginError');
    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;

    setButtonLoading(btn, true);
    hideError(errEl);

    try {
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await res.json();
        if (res.ok) {
            window.location.href = '/dashboard';
        } else {
            showError(errEl, data.error || 'Invalid credentials');
        }
    } catch {
        showError(errEl, 'Network error. Please try again.');
    } finally {
        setButtonLoading(btn, false);
    }
}

// ─── Register ─────────────────────────────────────────────────
async function handleRegister(e) {
    e.preventDefault();
    const btn = document.getElementById('registerSubmitBtn');
    const errEl = document.getElementById('registerError');
    const username = document.getElementById('regUsername').value.trim();
    const email = document.getElementById('regEmail').value.trim();
    const password = document.getElementById('regPassword').value;

    setButtonLoading(btn, true);
    hideError(errEl);

    try {
        const res = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });
        const data = await res.json();
        if (res.ok) {
            // Auto-login after register
            const loginRes = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            if (loginRes.ok) {
                window.location.href = '/dashboard';
            } else {
                switchModal('registerModal', 'loginModal');
            }
        } else {
            showError(errEl, data.error || 'Registration failed');
        }
    } catch {
        showError(errEl, 'Network error. Please try again.');
    } finally {
        setButtonLoading(btn, false);
    }
}

// ─── Helpers ──────────────────────────────────────────────────
function setButtonLoading(btn, loading) {
    if (!btn) return;
    if (loading) {
        btn.dataset.original = btn.textContent;
        btn.textContent = 'Please wait…';
        btn.disabled = true;
    } else {
        btn.textContent = btn.dataset.original || 'Submit';
        btn.disabled = false;
    }
}

function showError(el, msg) {
    if (!el) return;
    el.style.cssText = 'display:block;background:rgba(255,107,107,0.08);border:1px solid rgba(255,107,107,0.25);border-radius:10px;padding:12px 16px;font-size:0.9rem;color:#ff6b6b;margin-bottom:16px;';
    el.textContent = msg;
}

function hideError(el) {
    if (el) el.style.display = 'none';
}

// ─── Init ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    initAnimations();

    // Add enter-key support to forms
    document.getElementById('loginForm')?.addEventListener('submit', handleLogin);
    document.getElementById('registerForm')?.addEventListener('submit', handleRegister);

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', e => {
            const target = document.querySelector(anchor.getAttribute('href'));
            if (target) {
                e.preventDefault();
                // Lenis Handles native scrollIntoView gracefully
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
});
