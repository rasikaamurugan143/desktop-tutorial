document.addEventListener('DOMContentLoaded', () => {
    initMatrixRain();
    
    const form = document.querySelector('#scan-form');
    const input = document.querySelector('#url-input');
    const scanBtn = document.querySelector('#scan-btn');
    const btnText = document.querySelector('.btn-text');
    
    const terminalOutput = document.querySelector('#terminal-output');
    const consoleLines = document.querySelector('#console-lines');
    
    const resultContainer = document.querySelector('#result-container');
    const resultCard = document.querySelector('#result-card');
    const resultIcon = document.querySelector('#result-icon');
    const resultTitle = document.querySelector('#result-title');
    const resultText = document.querySelector('#result-text');

    const icons = {
        success: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`,
        danger: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"></polygon><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`
    };

    const hackerLogs = [
        "Initializing payload deployment...",
        "Bypassing perimeter firewalls...",
        "Scraping DOM structure for zero-day signatures...",
        "Extracting visual hashes...",
        "Computing TF-IDF vector distances...",
        "Running Artificial Neural Network inference...",
        "Cross-referencing global threat databases...",
        "Decoupling heuristic results..."
    ];

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const urlValue = input.value.trim();
        if (!urlValue) return;

        // UI Scanning State
        scanBtn.classList.add('loading');
        btnText.textContent = "HACKING...";
        input.disabled = true;
        scanBtn.disabled = true;
        speedUpRain();
        
        resultContainer.classList.add('hidden');
        terminalOutput.classList.remove('hidden');
        consoleLines.innerHTML = '';

        // Simulate Terminal Typing
        let sysLogs = [];
        for (let i = 0; i < 5; i++) {
            const index = Math.floor(Math.random() * hackerLogs.length);
            sysLogs.push(`[SYS.PID_${Math.floor(Math.random()*9000)+1000}] ${hackerLogs[index]} <span class="highlight">OK</span>`);
        }
        
        for (let i = 0; i < sysLogs.length; i++) {
            await new Promise(r => setTimeout(r, 400 + Math.random() * 300));
            const li = document.createElement('li');
            li.innerHTML = sysLogs[i];
            consoleLines.appendChild(li);
        }

        // Fetch API
        try {
            consoleLines.innerHTML += `<li>[SYS.NET] Waiting for Engine response...</li>`;
            
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: urlValue })
            });
            
            const data = await response.json();

            consoleLines.innerHTML += `<li>[SYS.NET] <span class="highlight">Response received. Decoding stream...</span></li>`;
            await new Promise(r => setTimeout(r, 500));

            terminalOutput.classList.add('hidden');

            if (data.success) {
                if (data.is_phishing) {
                    setResultState('danger', 'THREAT DETECTED [!!!]', data.result);
                } else {
                    setResultState('success', 'SECURE [VERIFIED]', data.result);
                }
            } else {
                setResultState('danger', 'SYSTEM FAILURE', data.error || 'Connection broken.');
            }
        } catch (error) {
            setResultState('danger', 'FATAL ERROR', 'Neural Engine disconnected.');
        } finally {
            scanBtn.classList.remove('loading');
            btnText.textContent = "EXECUTE";
            input.disabled = false;
            scanBtn.disabled = false;
            input.focus();
            slowDownRain();
        }
    });

    function setResultState(type, title, text) {
        resultCard.className = `result-card ${type}`; // reset
        resultIcon.innerHTML = icons[type];
        resultTitle.textContent = title;
        resultText.textContent = text.replace(/🚨|✅/g, '').trim();
        resultContainer.classList.remove('hidden');
    }
});

// --- ENHANCED NEON CYBER FISHES ---
let fishSpeedMultiplier = 1;

function initMatrixRain() { // Kept name so we don't break existing calls
    const canvas = document.getElementById('matrix-bg');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    let width, height;
    function resize() {
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = width;
        canvas.height = height;
    }
    window.addEventListener('resize', resize);
    resize();

    const fishes = [];
    // Ultra vibrant cyber colors
    const colors = ['#00ff66', '#00e5ff', '#ff0055', '#ffaa00', '#aa00ff', '#ff00cc'];
    const count = 40; // Dense school of fishes

    for (let i = 0; i < count; i++) {
        fishes.push({
            x: Math.random() * width,
            y: Math.random() * height,
            size: Math.random() * 12 + 8, // Varying sizes
            speed: (Math.random() * 1.5 + 0.5),
            color: colors[Math.floor(Math.random() * colors.length)],
            wobble: Math.random() * Math.PI * 2,
            wobbleSpeed: Math.random() * 0.06 + 0.02
        });
    }

    function drawFish(ctx, f) {
        ctx.save();
        // Add wobble motion to y-axis
        ctx.translate(f.x, f.y + Math.sin(f.wobble) * 12);
        
        ctx.fillStyle = f.color;
        ctx.shadowBlur = 15;
        ctx.shadowColor = f.color;
        
        // Draw sleek, angular cyber-fish (arrow shape)
        ctx.beginPath();
        ctx.moveTo(f.size * 1.2, 0); // pointy nose
        ctx.lineTo(-f.size, -f.size * 0.6); // top tail fin
        ctx.lineTo(-f.size * 0.6, 0); // inner tail indent
        ctx.lineTo(-f.size, f.size * 0.6); // bottom tail fin
        ctx.closePath();
        ctx.fill();

        ctx.restore();
    }

    function draw() {
        // Translucent black to reveal fading water/grid trail
        ctx.fillStyle = 'rgba(3, 6, 10, 0.15)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        fishes.forEach(f => {
            drawFish(ctx, f);
            
            // Move fish leftwards across screen
            f.x -= f.speed * fishSpeedMultiplier;
            f.wobble += f.wobbleSpeed * fishSpeedMultiplier;

            // Reset fish to right side if it swims off screen left
            if (f.x < -f.size * 2) {
                f.x = width + f.size * 2;
                f.y = Math.random() * height;
            }
        });
        requestAnimationFrame(draw);
    }
    draw();
}

function speedUpRain() { fishSpeedMultiplier = 6; } // Fishes swim incredibly fast on scan!
function slowDownRain() { fishSpeedMultiplier = 1; }
