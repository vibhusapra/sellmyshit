import React, { useEffect, useRef } from 'react';

const MatrixTerminalBackground: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  // Crypto scam phrases and terms
  const cryptoTerms = [
    'BTC', 'ETH', 'DOGE', 'SHIB', 'PEPE', 'APE', 'MOON',
    '🚀TO THE MOON🚀', '💎DIAMOND HANDS💎', '🔥100X PUMP🔥',
    'HODL', 'WAGMI', 'NGMI', 'LFG', 'PUMP', 'DUMP', 'RUG',
    'WHALE ALERT', 'BULL RUN', 'BEAR TRAP', 'SHORT SQUEEZE',
    '0x1a2b3c4d5e6f...', '0xdeadbeef...', '0x420691337...',
    'PROFIT SECURED', 'DIAMOND HANDS', 'PAPER HANDS',
    'NOT FINANCIAL ADVICE', 'DYOR', 'NFA', 'SAFU',
    'WHEN LAMBO?', 'GM FRENS', 'LFG 🚀', 'NUMBER GO UP'
  ];

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Matrix rain settings
    const fontSize = 12;
    const columns = Math.floor(canvas.width / fontSize);
    const drops: number[] = new Array(columns).fill(1);
    
    // Different colors for different vibes
    const colors = ['#00ff41', '#39ff14', '#00ff00', '#32cd32', '#adff2f'];
    
    let animationId: number;

    const draw = () => {
      // Create trailing effect
      ctx.fillStyle = 'rgba(0, 0, 0, 0.04)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.font = `${fontSize}px 'Courier New', monospace`;
      
      for (let i = 0; i < drops.length; i++) {
        // Pick random crypto term
        const text = cryptoTerms[Math.floor(Math.random() * cryptoTerms.length)];
        
        // Random color from matrix palette
        ctx.fillStyle = colors[Math.floor(Math.random() * colors.length)];
        
        // Add glow effect for some characters
        if (Math.random() > 0.8) {
          ctx.shadowColor = ctx.fillStyle;
          ctx.shadowBlur = 10;
        } else {
          ctx.shadowBlur = 0;
        }
        
        const x = i * fontSize;
        const y = drops[i] * fontSize;
        
        // Draw the character/text
        if (text.length === 1) {
          ctx.fillText(text, x, y);
        } else {
          // For longer phrases, show them occasionally
          if (Math.random() > 0.95) {
            ctx.font = `${fontSize - 2}px 'Courier New', monospace`;
            ctx.fillText(text.substring(0, 10), x, y);
            ctx.font = `${fontSize}px 'Courier New', monospace`;
          } else {
            // Show individual characters from the phrase
            const char = text[Math.floor(Math.random() * text.length)];
            ctx.fillText(char, x, y);
          }
        }

        // Reset drop to top with some randomness
        if (y > canvas.height && Math.random() > 0.975) {
          drops[i] = 0;
        }
        
        drops[i]++;
      }

      animationId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(animationId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none opacity-60"
      style={{ zIndex: -1 }}
    />
  );
};

export default MatrixTerminalBackground;