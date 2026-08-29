function shootingStars(canvasId, options = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const colors = options.colors || ['#6ea8fe', '#f87171', '#4ade80', '#fbbf24', '#e879f9', '#e8e8e8'];
    const spawnChance = options.spawnChance ?? 0.02;
    const speed = options.speed ?? 8;
    const trailLength = options.trailLength ?? 80;

    let stars = [];
    let width, height;

    function resize() {
        width = canvas.width = canvas.offsetWidth;
        height = canvas.height = canvas.offsetHeight;
    }
    window.addEventListener('resize', resize);
    resize();

    function spawnStar() {
        const angle = (Math.PI / 4) + (Math.random() * 0.4 - 0.2);
        stars.push({
            x: Math.random() * width,
            y: -20,
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed,
            color: colors[Math.floor(Math.random() * colors.length)],
            life: 1,
        });
    }

    function draw() {
        ctx.clearRect(0, 0, width, height);

        if (Math.random() < spawnChance) spawnStar();

        stars = stars.filter(s => s.x < width + trailLength && s.y < height + trailLength && s.life > 0);

        for (const s of stars) {
            s.x += s.vx;
            s.y += s.vy;

            const tailX = s.x - s.vx * (trailLength / speed);
            const tailY = s.y - s.vy * (trailLength / speed);

            const gradient = ctx.createLinearGradient(s.x, s.y, tailX, tailY);
            gradient.addColorStop(0, s.color);
            gradient.addColorStop(1, 'transparent');

            ctx.strokeStyle = gradient;
            ctx.lineWidth = 2;
            ctx.lineCap = 'round';
            ctx.beginPath();
            ctx.moveTo(s.x, s.y);
            ctx.lineTo(tailX, tailY);
            ctx.stroke();

            ctx.fillStyle = s.color;
            ctx.beginPath();
            ctx.arc(s.x, s.y, 1.5, 0, Math.PI * 2);
            ctx.fill();
        }

        requestAnimationFrame(draw);
    }

    draw();
}