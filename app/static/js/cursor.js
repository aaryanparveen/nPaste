(function () {
    const canvas = document.createElement('canvas');
    canvas.style.cssText = 'position:fixed;inset:0;z-index:-1;pointer-events:none;opacity:0.4';
    document.body.appendChild(canvas);
    const ctx = canvas.getContext('2d');
    let w, h, particles = [];
    const COUNT = 35;

    function resize() {
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
    }

    function init() {
        resize();
        particles = [];
        for (let i = 0; i < COUNT; i++) {
            particles.push({
                x: Math.random() * w,
                y: Math.random() * h,
                r: Math.random() * 1.2 + 0.3,
                vx: (Math.random() - 0.5) * 0.15,
                vy: (Math.random() - 0.5) * 0.15,
                alpha: Math.random() * 0.3 + 0.05
            });
        }
    }

    function draw() {
        ctx.clearRect(0, 0, w, h);
        particles.forEach(p => {
            p.x += p.vx;
            p.y += p.vy;
            if (p.x < 0) p.x = w;
            if (p.x > w) p.x = 0;
            if (p.y < 0) p.y = h;
            if (p.y > h) p.y = 0;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(160,160,184,${p.alpha})`;
            ctx.fill();
        });
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 150) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(160,160,184,${0.03 * (1 - dist / 150)})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }
        }
        requestAnimationFrame(draw);
    }

    window.addEventListener('resize', resize);
    if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        init();
        draw();
    }
})();


document.addEventListener('DOMContentLoaded', () => {
    if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
        gsap.registerPlugin(ScrollTrigger);
    } else {
        console.warn("GSAP or ScrollTrigger not loaded.");
        return;
    }
    const heroWords = document.querySelectorAll('.morph-hero__word');
    if (heroWords.length > 0) {
        gsap.fromTo(heroWords,
            { y: 60, opacity: 0, scale: 0.9, rotateX: 20 },
            {
                y: 0,
                opacity: 1,
                scale: 1,
                rotateX: 0,
                duration: 1.2,
                ease: 'power4.out',
                stagger: 0.15,
                delay: 0.1
            }
        );
    }

    const heroSub = document.querySelector('.morph-hero__sub');
    if (heroSub) {
        gsap.fromTo(heroSub,
            { y: 20, opacity: 0 },
            { y: 0, opacity: 1, duration: 1, ease: 'power3.out', delay: 0.5 }
        );
    }
    const statNumbers = document.querySelectorAll('.morph-stat__number');
    statNumbers.forEach(stat => {
        const target = parseInt(stat.getAttribute('data-count') || '0', 10);
        if (target > 0) {
            gsap.fromTo(stat,
                { innerHTML: 0 },
                {
                    innerHTML: target,
                    duration: 2,
                    ease: 'power3.out',
                    snap: { innerHTML: 1 },
                    scrollTrigger: {
                        trigger: '.morph-stats',
                        start: 'top 90%'
                    }
                }
            );
        }
    });
    const uploadZone = document.querySelector('.upload-zone');
    if (uploadZone) {
        gsap.to(uploadZone, {
            scale: 1.01,
            boxShadow: '0 0 40px rgba(34, 197, 94, 0.15), inset 0 0 20px rgba(34, 197, 94, 0.05)',
            duration: 2.5,
            ease: 'sine.inOut',
            yoyo: true,
            repeat: -1
        });
    }
    const toolCards = document.querySelectorAll('.morph-tool-card');
    if (toolCards.length > 0) {
        ScrollTrigger.batch(toolCards, {
            start: "top 85%",
            onEnter: (elements) => {
                gsap.fromTo(elements,
                    { y: 40, opacity: 0, scale: 0.95 },
                    {
                        y: 0,
                        opacity: 1,
                        scale: 1,
                        duration: 0.8,
                        ease: 'power3.out',
                        stagger: 0.08,
                        overwrite: true
                    }
                );
            },
            onLeaveBack: (elements) => {
                gsap.set(elements, { y: 40, opacity: 0, scale: 0.95, overwrite: true });
            }
        });
    }
    gsap.utils.toArray('.morph-section__header').forEach(header => {
        gsap.fromTo(header,
            { y: 50, opacity: 0 },
            {
                scrollTrigger: {
                    trigger: header,
                    start: 'top 85%',
                },
                y: 0,
                opacity: 1,
                duration: 1,
                ease: 'power3.out'
            }
        );
    });

    gsap.utils.toArray('.deco-arc').forEach(arc => {
        gsap.fromTo(arc,
            { opacity: 0, scale: 0.9, y: 30 },
            {
                scrollTrigger: {
                    trigger: arc,
                    start: 'top 95%',
                },
                opacity: 0.1,
                scale: 1,
                y: 0,
                duration: 1.5,
                ease: 'power2.out'
            }
        );
    });
    const magneticElements = document.querySelectorAll('.btn, .morph-tool-card');
    magneticElements.forEach(elem => {
        elem.addEventListener('mousemove', (e) => {
            const rect = elem.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            gsap.to(elem, {
                x: x * 0.1,
                y: y * 0.1,
                duration: 0.4,
                ease: 'power2.out'
            });
        });

        elem.addEventListener('mouseleave', () => {
            gsap.to(elem, {
                x: 0,
                y: 0,
                duration: 0.6,
                ease: 'elastic.out(1, 0.3)'
            });
        });
    });
    window.showToast = function (message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = message;
        container.appendChild(toast);
        gsap.fromTo(toast,
            { x: 50, opacity: 0, scale: 0.9 },
            { x: 0, opacity: 1, scale: 1, duration: 0.6, ease: 'back.out(1.7)' }
        );

        setTimeout(() => {
            gsap.to(toast, {
                opacity: 0, x: 20, scale: 0.9, duration: 0.4, ease: 'power2.in',
                onComplete: () => toast.remove()
            });
        }, 4000);
    };
});
const cursor = document.createElement('div');
cursor.id = 'custom-cursor';
document.body.appendChild(cursor);

const cursorDot = document.createElement('div');
cursorDot.id = 'custom-cursor-dot';
document.body.appendChild(cursorDot);
window.originalDPR = window.originalDPR || window.devicePixelRatio;
let mouse = { x: -100, y: -100 };
let pos = { x: -100, y: -100 };
let posDot = { x: -100, y: -100 };
let hasMoved = false;
let currentRotation = 0;

window.addEventListener('mousemove', (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
    if (!hasMoved) {
        pos.x = mouse.x;
        pos.y = mouse.y;
        posDot.x = mouse.x;
        posDot.y = mouse.y;
        hasMoved = true;
    }
});

const setX = gsap.quickSetter(cursor, "x", "px");
const setY = gsap.quickSetter(cursor, "y", "px");
const setScaleX = gsap.quickSetter(cursor, "scaleX");
const setScaleY = gsap.quickSetter(cursor, "scaleY");
const setRotation = gsap.quickSetter(cursor, "rotation", "deg");
const setBorderRadius = gsap.quickSetter(cursor, "borderRadius");
const setBgColor = gsap.quickSetter(cursor, "backgroundColor");
const setMixBlendMode = gsap.quickSetter(cursor, "mixBlendMode");
const setBorder = gsap.quickSetter(cursor, "border");
const setWidth = gsap.quickSetter(cursor, "width", "px");
const setHeight = gsap.quickSetter(cursor, "height", "px");

const setDotX = gsap.quickSetter(cursorDot, "x", "px");
const setDotY = gsap.quickSetter(cursorDot, "y", "px");
const setDotWidth = gsap.quickSetter(cursorDot, "width", "px");
const setDotHeight = gsap.quickSetter(cursorDot, "height", "px");
const BASE_SIZE = 20;
function getZoom() {
    return window.devicePixelRatio / (window.screen.availWidth / window.innerWidth) || window.devicePixelRatio;
}
function getZoomScale() {
    if (window.visualViewport) {
        return window.visualViewport.scale;
    }
    return 1;
}
const baseDPR = window.devicePixelRatio;
function getZoomCompensation() {
    return baseDPR / window.devicePixelRatio;
}
let isHovering = false;
let hoverTarget = null;
let targetScale = 1;
let morphRadius = '50%';

const handleHoverEnter = (e) => {
    isHovering = true;
    hoverTarget = e.target;
    targetScale = 1.3;
    morphRadius = '50%';
    if (e.target.classList.contains('dash-card-head') || e.target.closest('button, a, .tool-card, .file-type-pill')) {
        targetScale = 1.6;
    }
};

const handleHoverLeave = () => {
    isHovering = false;
    hoverTarget = null;
    targetScale = 1;
    morphRadius = '50%';
};

const attachInteractivity = () => {
    const interactables = document.querySelectorAll('a, button, .dash-card-head, .tool-card, .file-type-pill');
    interactables.forEach(el => {
        el.removeEventListener('mouseenter', handleHoverEnter);
        el.removeEventListener('mouseleave', handleHoverLeave);
        el.addEventListener('mouseenter', handleHoverEnter);
        el.addEventListener('mouseleave', handleHoverLeave);
        el.style.cursor = 'none';
        Array.from(el.children).forEach(child => { if (child.style) child.style.cursor = 'none'; });
    });
};
setTimeout(attachInteractivity, 500);
function lerpAngle(from, to, t) {
    let diff = to - from;
    while (diff > 180) diff -= 360;
    while (diff < -180) diff += 360;
    return from + diff * t;
}
let smoothScaleX = 1;
let smoothScaleY = 1;
let smoothBorderOpacity = 0;
let smoothBgAlpha = 1;
let smoothMixBlend = 1;
function smoothDamp(speed, deltaRatio) {
    return 1.0 - Math.pow(1.0 - speed, deltaRatio);
}

gsap.ticker.add(() => {
    if (!hasMoved) return;

    const deltaRatio = gsap.ticker.deltaRatio(60);
    const posDt = smoothDamp(0.15, deltaRatio);
    pos.x += (mouse.x - pos.x) * posDt;
    pos.y += (mouse.y - pos.y) * posDt;
    const posDotDt = smoothDamp(0.6, deltaRatio);
    posDot.x += (mouse.x - posDot.x) * posDotDt;
    posDot.y += (mouse.y - posDot.y) * posDotDt;
    const vx = mouse.x - pos.x;
    const vy = mouse.y - pos.y;
    const velocity = Math.sqrt(vx * vx + vy * vy) / deltaRatio;
    const sizeMultiplier = (smoothScaleX + smoothScaleY) / 2;
    const stretch = Math.min(velocity * 0.008 * sizeMultiplier, 0.3 * sizeMultiplier);
    const velocityDeformX = 1 + stretch;
    const velocityDeformY = 1 - (stretch * 0.3);

    let velocityRotation = currentRotation;
    if (velocity > 2) {
        velocityRotation = Math.atan2(vy, vx) * (180 / Math.PI);
    }

    let wantScaleX = targetScale;
    let wantScaleY = targetScale;
    let wantRotation = currentRotation;
    let wantMixBlend = 1;
    let wantBorderStyle = 0;
    let wantBgAlpha = 1;

    let nearestDot = null;
    let minDist = Infinity;
    const dots = document.querySelectorAll('.dot');
    dots.forEach(dot => {
        const rect = dot.getBoundingClientRect();
        if (rect.width === 0 && rect.height === 0) return;
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        const dX = mouse.x - centerX;
        const dY = mouse.y - centerY;
        const dist = Math.sqrt(dX * dX + dY * dY);
        if (dist < minDist) {
            minDist = dist;
            nearestDot = dot;
        }
    });

    const tracerProximity = 30;
    const tracerMaxDist = 25;
    const isNearTracer = nearestDot && minDist < tracerProximity;

    if (isNearTracer) {
        const closeness = Math.min(1, Math.max(0, 1 - (minDist - tracerMaxDist) / (tracerProximity - tracerMaxDist)));

        const tracerBase = 1 + (closeness * 1.2);
        wantScaleX = tracerBase + stretch * 0.4;
        wantScaleY = tracerBase - (stretch * 0.15);

        wantRotation = velocityRotation;
        morphRadius = '50%';
        wantMixBlend = 1 - closeness;

        wantBorderStyle = closeness;
        wantBgAlpha = 1 - (closeness * 0.85);

    } else if (isHovering) {
        const deformFactor = 0.3;
        wantScaleX = targetScale + (stretch * deformFactor);
        wantScaleY = targetScale - (stretch * deformFactor * 0.25);

        wantRotation = velocity > 2 ? velocityRotation : 0;
        morphRadius = '50%';

        wantBorderStyle = 1;
        wantBgAlpha = 0.12;
        wantMixBlend = 1;

    } else {
        wantScaleX = velocityDeformX;
        wantScaleY = velocityDeformY;
        wantRotation = velocityRotation;
        morphRadius = '50%';
        wantBorderStyle = 0;
        wantBgAlpha = 1;
        wantMixBlend = 1;
    }
    const scaleDt = smoothDamp(0.22, deltaRatio);
    const rotDt = smoothDamp(0.4, deltaRatio);
    const styleDt = smoothDamp(0.1, deltaRatio);

    smoothScaleX += (wantScaleX - smoothScaleX) * scaleDt;
    smoothScaleY += (wantScaleY - smoothScaleY) * scaleDt;
    currentRotation = lerpAngle(currentRotation, wantRotation, rotDt);
    smoothBorderOpacity += (wantBorderStyle - smoothBorderOpacity) * styleDt;
    smoothBgAlpha += (wantBgAlpha - smoothBgAlpha) * styleDt;
    smoothMixBlend += (wantMixBlend - smoothMixBlend) * styleDt;
    const borderWeight = 1.5 + smoothBorderOpacity * 0.5;
    const borderAlpha = smoothBorderOpacity;
    const bgAlpha = smoothBgAlpha;

    let bgColor, border;
    if (borderAlpha > 0.01) {
        bgColor = `rgba(255, 255, 255, ${(bgAlpha * 0.95).toFixed(3)})`;
        border = `${borderWeight.toFixed(1)}px solid rgba(255, 255, 255, ${(0.6 + borderAlpha * 0.4).toFixed(3)})`;
    } else {
        bgColor = `rgba(255, 255, 255, ${bgAlpha.toFixed(3)})`;
        border = '0px solid transparent';
    }
    const mixBlend = smoothMixBlend > 0.5 ? 'difference' : 'normal';
    const zoomCompensation = baseDPR / window.devicePixelRatio;
    const size = BASE_SIZE * zoomCompensation;
    const half = size / 2;
    setX(pos.x - half);
    setY(pos.y - half);
    setWidth(size);
    setHeight(size);
    setScaleX(smoothScaleX);
    setScaleY(smoothScaleY);
    setRotation(currentRotation);
    setBorderRadius(morphRadius);
    setBgColor(bgColor);
    setBorder(border);
    setMixBlendMode(mixBlend);

    const dotSize = 4 * zoomCompensation;
    const dotHalf = dotSize / 2;
    setDotX(posDot.x - dotHalf);
    setDotY(posDot.y - dotHalf);
    setDotWidth(dotSize);
    setDotHeight(dotSize);
});

const observer = new MutationObserver(() => {
    attachInteractivity();
});
observer.observe(document.body, { childList: true, subtree: true });
