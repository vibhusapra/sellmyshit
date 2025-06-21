import React, { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';
import AnimatedSalesBackground from './components/AnimatedSalesBackground';
import HeroSection from './components/HeroSection';
import ImageUploader from './components/ImageUploader';
import ProgressIndicator from './components/ProgressIndicator';
import ResultsDisplay from './components/ResultsDisplay';
import ImageVariations from './components/ImageVariations';
import EnhancementModeSelector from './components/EnhancementModeSelector';
import { processItem, AnalysisResponse } from './services/api';
import toast from 'react-hot-toast';

const progressSteps = [
  'Upload Images',
  'Analyzing Items',
  'Enhancing Images',
  'Generating Listing',
  'Complete'
];

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [results, setResults] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isRealMode, setIsRealMode] = useState(false);
  const [enhancementMode, setEnhancementMode] = useState<'smart' | 'quick' | 'custom'>('smart');

  const handleImagesSelected = async (files: File[]) => {
    setIsLoading(true);
    setError(null);
    setCurrentStep(1);
    setUploadedFile(files[0]);

    try {
      const stepDuration = 2000;
      
      // Step 2: Analyzing
      setTimeout(() => setCurrentStep(2), stepDuration);
      
      // Step 3: Enhancing
      setTimeout(() => setCurrentStep(3), stepDuration * 2);
      
      const response = await processItem(files[0], enhancementMode, undefined, isRealMode);
      
      // Step 4: Complete
      setCurrentStep(4);
      setResults(response);
      
      toast.success('Analysis complete! Your listing is ready.');
      setIsLoading(false);
    } catch (err) {
      console.error('Error uploading images:', err);
      setError('Failed to analyze images. Please try again.');
      toast.error('Something went wrong. Please try again.');
      setCurrentStep(0);
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResults(null);
    setCurrentStep(0);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-darker-bg relative overflow-hidden">
      {/* Animated sales background */}
      <AnimatedSalesBackground />
      
      {/* Main content */}
      <div className="relative z-10 container mx-auto px-4 py-12">
        <HeroSection />
        
        <AnimatePresence mode="wait">
          {!results ? (
            <motion.div
              key="uploader"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              {/* Real Mode Toggle */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex justify-center mb-8"
              >
                <div className="glass rounded-lg p-4 flex items-center space-x-4">
                  <span className={`font-semibold ${!isRealMode ? 'text-cyber-purple' : 'text-gray-400'}`}>
                    Fun Mode 🎮
                  </span>
                  <button
                    onClick={() => setIsRealMode(!isRealMode)}
                    className="relative inline-flex h-8 w-14 items-center rounded-full transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-cyber-purple focus:ring-offset-2 focus:ring-offset-gray-900"
                    style={{
                      backgroundColor: isRealMode ? '#8b5cf6' : '#4b5563'
                    }}
                  >
                    <motion.span
                      layout
                      className="inline-block h-6 w-6 transform rounded-full bg-white shadow-lg"
                      animate={{
                        x: isRealMode ? 26 : 2
                      }}
                      transition={{ type: "spring", stiffness: 500, damping: 30 }}
                    />
                  </button>
                  <span className={`font-semibold ${isRealMode ? 'text-cyber-purple' : 'text-gray-400'}`}>
                    Real Mode 💼
                  </span>
                </div>
              </motion.div>

              {/* Enhancement Mode Selector */}
              <EnhancementModeSelector
                selectedMode={enhancementMode}
                onModeChange={setEnhancementMode}
                disabled={isLoading}
              />

              {isLoading && (
                <ProgressIndicator steps={progressSteps} currentStep={currentStep} />
              )}
              
              <ImageUploader 
                onImagesSelected={handleImagesSelected} 
                isLoading={isLoading}
              />
              
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-6 p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-center max-w-md mx-auto"
                >
                  <p className="text-red-400">{error}</p>
                </motion.div>
              )}
            </motion.div>
          ) : (
            <motion.div
              key="results"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <ResultsDisplay results={results} onReset={handleReset} />
              
              {/* Image Variations Section */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="mt-12 max-w-6xl mx-auto"
              >
                <ImageVariations imageFile={uploadedFile} />
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      
      {/* Toast notifications */}
      <Toaster
        position="bottom-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#1a1a1a',
            color: '#fff',
            border: '1px solid rgba(147, 51, 234, 0.3)',
            boxShadow: '0 0 20px rgba(147, 51, 234, 0.2)',
          },
          success: {
            iconTheme: {
              primary: '#9333ea',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
    </div>
  );
}

export default App;