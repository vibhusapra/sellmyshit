import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { PlusIcon, XMarkIcon, SparklesIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface CustomPromptInputProps {
  prompts: string[];
  onPromptsChange: (prompts: string[]) => void;
  disabled?: boolean;
}

const PROMPT_SUGGESTIONS = [
  'Professional studio lighting with soft shadows',
  'Lifestyle shot in modern home setting',
  'Close-up detail shot showing texture',
  'Minimalist white background',
  'Outdoor natural lighting',
  'Vintage aesthetic with warm tones',
  'Dark moody background with dramatic lighting',
  'Flat lay arrangement from above'
];

const CustomPromptInput: React.FC<CustomPromptInputProps> = ({
  prompts,
  onPromptsChange,
  disabled = false
}) => {
  const [currentPrompt, setCurrentPrompt] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);

  const addPrompt = () => {
    if (currentPrompt.trim() && prompts.length < 5) {
      onPromptsChange([...prompts, currentPrompt.trim()]);
      setCurrentPrompt('');
      toast.success('Prompt added!');
    } else if (prompts.length >= 5) {
      toast.error('Maximum 5 prompts allowed');
    }
  };

  const removePrompt = (index: number) => {
    onPromptsChange(prompts.filter((_, i) => i !== index));
  };

  const addSuggestion = (suggestion: string) => {
    if (prompts.length < 5) {
      onPromptsChange([...prompts, suggestion]);
      toast.success('Suggestion added!');
    } else {
      toast.error('Maximum 5 prompts allowed');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      addPrompt();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-4xl mx-auto mb-6"
    >
      <div className="glass rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-cyber font-semibold flex items-center">
            <SparklesIcon className="w-5 h-5 mr-2 text-cyber-purple" />
            Custom Image Prompts
          </h3>
          <button
            onClick={() => setShowSuggestions(!showSuggestions)}
            disabled={disabled}
            className="text-sm text-cyber-purple hover:text-cyber-pink transition-colors duration-200 disabled:opacity-50"
          >
            {showSuggestions ? 'Hide' : 'Show'} Suggestions
          </button>
        </div>

        {/* Suggestions */}
        <AnimatePresence>
          {showSuggestions && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-4 overflow-hidden"
            >
              <p className="text-xs text-gray-400 mb-2">Click to add a suggestion:</p>
              <div className="flex flex-wrap gap-2">
                {PROMPT_SUGGESTIONS.map((suggestion, index) => (
                  <motion.button
                    key={index}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => addSuggestion(suggestion)}
                    disabled={disabled || prompts.includes(suggestion)}
                    className={`
                      text-xs px-3 py-1 rounded-full transition-all duration-200
                      ${prompts.includes(suggestion)
                        ? 'bg-gray-800 text-gray-600 cursor-not-allowed'
                        : 'bg-cyber-purple/20 text-cyber-purple border border-cyber-purple/30 hover:bg-cyber-purple/30'
                      }
                      ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
                    `}
                  >
                    {suggestion}
                  </motion.button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Input field */}
        <div className="relative mb-4">
          <input
            type="text"
            value={currentPrompt}
            onChange={(e) => setCurrentPrompt(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={disabled || prompts.length >= 5}
            placeholder={prompts.length >= 5 ? "Maximum prompts reached" : "Describe your custom image style..."}
            className={`
              w-full px-4 py-3 pr-12 bg-black/50 border rounded-lg
              focus:outline-none focus:border-cyber-purple transition-colors duration-200
              ${disabled || prompts.length >= 5 
                ? 'border-gray-700 opacity-50 cursor-not-allowed' 
                : 'border-gray-600 hover:border-gray-500'
              }
            `}
          />
          <button
            onClick={addPrompt}
            disabled={disabled || !currentPrompt.trim() || prompts.length >= 5}
            className={`
              absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg
              transition-all duration-200
              ${disabled || !currentPrompt.trim() || prompts.length >= 5
                ? 'bg-gray-800 text-gray-600 cursor-not-allowed'
                : 'bg-cyber-purple hover:bg-cyber-purple/80 text-white hover:scale-110'
              }
            `}
          >
            <PlusIcon className="w-4 h-4" />
          </button>
        </div>

        {/* Prompt count */}
        <div className="text-sm text-gray-400 mb-3">
          {prompts.length}/5 prompts added
        </div>

        {/* Added prompts */}
        <AnimatePresence>
          {prompts.length > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-2"
            >
              {prompts.map((prompt, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ delay: index * 0.05 }}
                  className="flex items-center gap-3 p-3 bg-cyber-purple/10 border border-cyber-purple/30 rounded-lg"
                >
                  <span className="text-xs font-cyber text-cyber-purple">
                    #{index + 1}
                  </span>
                  <span className="flex-1 text-sm">{prompt}</span>
                  <button
                    onClick={() => removePrompt(index)}
                    disabled={disabled}
                    className="p-1 rounded hover:bg-red-500/20 transition-colors duration-200 disabled:opacity-50"
                  >
                    <XMarkIcon className="w-4 h-4 text-red-400" />
                  </button>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {prompts.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <SparklesIcon className="w-12 h-12 mx-auto mb-2 opacity-20" />
            <p className="text-sm">Add custom prompts to generate unique image variations</p>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default CustomPromptInput;