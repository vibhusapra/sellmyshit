import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ParticleBackground from './ParticleBackground';
import MoneyRainBackground from './MoneyRainBackground';
import SalesGraphBackground from './SalesGraphBackground';

const AnimatedSalesBackground: React.FC = () => {
  const [activeBackground, setActiveBackground] = useState(0);
  const backgrounds = [
    { component: ParticleBackground, duration: 20000 },
    { component: MoneyRainBackground, duration: 15000 },
    { component: SalesGraphBackground, duration: 15000 },
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveBackground((prev) => (prev + 1) % backgrounds.length);
    }, backgrounds[activeBackground].duration);

    return () => clearInterval(interval);
  }, [activeBackground, backgrounds]);

  return (
    <>
      {/* Static gradient base */}
      <div className="fixed inset-0 bg-gradient-to-br from-darker-bg via-dark-bg to-darker-bg"></div>
      
      {/* Animated grid pattern */}
      <div className="fixed inset-0 grid-pattern opacity-20"></div>
      
      {/* Dynamic animated backgrounds */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeBackground}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 2 }}
          className="fixed inset-0"
        >
          {React.createElement(backgrounds[activeBackground].component)}
        </motion.div>
      </AnimatePresence>
      
      {/* Floating sales badges */}
      <div className="fixed inset-0 pointer-events-none">
        {[...Array(5)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute"
            initial={{ 
              x: Math.random() * window.innerWidth,
              y: window.innerHeight + 100,
              rotate: Math.random() * 360
            }}
            animate={{ 
              y: -100,
              rotate: Math.random() * 360 + 360,
            }}
            transition={{
              duration: 20 + Math.random() * 10,
              repeat: Infinity,
              delay: i * 4,
              ease: "linear"
            }}
          >
            <div className="bg-gradient-to-r from-neon-green to-cyber-cyan text-dark-bg font-bold px-4 py-2 rounded-full shadow-lg opacity-30">
              {['SALE', 'HOT DEAL', '-50%', 'LIMITED', 'TRENDING'][i]}
            </div>
          </motion.div>
        ))}
      </div>
      
      {/* Animated dollar signs corner decorations */}
      <div className="fixed top-10 left-10 text-6xl font-cyber text-neon-green opacity-10 animate-pulse-neon">
        $
      </div>
      <div className="fixed bottom-10 right-10 text-6xl font-cyber text-neon-green opacity-10 animate-pulse-neon" style={{ animationDelay: '0.5s' }}>
        $
      </div>
      
      {/* Subtle cash register sound effect visual (CSS only) */}
      <div className="fixed bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-neon-green to-transparent opacity-20 animate-pulse"></div>
    </>
  );
};

export default AnimatedSalesBackground;