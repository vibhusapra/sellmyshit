import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { CloudArrowUpIcon, XMarkIcon } from '@heroicons/react/24/outline';

interface ImageUploaderProps {
  onImagesSelected: (files: File[]) => void;
  isLoading: boolean;
}

const ImageUploader: React.FC<ImageUploaderProps> = ({ onImagesSelected, isLoading }) => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = [...selectedFiles, ...acceptedFiles].slice(0, 5); // Max 5 files
    setSelectedFiles(newFiles);
    
    // Create previews
    const newPreviews = newFiles.map(file => URL.createObjectURL(file));
    setPreviews(prev => {
      // Clean up old previews
      prev.forEach(url => URL.revokeObjectURL(url));
      return newPreviews;
    });
  }, [selectedFiles]);

  const removeFile = (index: number) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index);
    const newPreviews = previews.filter((_, i) => i !== index);
    
    // Clean up removed preview
    URL.revokeObjectURL(previews[index]);
    
    setSelectedFiles(newFiles);
    setPreviews(newPreviews);
  };

  const handleUpload = () => {
    if (selectedFiles.length > 0) {
      onImagesSelected(selectedFiles);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.webp']
    },
    maxFiles: 5,
    disabled: isLoading
  });

  return (
    <div className="w-full max-w-4xl mx-auto">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className={`relative ${selectedFiles.length > 0 ? 'mb-6' : ''}`}
      >
        <div
          {...getRootProps()}
          className={`
            relative p-12 border-2 border-dashed rounded-lg cursor-pointer
            transition-all duration-300 overflow-hidden
            ${isDragActive 
              ? 'border-cyber-purple bg-cyber-purple/10 shadow-lg shadow-cyber-purple/50' 
              : 'border-gray-600 hover:border-cyber-purple hover:bg-cyber-purple/5'
            }
            ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <input {...getInputProps()} />
          
          {/* Animated background gradient */}
          <div className="absolute inset-0 opacity-10">
            <div className="absolute inset-0 bg-gradient-to-br from-cyber-purple via-transparent to-cyber-pink animate-gradient"></div>
          </div>
          
          <div className="relative z-10 text-center">
            <motion.div
              animate={{ 
                y: isDragActive ? -10 : 0,
                scale: isDragActive ? 1.1 : 1
              }}
              transition={{ duration: 0.2 }}
            >
              <CloudArrowUpIcon className="w-16 h-16 mx-auto mb-4 text-cyber-purple" />
            </motion.div>
            
            <p className="text-xl font-retro mb-2">
              {isDragActive ? 'Drop your images here' : 'Drag & drop images here'}
            </p>
            <p className="text-gray-400">or click to select files</p>
            <p className="text-sm text-gray-500 mt-2">Maximum 5 images (JPEG, PNG, GIF, WebP)</p>
          </div>
        </div>
      </motion.div>

      {/* Image previews */}
      <AnimatePresence>
        {selectedFiles.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6"
          >
            {previews.map((preview, index) => (
              <motion.div
                key={preview}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ delay: index * 0.1 }}
                className="relative group"
              >
                <div className="relative overflow-hidden rounded-lg border-2 border-cyber-purple/30 hover:border-cyber-purple transition-all duration-300">
                  <img
                    src={preview}
                    alt={`Preview ${index + 1}`}
                    className="w-full h-32 object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  <button
                    onClick={() => removeFile(index)}
                    className="absolute top-2 right-2 p-1 bg-red-500 rounded-full opacity-0 group-hover:opacity-100 transition-all duration-300 hover:bg-red-600 hover:scale-110"
                    disabled={isLoading}
                  >
                    <XMarkIcon className="w-4 h-4 text-white" />
                  </button>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Upload button */}
      <AnimatePresence>
        {selectedFiles.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="text-center"
          >
            <button
              onClick={handleUpload}
              disabled={isLoading}
              className="cyber-button px-8 py-4 rounded-lg font-cyber font-semibold text-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center space-x-3">
                  <div className="cyber-loader w-6 h-6"></div>
                  <span>Analyzing your items...</span>
                </div>
              ) : (
                `Analyze ${selectedFiles.length} Image${selectedFiles.length > 1 ? 's' : ''}`
              )}
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ImageUploader;