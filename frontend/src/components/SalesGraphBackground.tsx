import React, { useEffect, useRef } from 'react';

interface ChartLine {
  points: { x: number; y: number }[];
  color: string;
  strokeWidth: number;
}

const SalesGraphBackground: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const chartLines: ChartLine[] = [];
    const colors = ['#10b981', '#22c55e', '#9333ea', '#ec4899', '#3b82f6'];
    
    // Create multiple animated chart lines
    for (let i = 0; i < 5; i++) {
      const points = [];
      const segments = 10;
      const segmentWidth = canvas.width / segments;
      
      for (let j = 0; j <= segments; j++) {
        points.push({
          x: j * segmentWidth,
          y: canvas.height * 0.5 + (Math.random() - 0.5) * canvas.height * 0.3
        });
      }
      
      chartLines.push({
        points,
        color: colors[i % colors.length],
        strokeWidth: Math.random() * 2 + 1
      });
    }

    let offset = 0;

    const drawChart = (line: ChartLine, time: number) => {
      ctx.beginPath();
      ctx.strokeStyle = line.color;
      ctx.lineWidth = line.strokeWidth;
      ctx.globalAlpha = 0.3;
      
      // Add glow effect
      ctx.shadowBlur = 15;
      ctx.shadowColor = line.color;

      // Draw smooth curve through points
      line.points.forEach((point, index) => {
        const x = point.x - offset;
        const y = point.y + Math.sin((time + index * 100) * 0.001) * 20;
        
        if (index === 0) {
          ctx.moveTo(x, y);
        } else {
          const prevPoint = line.points[index - 1];
          const prevX = prevPoint.x - offset;
          const prevY = prevPoint.y + Math.sin((time + (index - 1) * 100) * 0.001) * 20;
          
          const cpx = (prevX + x) / 2;
          const cpy = (prevY + y) / 2;
          
          ctx.quadraticCurveTo(prevX, prevY, cpx, cpy);
        }
      });
      
      ctx.stroke();
      
      // Reset shadow for next draw
      ctx.shadowBlur = 0;
    };

    const drawGrid = () => {
      ctx.strokeStyle = 'rgba(147, 51, 234, 0.1)';
      ctx.lineWidth = 1;
      ctx.globalAlpha = 1;
      
      // Vertical lines
      for (let x = 0; x < canvas.width; x += 50) {
        ctx.beginPath();
        ctx.moveTo(x - (offset % 50), 0);
        ctx.lineTo(x - (offset % 50), canvas.height);
        ctx.stroke();
      }
      
      // Horizontal lines
      for (let y = 0; y < canvas.height; y += 50) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
      }
    };

    const drawPriceTag = (x: number, y: number, price: string, time: number) => {
      const pulse = Math.sin(time * 0.003) * 0.2 + 0.8;
      
      ctx.save();
      ctx.translate(x, y);
      ctx.scale(pulse, pulse);
      
      // Draw tag background
      ctx.fillStyle = 'rgba(16, 185, 129, 0.2)';
      ctx.strokeStyle = '#10b981';
      ctx.lineWidth = 2;
      
      ctx.beginPath();
      ctx.moveTo(-30, -15);
      ctx.lineTo(30, -15);
      ctx.lineTo(30, 15);
      ctx.lineTo(-30, 15);
      ctx.lineTo(-40, 0);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
      
      // Draw price text
      ctx.fillStyle = '#10b981';
      ctx.font = 'bold 14px "Orbitron", monospace';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(price, 0, 0);
      
      ctx.restore();
    };

    const animate = (time: number) => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw grid
      drawGrid();
      
      // Draw chart lines
      chartLines.forEach(line => {
        drawChart(line, time);
      });
      
      // Draw floating price tags
      const tagPositions = [
        { x: canvas.width * 0.2, y: canvas.height * 0.3, price: '$99' },
        { x: canvas.width * 0.5, y: canvas.height * 0.6, price: '$249' },
        { x: canvas.width * 0.8, y: canvas.height * 0.4, price: '$549' },
      ];
      
      tagPositions.forEach(pos => {
        drawPriceTag(
          pos.x, 
          pos.y + Math.sin(time * 0.002) * 10, 
          pos.price, 
          time
        );
      });
      
      // Update offset for scrolling effect
      offset += 0.5;
      
      // Update chart points periodically
      if (offset % 100 === 0) {
        chartLines.forEach(line => {
          // Add new point at the end
          line.points.push({
            x: line.points[line.points.length - 1].x + canvas.width / 10,
            y: canvas.height * 0.5 + (Math.random() - 0.5) * canvas.height * 0.3
          });
          
          // Remove old points that are off screen
          line.points = line.points.filter(point => point.x - offset > -100);
        });
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
      style={{ opacity: 0.3 }}
    />
  );
};

export default SalesGraphBackground;