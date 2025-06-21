import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeftIcon, ChevronRightIcon, SparklesIcon, DocumentDuplicateIcon, CheckIcon } from '@heroicons/react/24/outline';
import { AnalysisResponse, getImageUrl } from '../services/api';
import toast from 'react-hot-toast';

interface ResultsDisplayProps {
  results: AnalysisResponse;
  onReset: () => void;
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results, onReset }) => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [copiedField, setCopiedField] = useState<string | null>(null);

  const copyToClipboard = async (text: string, field: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedField(field);
      toast.success('Copied to clipboard!');
      setTimeout(() => setCopiedField(null), 2000);
    } catch (err) {
      toast.error('Failed to copy');
    }
  };

  const nextImage = () => {
    setCurrentImageIndex((prev) => 
      prev === results.enhanced_images.length - 1 ? 0 : prev + 1
    );
  };

  const prevImage = () => {
    setCurrentImageIndex((prev) => 
      prev === 0 ? results.enhanced_images.length - 1 : prev - 1
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="w-full max-w-6xl mx-auto"
    >
      {/* Enhanced Images Carousel */}
      {results.enhanced_images.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <h2 className="text-3xl font-cyber font-bold mb-6 text-center">
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyber-purple to-cyber-pink">
              Enhanced Images
            </span>
          </h2>
          
          <div className="relative max-w-2xl mx-auto">
            <div className="relative overflow-hidden rounded-lg border-2 border-cyber-purple/30 neon-border">
              <AnimatePresence mode="wait">
                <motion.img
                  key={currentImageIndex}
                  src={getImageUrl(results.enhanced_images[currentImageIndex].url.replace('/image/', ''))}
                  alt={`Enhanced ${currentImageIndex + 1}`}
                  className="w-full h-[500px] object-contain bg-black"
                  initial={{ opacity: 0, x: 100 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -100 }}
                  transition={{ duration: 0.3 }}
                />
              </AnimatePresence>
              
              {/* Navigation buttons */}
              {results.enhanced_images.length > 1 && (
                <>
                  <button
                    onClick={prevImage}
                    className="absolute left-4 top-1/2 -translate-y-1/2 p-2 rounded-full bg-black/50 hover:bg-black/70 transition-all duration-300 hover:scale-110"
                  >
                    <ChevronLeftIcon className="w-6 h-6" />
                  </button>
                  <button
                    onClick={nextImage}
                    className="absolute right-4 top-1/2 -translate-y-1/2 p-2 rounded-full bg-black/50 hover:bg-black/70 transition-all duration-300 hover:scale-110"
                  >
                    <ChevronRightIcon className="w-6 h-6" />
                  </button>
                </>
              )}
              
              {/* Image indicators */}
              <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex space-x-2">
                {results.enhanced_images.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentImageIndex(index)}
                    className={`w-2 h-2 rounded-full transition-all duration-300 ${
                      index === currentImageIndex 
                        ? 'w-8 bg-cyber-purple' 
                        : 'bg-gray-600 hover:bg-gray-500'
                    }`}
                  />
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Results Grid */}
      <div className="grid md:grid-cols-2 gap-8 mb-8">
        {/* Item Analysis */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="glass rounded-lg p-6"
        >
          <h3 className="text-2xl font-cyber font-bold mb-4 flex items-center">
            <SparklesIcon className="w-6 h-6 mr-2 text-cyber-purple" />
            Item Analysis
          </h3>
          
          <div className="space-y-3">
            <div className="border-b border-gray-700 pb-2">
              <span className="text-gray-400 text-sm">Item Name</span>
              <p className="text-lg font-semibold">{results.item_analysis.item_name}</p>
            </div>
            
            <div className="grid grid-cols-2 gap-3">
              <div>
                <span className="text-gray-400 text-sm">Category</span>
                <p className="font-semibold">{results.item_analysis.category}</p>
              </div>
              <div>
                <span className="text-gray-400 text-sm">Condition</span>
                <p className="font-semibold">{results.item_analysis.condition}</p>
              </div>
            </div>
            
            {results.item_analysis.brand && (
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <span className="text-gray-400 text-sm">Brand</span>
                  <p className="font-semibold">{results.item_analysis.brand}</p>
                </div>
                {results.item_analysis.model && (
                  <div>
                    <span className="text-gray-400 text-sm">Model</span>
                    <p className="font-semibold">{results.item_analysis.model}</p>
                  </div>
                )}
              </div>
            )}
            
            <div>
              <span className="text-gray-400 text-sm">Key Features</span>
              <div className="flex flex-wrap gap-2 mt-1">
                {results.item_analysis.key_features.map((feature, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-cyber-purple/20 border border-cyber-purple/30 rounded-full text-sm"
                  >
                    {feature}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Pricing Info */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="glass rounded-lg p-6"
        >
          <h3 className="text-2xl font-cyber font-bold mb-4">Pricing Strategy</h3>
          
          <div className="text-center mb-6">
            <p className="text-gray-400 text-sm mb-2">Suggested Price</p>
            <p className="text-5xl font-cyber font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyber-purple to-cyber-pink">
              ${results.listing.suggested_price}
            </p>
          </div>
          
          <div className="p-4 bg-cyber-purple/10 border border-cyber-purple/30 rounded-lg">
            <p className="text-sm leading-relaxed">
              {results.price_data.ai_estimated ? 
                "🤖 AI-estimated price based on item analysis" : 
                "Based on market research of similar items"
              }
            </p>
          </div>
          
          <div className="mt-4">
            <span className="text-gray-400 text-sm">Best Platforms</span>
            <div className="flex flex-wrap gap-2 mt-1">
              {['eBay', 'Facebook', 'Craigslist'].map((platform, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-cyber-blue/20 border border-cyber-blue/30 rounded-full text-sm"
                >
                  {platform}
                </span>
              ))}
            </div>
          </div>
        </motion.div>
      </div>

      {/* Listing Details */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="glass rounded-lg p-6 mb-8"
      >
        <h3 className="text-2xl font-cyber font-bold mb-6">Generated Listing</h3>
        
        <div className="space-y-6">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-sm">Title</span>
              <button
                onClick={() => copyToClipboard(results.listing.title, 'title')}
                className="p-1 hover:bg-cyber-purple/20 rounded transition-colors duration-200"
              >
                {copiedField === 'title' ? (
                  <CheckIcon className="w-5 h-5 text-green-500" />
                ) : (
                  <DocumentDuplicateIcon className="w-5 h-5 text-gray-400" />
                )}
              </button>
            </div>
            <p className="text-xl font-semibold p-3 bg-black/30 rounded-lg border border-gray-700">
              {results.listing.title}
            </p>
          </div>
          
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-sm">Description</span>
              <button
                onClick={() => copyToClipboard(results.listing.description, 'description')}
                className="p-1 hover:bg-cyber-purple/20 rounded transition-colors duration-200"
              >
                {copiedField === 'description' ? (
                  <CheckIcon className="w-5 h-5 text-green-500" />
                ) : (
                  <DocumentDuplicateIcon className="w-5 h-5 text-gray-400" />
                )}
              </button>
            </div>
            <div className="p-4 bg-black/30 rounded-lg border border-gray-700 max-h-64 overflow-y-auto">
              <p className="whitespace-pre-wrap">{results.listing.description}</p>
            </div>
          </div>
          
          <div>
            <span className="text-gray-400 text-sm">Tags</span>
            <div className="flex flex-wrap gap-2 mt-2">
              {results.listing.keywords.map((tag, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-gradient-to-r from-cyber-purple/20 to-cyber-pink/20 border border-cyber-purple/30 rounded-full text-sm hover:from-cyber-purple/30 hover:to-cyber-pink/30 transition-all duration-200 cursor-pointer"
                  onClick={() => copyToClipboard(tag, `tag-${index}`)}
                >
                  #{tag}
                </span>
              ))}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Action Button */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="text-center"
      >
        <button
          onClick={onReset}
          className="cyber-button px-8 py-4 rounded-lg font-cyber font-semibold text-lg"
        >
          Analyze Another Item
        </button>
      </motion.div>
    </motion.div>
  );
};

export default ResultsDisplay;