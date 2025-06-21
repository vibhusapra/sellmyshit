import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface ProgressIndicatorProps {
  steps: string[];
  currentStep: number;
  statusMessage?: string;
}

const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({ steps, currentStep, statusMessage }) => {
  const [elapsedTime, setElapsedTime] = useState(0);
  
  useEffect(() => {
    const startTime = Date.now();
    const timer = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);
    
    return () => clearInterval(timer);
  }, []);
  
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-4xl mx-auto mb-12"
    >
      {/* Timer and Status */}
      <div className="text-center mb-6">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="inline-flex items-center gap-4 px-6 py-3 bg-black/50 border border-gray-700 rounded-full"
        >
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-cyber-purple rounded-full animate-pulse"></div>
            <span className="text-sm font-cyber text-cyber-purple">
              {formatTime(elapsedTime)}
            </span>
          </div>
          {statusMessage && (
            <>
              <div className="w-px h-4 bg-gray-700"></div>
              <span className="text-sm text-gray-300">{statusMessage}</span>
            </>
          )}
        </motion.div>
      </div>
      <div className="relative">
        {/* Progress bar background */}
        <div className="absolute top-5 left-0 right-0 h-1 bg-gray-700 rounded-full"></div>
        
        {/* Animated progress bar */}
        <motion.div
          className="absolute top-5 left-0 h-1 bg-gradient-to-r from-cyber-purple to-cyber-pink rounded-full"
          initial={{ width: '0%' }}
          animate={{ width: `${(currentStep / (steps.length - 1)) * 100}%` }}
          transition={{ duration: 0.5, ease: 'easeInOut' }}
        >
          {/* Glowing effect at the end */}
          <div className="absolute right-0 top-1/2 -translate-y-1/2 w-4 h-4 bg-cyber-pink rounded-full animate-pulse shadow-lg shadow-cyber-pink/50"></div>
        </motion.div>
        
        {/* Steps */}
        <div className="relative flex justify-between">
          {steps.map((step, index) => (
            <motion.div
              key={step}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="flex flex-col items-center"
            >
              {/* Step circle */}
              <motion.div
                className={`
                  w-10 h-10 rounded-full flex items-center justify-center
                  transition-all duration-300 relative
                  ${index <= currentStep 
                    ? 'bg-gradient-to-br from-cyber-purple to-cyber-pink shadow-lg shadow-cyber-purple/50' 
                    : 'bg-gray-700 border-2 border-gray-600'
                  }
                `}
                animate={index === currentStep ? {
                  boxShadow: [
                    '0 0 20px rgba(147, 51, 234, 0.5)',
                    '0 0 40px rgba(147, 51, 234, 0.8)',
                    '0 0 20px rgba(147, 51, 234, 0.5)',
                  ]
                } : {}}
                transition={{ duration: 1.5, repeat: Infinity }}
              >
                <span className="text-sm font-bold">
                  {index <= currentStep ? '✓' : index + 1}
                </span>
                
                {/* Active step pulse effect */}
                {index === currentStep && (
                  <motion.div
                    className="absolute inset-0 rounded-full bg-cyber-purple"
                    initial={{ scale: 1, opacity: 0.5 }}
                    animate={{ scale: 1.5, opacity: 0 }}
                    transition={{ duration: 1, repeat: Infinity }}
                  />
                )}
              </motion.div>
              
              {/* Step label */}
              <motion.span
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 + 0.2 }}
                className={`
                  mt-2 text-xs font-retro text-center max-w-[100px]
                  ${index <= currentStep ? 'text-cyber-purple' : 'text-gray-500'}
                `}
              >
                {step}
              </motion.span>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  );
};

export default ProgressIndicator;