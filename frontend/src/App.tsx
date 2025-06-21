import React, { useState, useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';
import ParticleBackground from './components/ParticleBackground';
import HeroSection from './components/HeroSection';
import ImageUploader from './components/ImageUploader';
import ProgressIndicator from './components/ProgressIndicator';
import ResultsDisplay from './components/ResultsDisplay';
import ImageVariations from './components/ImageVariations';
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

  const handleImagesSelected = async (files: File[]) => {
    setIsLoading(true);
    setError(null);
    setCurrentStep(1);
    setUploadedFile(files[0]);

    try {
      // Simulate progress through steps
      const stepDuration = 2000; // 2 seconds per step
      
      // Step 2: Analyzing
      setTimeout(() => setCurrentStep(2), stepDuration);
      
      // Step 3: Enhancing
      setTimeout(() => setCurrentStep(3), stepDuration * 2);
      
      // Make the actual API call
      const response = await processItem(files[0], 'quick');
      
      // Step 4: Complete
      setCurrentStep(4);
      setResults(response);
      
      toast.success('Analysis complete! Your listing is ready.');
    } catch (err) {
      console.error('Error uploading images:', err);
      setError('Failed to analyze images. Please try again.');
      toast.error('Something went wrong. Please try again.');
      setCurrentStep(0);
    } finally {
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
      {/* Background effects */}
      <div className="fixed inset-0 bg-gradient-to-br from-darker-bg via-dark-bg to-darker-bg"></div>
      <div className="fixed inset-0 grid-pattern opacity-20"></div>
      <ParticleBackground />
      
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