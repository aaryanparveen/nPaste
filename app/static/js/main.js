
document.addEventListener('DOMContentLoaded', () => {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    const copyBtn = document.getElementById('copyBtn');
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            const content = document.getElementById('pasteContent').innerText;
            navigator.clipboard.writeText(content).then(() => {
                const originalText = copyBtn.innerText;
                copyBtn.innerText = 'Copied!';
                setTimeout(() => copyBtn.innerText = originalText, 2000);
            });
        });
    }

    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const browseBtn = document.getElementById('browseBtn');
    const fileName = document.getElementById('fileName');

    if (uploadArea && fileInput) {
        browseBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.click();
        });

        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                fileName.textContent = `Selected: ${fileInput.files[0].name}`;
                uploadArea.classList.add('active');
            } else {
                fileName.textContent = '';
                uploadArea.classList.remove('active');
            }
        });

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });

        function highlight(e) {
            uploadArea.classList.add('active');
        }

        function unhighlight(e) {
            uploadArea.classList.remove('active');
        }

        uploadArea.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;

            if (files.length > 0) {
                fileInput.files = files;
                const event = new Event('change');
                fileInput.dispatchEvent(event);
            }
        }
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const el = document.getElementById('sortable-grid');
    if (el) {
        Sortable.create(el, {
            animation: 300,
            ghostClass: 'sortable-ghost',
            dragClass: 'sortable-drag',
            onStart: function () {
                document.body.style.cursor = 'grabbing';
            },
            onEnd: function () {
                document.body.style.cursor = 'default';
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const isMobile = window.innerWidth < 768 || /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

    if (isMobile) {
        console.log("Mobile device detected. Drag-and-drop disabled for scrolling.");
        return;
    }

    const el = document.getElementById('sortable-grid');
    if (el) {
        Sortable.create(el, {
            animation: 400,
            easing: "cubic-bezier(1, 0, 0, 1)",
            ghostClass: 'sortable-ghost',
            dragClass: 'sortable-drag',
            forceFallback: true, 
            fallbackClass: 'sortable-drag',
            delay: 0,
            onStart: function () {
                document.body.style.cursor = 'grabbing';
                document.body.classList.add('dragging');
            },
            onEnd: function () {
                document.body.style.cursor = 'default';
                document.body.classList.remove('dragging');
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', () => {
    console.log("Tilt Script Loaded Details");
    const cards = document.querySelectorAll('.bento-card');

    cards.forEach(card => {
        let isHovering = false;

        card.addEventListener('mouseenter', () => {
            isHovering = true;
        });

        card.addEventListener('mouseleave', () => {
            isHovering = false;
            card.style.transform = 'none';
        });

        card.addEventListener('mousemove', (e) => {
            if (!isHovering) return;

            requestAnimationFrame(() => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;

                const xPct = (x / rect.width) - 0.5;
                const yPct = (y / rect.height) - 0.5;

                const tiltX = yPct * -10;
                const tiltY = xPct * 10;

                card.style.transform = `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) scale3d(1.02, 1.02, 1.02)`;
            });
        });
    });
});
