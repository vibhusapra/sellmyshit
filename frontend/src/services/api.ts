import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});


export interface ItemAnalysis {
  item_name: string;
  category: string;
  condition: string;
  brand?: string;
  model?: string;
  key_features: string[];
  potential_issues: string[];
  color?: string;
  size?: string;
  material?: string;
  estimated_price?: number;
}

export interface PriceData {
  min_price?: number;
  max_price?: number;
  avg_price?: number;
  demand_level?: string;
  best_time_to_sell?: string;
  items_found?: number;
  ai_estimated?: boolean;
}

export interface MarketInsights {
  demand_level?: string;
  seasonal_trends?: string[];
  competitor_analysis?: string;
  best_time_to_sell?: string;
  pricing_strategy?: string;
  target_audience?: string[];
}

export interface ImageInsights {
  photo_tips: string[];
  staging_suggestions: string[];
  lighting_recommendations: string;
  angle_suggestions: string[];
  background_tips: string;
}

export interface EnhancedImage {
  type: string;
  description: string;
  path: string;
  url: string;
}

export interface PlatformListing {
  title: string;
  description: string;
  tags?: string[];
  keywords?: string[];
  category_suggestions?: string[];
  pricing_note?: string;
  item_specifics?: Record<string, string>;
  category?: string;
}

export interface ListingContent {
  title: string;
  description: string;
  suggested_price: number;
  keywords: string[];
}

export interface AnalysisResponse {
  listing_id: number;
  item_analysis: ItemAnalysis;
  price_data: PriceData;
  market_insights: MarketInsights;
  image_insights?: ImageInsights;
  listing: ListingContent;
  platform_listings: {
    ebay?: PlatformListing;
    craigslist?: PlatformListing;
    facebook?: PlatformListing;
  };
  enhanced_images: EnhancedImage[];
  enhancement_mode: string;
}

export interface ListingSummary {
  id: number;
  item_name: string;
  category: string;
  suggested_price: number;
  created_at: string;
  enhanced_image_url: string;
}

export interface ListingsResponse {
  total: number;
  listings: ListingSummary[];
}

export const processItem = async (
  file: File,
  enhancementMode: 'smart' | 'quick' | 'custom' = 'quick',
  customPrompts?: string[],
  realMode: boolean = false
): Promise<AnalysisResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('enhancement_mode', enhancementMode);
  formData.append('real_mode', realMode.toString());
  
  if (customPrompts && customPrompts.length > 0) {
    formData.append('custom_prompts', JSON.stringify(customPrompts));
  }

  const response = await api.post<AnalysisResponse>('/process-item', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};


export const generateImages = async (
  file: File,
  mode: 'smart' | 'custom',
  customPrompts?: string[],
  itemAnalysis?: ItemAnalysis
) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('mode', mode);
  
  if (customPrompts) {
    formData.append('custom_prompts', JSON.stringify(customPrompts));
  }
  
  if (itemAnalysis) {
    formData.append('item_analysis', JSON.stringify(itemAnalysis));
  }

  const response = await api.post('/generate-images', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const getMarketInsights = async (itemName: string, category: string) => {
  const response = await api.get<MarketInsights>(
    `/market-insights/${encodeURIComponent(itemName)}/${encodeURIComponent(category)}`
  );
  return response.data;
};

export const getListing = async (listingId: number) => {
  const response = await api.get(`/listing/${listingId}`);
  return response.data;
};

export const getListings = async (skip: number = 0, limit: number = 10): Promise<ListingsResponse> => {
  const response = await api.get<ListingsResponse>(`/listings?skip=${skip}&limit=${limit}`);
  return response.data;
};

export const downloadListing = async (listingId: number) => {
  const response = await api.get(`/download-listing/${listingId}`, {
    responseType: 'blob',
  });
  
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `listing_${listingId}.json`);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export const getImageUrl = (filename: string) => {
  return `${API_BASE_URL}/image/${filename}`;
};

export const getHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export interface ImageVariation {
  type: string;
  prompt: string;
  url: string;
  error: string | null;
  meme_title?: string;
  meme_context?: string;
}

export interface VariationsResponse {
  success: boolean;
  total_requested: number;
  total_generated: number;
  variations: ImageVariation[];
}

export const generateVariations = async (file: File): Promise<VariationsResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<VariationsResponse>('/generate-variations', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};