import React from 'react';
import { motion } from 'framer-motion';
import { SparklesIcon, BoltIcon, WrenchScrewdriverIcon } from '@heroicons/react/24/outline';

export type EnhancementMode = 'smart' | 'quick' | 'custom';

interface EnhancementModeSelectorProps {
  selectedMode: EnhancementMode;
  onModeChange: (mode: EnhancementMode) => void;
  disabled?: boolean;
}

const modes = [
  {
    id: 'smart' as EnhancementMode,
    name: 'Smart Mode',
    description: 'AI generates multiple professional product images',
    icon: SparklesIcon,
    color: 'from-cyber-purple to-cyber-pink',
    features: ['Multiple angles', 'Professional lighting', 'Lifestyle shots']
  },
  {
    id: 'quick' as EnhancementMode,
    name: 'Quick Mode',
    description: 'Fast background removal for immediate listing',
    icon: BoltIcon,
    color: 'from-cyber-blue to-cyber-purple',
    features: ['Instant results', 'Clean background', 'Ready to list']
  },
  {
    id: 'custom' as EnhancementMode,
    name: 'Custom Mode',
    description: 'Create your own custom image variations',
    icon: WrenchScrewdriverIcon,
    color: 'from-cyber-pink to-purple-600',
    features: ['Full control', 'Custom prompts', 'Unique styles']
  }
];

const EnhancementModeSelector: React.FC<EnhancementModeSelectorProps> = ({
  selectedMode,
  onModeChange,
  disabled = false
}) => {
  return (
    <div className="w-full max-w-4xl mx-auto mb-8">
      <h3 className="text-xl font-cyber font-semibold mb-4 text-center">
        Choose Enhancement Mode
      </h3>
      <div className="grid md:grid-cols-3 gap-4">
        {modes.map((mode) => {
          const Icon = mode.icon;
          const isSelected = selectedMode === mode.id;
          
          return (
            <motion.button
              key={mode.id}
              onClick={() => !disabled && onModeChange(mode.id)}
              disabled={disabled}
              whileHover={!disabled ? { scale: 1.02 } : {}}
              whileTap={!disabled ? { scale: 0.98 } : {}}
              className={`
                relative p-6 rounded-lg border-2 transition-all duration-300
                ${isSelected 
                  ? 'border-cyber-purple bg-cyber-purple/10 shadow-lg shadow-cyber-purple/30' 
                  : 'border-gray-700 hover:border-gray-600 bg-black/30'
                }
                ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              `}
            >
              {/* Background gradient for selected state */}
              {isSelected && (
                <div className="absolute inset-0 rounded-lg overflow-hidden">
                  <div className={`absolute inset-0 bg-gradient-to-br ${mode.color} opacity-10 animate-pulse`}></div>
                </div>
              )}
              
              <div className="relative z-10">
                <div className={`
                  w-12 h-12 mx-auto mb-3 rounded-full flex items-center justify-center
                  bg-gradient-to-br ${mode.color}
                `}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                
                <h4 className="font-cyber font-semibold text-lg mb-2">
                  {mode.name}
                </h4>
                
                <p className="text-sm text-gray-400 mb-3">
                  {mode.description}
                </p>
                
                <div className="flex flex-wrap gap-2 justify-center">
                  {mode.features.map((feature, index) => (
                    <span
                      key={index}
                      className={`
                        text-xs px-2 py-1 rounded-full
                        ${isSelected 
                          ? 'bg-cyber-purple/20 text-cyber-purple border border-cyber-purple/30' 
                          : 'bg-gray-800 text-gray-400 border border-gray-700'
                        }
                      `}
                    >
                      {feature}
                    </span>
                  ))}
                </div>
              </div>
              
              {/* Selection indicator */}
              {isSelected && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="absolute top-3 right-3"
                >
                  <div className="w-6 h-6 rounded-full bg-gradient-to-br from-cyber-purple to-cyber-pink flex items-center justify-center">
                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                </motion.div>
              )}
            </motion.button>
          );
        })}
      </div>
    </div>
  );
};

export default EnhancementModeSelector;