import React, { useEffect, useRef } from 'react';

interface MoneyParticle {
  x: number;
  y: number;
  size: number;
  speedY: number;
  rotation: number;
  rotationSpeed: number;
  opacity: number;
  symbol: string;
  color: string;
}

const MoneyRainBackground: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const moneySymbols = ['$', '¢', '£', '€', '¥', '₹', '₿'];
    const colors = ['#10b981', '#22c55e', '#16a34a', '#15803d', '#14532d'];
    const particles: MoneyParticle[] = [];

    const createParticle = (): MoneyParticle => {
      return {
        x: Math.random() * canvas.width,
        y: -50,
        size: Math.random() * 20 + 15,
        speedY: Math.random() * 2 + 1,
        rotation: Math.random() * Math.PI * 2,
        rotationSpeed: (Math.random() - 0.5) * 0.1,
        opacity: Math.random() * 0.3 + 0.2,
        symbol: moneySymbols[Math.floor(Math.random() * moneySymbols.length)],
        color: colors[Math.floor(Math.random() * colors.length)]
      };
    };

    // Create initial particles
    for (let i = 0; i < 50; i++) {
      const particle = createParticle();
      particle.y = Math.random() * canvas.height;
      particles.push(particle);
    }

    let lastTime = 0;
    const spawnInterval = 500; // Spawn new particle every 500ms

    const animate = (currentTime: number) => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Spawn new particles periodically
      if (currentTime - lastTime > spawnInterval) {
        particles.push(createParticle());
        lastTime = currentTime;
      }

      // Update and draw particles
      particles.forEach((particle, index) => {
        particle.y += particle.speedY;
        particle.rotation += particle.rotationSpeed;

        // Remove particles that have fallen off screen
        if (particle.y > canvas.height + 50) {
          particles.splice(index, 1);
          return;
        }

        // Draw money symbol with rotation
        ctx.save();
        ctx.translate(particle.x, particle.y);
        ctx.rotate(particle.rotation);
        
        // Add glow effect
        ctx.shadowBlur = 20;
        ctx.shadowColor = particle.color;
        
        ctx.font = `bold ${particle.size}px 'Orbitron', monospace`;
        ctx.fillStyle = particle.color;
        ctx.globalAlpha = particle.opacity;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(particle.symbol, 0, 0);
        
        ctx.restore();
      });

      // Keep particle count manageable
      if (particles.length > 100) {
        particles.splice(0, particles.length - 100);
      }

      requestAnimationFrame(animate);
    };

    animate(0);

    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0"
      style={{ opacity: 0.4 }}
    />
  );
};

export default MoneyRainBackground;