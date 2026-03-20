document.addEventListener('DOMContentLoaded', () => {
    const container = document.createElement('div');
    container.id = 'particle-container';
    container.style.position = 'fixed';
    container.style.top = '0';
    container.style.left = '0';
    container.style.width = '100%';
    container.style.height = '100%';
    container.style.pointerEvents = 'none';
    container.style.zIndex = '-1'; 
    container.style.overflow = 'hidden';
    document.body.appendChild(container);

    const chars = 'NOVA';
    const particles = [];
    const maxParticles = 40; 

    function createParticle(x, y) {
        if (particles.length >= maxParticles) {
            const oldp = particles.shift();
            oldp.element.remove();
        }

        const el = document.createElement('div');
        el.classList.add('particle');
        el.innerText = chars.charAt(Math.floor(Math.random() * chars.length));

        const size = Math.random() * 2.5 + 2.0; 
        const opacity = Math.random() * 0.5 + 0.3; 

        el.style.fontSize = `${size}rem`;
        el.style.color = `rgba(211, 69, 91, ${opacity})`;
        el.style.position = 'absolute';
        el.style.userSelect = 'none';
        el.style.fontFamily = "'JetBrains Mono', monospace";
        el.style.transition = 'transform 0.1s ease-out';

        let posX;
        if (x) {
            posX = x;
        } else {
            const side = Math.random() > 0.5 ? 'left' : 'right';
            if (side === 'left') {
                posX = Math.random() * (window.innerWidth * 0.15); 
            } else {
                posX = window.innerWidth - (Math.random() * (window.innerWidth * 0.15)); 
            }
        }

        const posY = y || Math.random() * window.innerHeight;

        el.style.left = `${posX}px`;
        el.style.top = `${posY}px`;

        const depth = Math.random() * 2 + 1;

        container.appendChild(el);
        particles.push({ element: el, x: posX, y: posY, depth: depth });
    }

    for (let i = 0; i < 12; i++) {
        createParticle();
    }

    let mouseX = window.innerWidth / 2;
    let mouseY = window.innerHeight / 2;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;

        requestAnimationFrame(() => {
            particles.forEach(p => {
                const dx = (p.x - mouseX) / window.innerWidth;
                const dy = (p.y - mouseY) / window.innerHeight;

                const moveX = dx * 30 * p.depth;
                const moveY = dy * 30 * p.depth;

                p.element.style.transform = `translate(${moveX}px, ${moveY}px)`;
            });
        });
    });

    let lastScrollY = window.scrollY;
    let scrollAccumulator = 0;

    document.addEventListener('scroll', () => {
        const currentScrollY = window.scrollY;
        const delta = Math.abs(currentScrollY - lastScrollY);
        lastScrollY = currentScrollY;
        scrollAccumulator += delta;

        if (scrollAccumulator > 100) {
            createParticle(Math.random() * window.innerWidth, Math.random() * window.innerHeight);
            scrollAccumulator = 0;
        }

    });
});
