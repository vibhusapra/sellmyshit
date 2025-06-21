import React from 'react';
import { motion } from 'framer-motion';

const HeroSection: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
      className="text-center mb-16"
    >
      <motion.h1 
        className="text-6xl md:text-8xl font-cyber font-bold mb-6 relative"
        initial={{ opacity: 0, scale: 0.5 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyber-purple via-cyber-pink to-cyber-blue animate-gradient neon-text">
          SellMyShit
        </span>
      </motion.h1>
      
      <motion.p 
        className="text-xl md:text-2xl text-gray-300 mb-8 font-retro"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        Transform your items into irresistible listings with AI magic
      </motion.p>
      
      <motion.div 
        className="flex justify-center space-x-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.6 }}
      >
        <div className="h-1 w-20 bg-gradient-to-r from-transparent via-cyber-purple to-transparent animate-pulse-neon"></div>
        <div className="h-1 w-20 bg-gradient-to-r from-transparent via-cyber-pink to-transparent animate-pulse-neon" style={{ animationDelay: '0.5s' }}></div>
        <div className="h-1 w-20 bg-gradient-to-r from-transparent via-cyber-blue to-transparent animate-pulse-neon" style={{ animationDelay: '1s' }}></div>
      </motion.div>
    </motion.div>
  );
};

export default HeroSection;