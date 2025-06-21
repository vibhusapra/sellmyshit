import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ClockIcon, ChevronLeftIcon, ChevronRightIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { getListings, ListingSummary, getImageUrl } from '../services/api';
import toast from 'react-hot-toast';

interface RecentListingsProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectListing?: (listing: ListingSummary) => void;
}

const RecentListings: React.FC<RecentListingsProps> = ({ isOpen, onClose, onSelectListing }) => {
  const [listings, setListings] = useState<ListingSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(0);
  const [totalListings, setTotalListings] = useState(0);
  const itemsPerPage = 5;

  useEffect(() => {
    if (isOpen) {
      fetchListings();
    }
  }, [isOpen, currentPage]);

  const fetchListings = async () => {
    setLoading(true);
    try {
      const response = await getListings(currentPage * itemsPerPage, itemsPerPage);
      setListings(response.listings);
      setTotalListings(response.total);
    } catch (error) {
      console.error('Error fetching listings:', error);
      toast.error('Failed to load recent listings');
    } finally {
      setLoading(false);
    }
  };

  const totalPages = Math.ceil(totalListings / itemsPerPage);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
          />

          {/* Sidebar */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="fixed right-0 top-0 h-full w-96 bg-darker-bg border-l border-gray-800 shadow-2xl z-50 overflow-hidden"
          >
            {/* Header */}
            <div className="p-6 border-b border-gray-800">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-cyber font-bold flex items-center">
                  <ClockIcon className="w-6 h-6 mr-2 text-cyber-purple" />
                  Recent Listings
                </h2>
                <button
                  onClick={onClose}
                  className="p-2 rounded-lg hover:bg-gray-800 transition-colors duration-200"
                >
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-6 h-[calc(100%-200px)] overflow-y-auto">
              {loading ? (
                <div className="flex items-center justify-center h-full">
                  <div className="cyber-loader w-8 h-8"></div>
                </div>
              ) : listings.length === 0 ? (
                <div className="text-center py-12">
                  <ClockIcon className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                  <p className="text-gray-400">No listings yet</p>
                  <p className="text-sm text-gray-500 mt-2">Your analyzed items will appear here</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {listings.map((listing) => (
                    <motion.div
                      key={listing.id}
                      whileHover={{ scale: 1.02 }}
                      onClick={() => onSelectListing?.(listing)}
                      className="p-4 bg-black/30 border border-gray-700 rounded-lg cursor-pointer hover:border-cyber-purple transition-all duration-200"
                    >
                      <div className="flex gap-4">
                        {/* Image */}
                        <div className="w-20 h-20 flex-shrink-0 rounded-lg overflow-hidden border border-gray-700">
                          <img
                            src={getImageUrl(listing.enhanced_image_url.replace('/image/', ''))}
                            alt={listing.item_name}
                            className="w-full h-full object-cover"
                          />
                        </div>

                        {/* Details */}
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold text-sm mb-1 truncate">
                            {listing.item_name}
                          </h3>
                          <p className="text-xs text-gray-400 mb-2">
                            {listing.category}
                          </p>
                          <div className="flex items-center justify-between">
                            <span className="text-lg font-cyber text-cyber-purple">
                              ${listing.suggested_price}
                            </span>
                            <span className="text-xs text-gray-500">
                              {formatDate(listing.created_at)}
                            </span>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="absolute bottom-0 left-0 right-0 p-6 bg-darker-bg border-t border-gray-800">
                <div className="flex items-center justify-between">
                  <button
                    onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
                    disabled={currentPage === 0 || loading}
                    className={`
                      p-2 rounded-lg transition-all duration-200
                      ${currentPage === 0 || loading
                        ? 'bg-gray-800 text-gray-600 cursor-not-allowed'
                        : 'bg-cyber-purple/20 text-cyber-purple hover:bg-cyber-purple/30'
                      }
                    `}
                  >
                    <ChevronLeftIcon className="w-5 h-5" />
                  </button>

                  <span className="text-sm text-gray-400">
                    Page {currentPage + 1} of {totalPages}
                  </span>

                  <button
                    onClick={() => setCurrentPage(Math.min(totalPages - 1, currentPage + 1))}
                    disabled={currentPage === totalPages - 1 || loading}
                    className={`
                      p-2 rounded-lg transition-all duration-200
                      ${currentPage === totalPages - 1 || loading
                        ? 'bg-gray-800 text-gray-600 cursor-not-allowed'
                        : 'bg-cyber-purple/20 text-cyber-purple hover:bg-cyber-purple/30'
                      }
                    `}
                  >
                    <ChevronRightIcon className="w-5 h-5" />
                  </button>
                </div>
              </div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default RecentListings;