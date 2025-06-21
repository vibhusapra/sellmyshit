import React from 'react';
import { motion } from 'framer-motion';

const HeroSection: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
      className="text-center mb-16 relative"
    >
      {/* Floating dollar signs around the title */}
      <motion.div
        className="absolute -top-8 left-1/4 text-4xl text-neon-green opacity-30 dollar-pulse"
        initial={{ opacity: 0, rotate: -20 }}
        animate={{ opacity: 0.3, rotate: 20 }}
        transition={{ duration: 2, repeat: Infinity, repeatType: "reverse" }}
      >
        $
      </motion.div>
      <motion.div
        className="absolute -top-8 right-1/4 text-4xl text-neon-green opacity-30 dollar-pulse"
        initial={{ opacity: 0, rotate: 20 }}
        animate={{ opacity: 0.3, rotate: -20 }}
        transition={{ duration: 2, repeat: Infinity, repeatType: "reverse", delay: 0.5 }}
      >
        $
      </motion.div>
      
      <motion.h1 
        className="text-6xl md:text-8xl font-cyber font-bold mb-6 relative"
        initial={{ opacity: 0, scale: 0.5 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyber-purple via-cyber-pink to-cyber-blue animate-gradient neon-text">
          SellMyShit
        </span>
        {/* Cash register cha-ching effect */}
        <motion.span
          className="absolute -right-16 top-0 text-2xl text-neon-green font-bold"
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: [0, 1, 1, 0], scale: [0, 1.2, 1, 0] }}
          transition={{ duration: 3, repeat: Infinity, repeatDelay: 5 }}
        >
          CHA-CHING!
        </motion.span>
      </motion.h1>
      
      <motion.p 
        className="text-xl md:text-2xl text-gray-300 mb-8 font-retro"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        Transform your items into <span className="text-neon-green font-bold">CASH</span> with AI magic
      </motion.p>
      
      {/* Sales badges */}
      <motion.div
        className="flex justify-center space-x-4 mb-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
      >
        <div className="bg-gradient-to-r from-neon-green to-cyber-cyan text-dark-bg px-4 py-2 rounded-full font-bold sales-badge">
          Instant Valuation
        </div>
        <div className="bg-gradient-to-r from-cyber-purple to-cyber-pink text-white px-4 py-2 rounded-full font-bold sales-badge">
          Pro Photos
        </div>
        <div className="bg-gradient-to-r from-cyber-blue to-cyber-cyan text-white px-4 py-2 rounded-full font-bold sales-badge">
          Smart Pricing
        </div>
      </motion.div>
      
      <motion.div 
        className="flex justify-center space-x-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.6 }}
      >
        <div className="h-1 w-20 bg-gradient-to-r from-transparent via-neon-green to-transparent animate-pulse"></div>
        <div className="h-1 w-20 bg-gradient-to-r from-transparent via-cyber-purple to-transparent animate-pulse-neon"></div>
        <div className="h-1 w-20 bg-gradient-to-r from-transparent via-cyber-pink to-transparent animate-pulse-neon" style={{ animationDelay: '0.5s' }}></div>
        <div className="h-1 w-20 bg-gradient-to-r from-transparent via-cyber-blue to-transparent animate-pulse-neon" style={{ animationDelay: '1s' }}></div>
        <div className="h-1 w-20 bg-gradient-to-r from-transparent via-neon-green to-transparent animate-pulse" style={{ animationDelay: '1.5s' }}></div>
      </motion.div>
    </motion.div>
  );
};

export default HeroSection;