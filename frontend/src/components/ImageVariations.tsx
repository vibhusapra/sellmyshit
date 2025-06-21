import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { SparklesIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import { generateVariations, ImageVariation } from '../services/api';
import toast from 'react-hot-toast';

interface ImageVariationsProps {
  imageFile: File | null;
}

const ImageVariations: React.FC<ImageVariationsProps> = ({ imageFile }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [variations, setVariations] = useState<ImageVariation[]>([]);
  const [showVariations, setShowVariations] = useState(false);

  const handleGenerateVariations = async () => {
    if (!imageFile) {
      toast.error('Please upload an image first');
      return;
    }

    setIsGenerating(true);
    setShowVariations(true);

    try {
      const response = await generateVariations(imageFile);
      setVariations(response.variations);
      
      if (response.total_generated < response.total_requested) {
        toast(`Generated ${response.total_generated} out of ${response.total_requested} variations`, {
          icon: '⚠️',
          style: {
            background: '#713200',
            color: '#fff',
          },
        });
      } else {
        toast.success('All variations generated successfully!');
      }
    } catch (error) {
      console.error('Error generating variations:', error);
      toast.error('Failed to generate variations');
      setShowVariations(false);
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadImage = async (variation: ImageVariation) => {
    try {
      const response = await fetch(`http://localhost:8000${variation.url}`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${variation.type}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      toast.success('Image downloaded!');
    } catch (error) {
      toast.error('Failed to download image');
    }
  };

  return (
    <div className="w-full">
      {/* Generate Variations Button */}
      {!showVariations && (
        <motion.button
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          onClick={handleGenerateVariations}
          disabled={!imageFile || isGenerating}
          className="w-full py-4 bg-gradient-to-r from-cyber-purple to-cyber-pink rounded-lg font-cyber font-bold text-lg hover:from-cyber-purple/80 hover:to-cyber-pink/80 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          <SparklesIcon className="w-6 h-6" />
          Generate 5 Variations with FLUX.1 Kontext
        </motion.button>
      )}

      {/* Variations Display */}
      <AnimatePresence>
        {showVariations && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Header */}
            <div className="text-center">
              <h3 className="text-2xl font-cyber font-bold mb-2">
                <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyber-purple to-cyber-pink">
                  Image Variations
                </span>
              </h3>
              <p className="text-gray-400">Generated using FLUX.1 Kontext</p>
            </div>

            {/* Loading State */}
            {isGenerating && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[...Array(5)].map((_, index) => (
                  <div
                    key={index}
                    className="aspect-square bg-gray-800 rounded-lg animate-pulse"
                  />
                ))}
              </div>
            )}

            {/* Variations Grid */}
            {!isGenerating && variations.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {variations.map((variation, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.1 }}
                    className="relative group"
                  >
                    <div className="aspect-square rounded-lg overflow-hidden border-2 border-cyber-purple/30 neon-border">
                      {variation.error ? (
                        <div className="w-full h-full flex items-center justify-center bg-red-900/20">
                          <p className="text-red-400 text-sm text-center p-4">
                            Error: {variation.error}
                          </p>
                        </div>
                      ) : (
                        <>
                          <img
                            src={`http://localhost:8000${variation.url}`}
                            alt={variation.type}
                            className="w-full h-full object-cover"
                          />
                          <div className="absolute inset-0 bg-black/80 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col items-center justify-center p-4">
                            <p className="text-xs text-gray-300 text-center mb-3">
                              {variation.prompt}
                            </p>
                            <button
                              onClick={() => downloadImage(variation)}
                              className="flex items-center gap-2 px-4 py-2 bg-cyber-purple rounded-lg hover:bg-cyber-purple/80 transition-colors duration-200"
                            >
                              <ArrowDownTrayIcon className="w-4 h-4" />
                              Download
                            </button>
                          </div>
                        </>
                      )}
                    </div>
                    <p className="mt-2 text-sm text-gray-400 capitalize">
                      {variation.type.replace(/_/g, ' ')}
                    </p>
                  </motion.div>
                ))}
              </div>
            )}

            {/* Generate More Button */}
            {!isGenerating && variations.length > 0 && (
              <motion.button
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                onClick={handleGenerateVariations}
                className="w-full py-3 bg-gray-800 rounded-lg font-cyber hover:bg-gray-700 transition-colors duration-200"
              >
                Generate New Variations
              </motion.button>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ImageVariations;