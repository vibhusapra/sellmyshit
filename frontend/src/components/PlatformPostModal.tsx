import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { XMarkIcon, DocumentDuplicateIcon, CheckIcon, ArrowTopRightOnSquareIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface PlatformPostModalProps {
  isOpen: boolean;
  onClose: () => void;
  platform: 'craigslist' | 'ebay' | 'facebook';
  title: string;
  description: string;
  price: number;
  imageUrls?: string[];
}

const PlatformPostModal: React.FC<PlatformPostModalProps> = ({
  isOpen,
  onClose,
  platform,
  title,
  description,
  price,
  imageUrls = []
}) => {
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [selectedCity, setSelectedCity] = useState(localStorage.getItem('craigslistCity') || 'sfbay');

  interface City {
    value: string;
    label: string;
  }

  interface PlatformConfig {
    name: string;
    color: string;
    borderColor: string;
    bgColor: string;
    textColor: string;
    cities?: City[];
  }

  const platformConfig: Record<'craigslist' | 'ebay' | 'facebook', PlatformConfig> = {
    craigslist: {
      name: 'Craigslist',
      color: 'from-purple-600 to-purple-800',
      borderColor: 'border-purple-500',
      bgColor: 'bg-purple-500/20',
      textColor: 'text-purple-400',
      cities: [
        { value: 'sfbay', label: 'SF Bay Area' },
        { value: 'losangeles', label: 'Los Angeles' },
        { value: 'newyork', label: 'New York' },
        { value: 'chicago', label: 'Chicago' },
        { value: 'seattle', label: 'Seattle' },
        { value: 'austin', label: 'Austin' },
        { value: 'denver', label: 'Denver' },
        { value: 'portland', label: 'Portland' },
        { value: 'sandiego', label: 'San Diego' },
        { value: 'boston', label: 'Boston' }
      ]
    },
    ebay: {
      name: 'eBay',
      color: 'from-blue-600 to-yellow-600',
      borderColor: 'border-blue-500',
      bgColor: 'bg-blue-500/20',
      textColor: 'text-blue-400'
    },
    facebook: {
      name: 'Facebook Marketplace',
      color: 'from-blue-600 to-blue-800',
      borderColor: 'border-blue-500',
      bgColor: 'bg-blue-500/20',
      textColor: 'text-blue-400'
    }
  };

  const config = platformConfig[platform];

  const copyToClipboard = async (text: string, field: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedField(field);
      toast.success(`${field} copied to clipboard!`);
      setTimeout(() => setCopiedField(null), 2000);
    } catch (err) {
      toast.error('Failed to copy');
    }
  };

  const copyAll = async () => {
    const fullText = `${title}\n\n${description}`;
    await copyToClipboard(fullText, 'All content');
  };

  const openPlatform = () => {
    let url = '';
    
    if (platform === 'craigslist') {
      // Save selected city
      localStorage.setItem('craigslistCity', selectedCity);
      // Open Craigslist posting page for the selected city
      url = `https://${selectedCity}.craigslist.org/d/for-sale/search/sss#post`;
    } else if (platform === 'ebay') {
      url = 'https://www.ebay.com/sl/sell';
    } else if (platform === 'facebook') {
      url = 'https://www.facebook.com/marketplace/create/item';
    }
    
    if (url) {
      window.open(url, '_blank');
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className={`w-full max-w-4xl max-h-[90vh] overflow-hidden rounded-lg border-2 ${config.borderColor} bg-gray-900 shadow-2xl`}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className={`bg-gradient-to-r ${config.color} p-6 relative`}>
              <button
                onClick={onClose}
                className="absolute top-4 right-4 p-2 rounded-full bg-black/20 hover:bg-black/40 transition-colors duration-200"
              >
                <XMarkIcon className="w-6 h-6" />
              </button>
              
              <h2 className="text-2xl font-cyber font-bold">
                Post to {config.name}
              </h2>
              <p className="text-sm opacity-90 mt-1">
                Copy the content below or open {config.name} directly
              </p>
            </div>

            {/* Content */}
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
              {/* City selector for Craigslist */}
              {platform === 'craigslist' && (
                <div className="mb-6">
                  <label className="block text-sm font-medium mb-2 text-gray-400">
                    Select your city:
                  </label>
                  <select
                    value={selectedCity}
                    onChange={(e) => setSelectedCity(e.target.value)}
                    className="w-full p-3 rounded-lg bg-black/50 border border-gray-700 focus:border-purple-500 focus:outline-none transition-colors duration-200"
                  >
                    {config.cities?.map((city) => (
                      <option key={city.value} value={city.value}>
                        {city.label}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Title Section */}
              <div className="mb-6">
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium text-gray-400">Title</label>
                  <button
                    onClick={() => copyToClipboard(title, 'Title')}
                    className={`p-2 rounded hover:${config.bgColor} transition-colors duration-200`}
                  >
                    {copiedField === 'Title' ? (
                      <CheckIcon className="w-5 h-5 text-green-500" />
                    ) : (
                      <DocumentDuplicateIcon className={`w-5 h-5 ${config.textColor}`} />
                    )}
                  </button>
                </div>
                <div className={`p-4 rounded-lg bg-black/30 border ${config.borderColor}/30`}>
                  <p className="font-semibold">{title}</p>
                </div>
              </div>

              {/* Price Section */}
              <div className="mb-6">
                <label className="text-sm font-medium text-gray-400">Price</label>
                <div className={`p-4 rounded-lg bg-black/30 border ${config.borderColor}/30`}>
                  <p className="text-2xl font-bold font-cyber bg-clip-text text-transparent bg-gradient-to-r ${config.color}">
                    ${price}
                  </p>
                </div>
              </div>

              {/* Description Section */}
              <div className="mb-6">
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium text-gray-400">Description</label>
                  <button
                    onClick={() => copyToClipboard(description, 'Description')}
                    className={`p-2 rounded hover:${config.bgColor} transition-colors duration-200`}
                  >
                    {copiedField === 'Description' ? (
                      <CheckIcon className="w-5 h-5 text-green-500" />
                    ) : (
                      <DocumentDuplicateIcon className={`w-5 h-5 ${config.textColor}`} />
                    )}
                  </button>
                </div>
                <div className={`p-4 rounded-lg bg-black/30 border ${config.borderColor}/30 max-h-64 overflow-y-auto`}>
                  <p className="whitespace-pre-wrap">{description}</p>
                </div>
              </div>

              {/* Images Reference */}
              {imageUrls.length > 0 && (
                <div className="mb-6">
                  <label className="text-sm font-medium text-gray-400 block mb-2">
                    Your Enhanced Images (save these to upload to {config.name})
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {imageUrls.slice(0, 6).map((url, index) => (
                      <a
                        key={index}
                        href={url}
                        download
                        className={`relative overflow-hidden rounded-lg border ${config.borderColor}/30 hover:${config.borderColor} transition-all duration-200 hover:scale-105`}
                      >
                        <img
                          src={url}
                          alt={`Enhanced ${index + 1}`}
                          className="w-full h-24 object-cover"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-200 flex items-end justify-center pb-2">
                          <span className="text-xs">Click to download</span>
                        </div>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Footer Actions */}
            <div className={`border-t ${config.borderColor}/30 p-6 bg-gray-900/50`}>
              <div className="flex justify-between items-center">
                <button
                  onClick={copyAll}
                  className={`px-6 py-3 rounded-lg ${config.bgColor} hover:opacity-80 transition-opacity duration-200 font-semibold`}
                >
                  {copiedField === 'All content' ? (
                    <>
                      <CheckIcon className="w-5 h-5 inline mr-2" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <DocumentDuplicateIcon className="w-5 h-5 inline mr-2" />
                      Copy All
                    </>
                  )}
                </button>
                
                <button
                  onClick={openPlatform}
                  className={`px-6 py-3 rounded-lg bg-gradient-to-r ${config.color} hover:opacity-90 transition-opacity duration-200 font-semibold flex items-center`}
                >
                  Open {config.name}
                  <ArrowTopRightOnSquareIcon className="w-5 h-5 ml-2" />
                </button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default PlatformPostModal;