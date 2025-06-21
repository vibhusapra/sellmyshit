# SellMyShit Frontend

A stunning cyber-retro themed React application for transforming your items into irresistible marketplace listings using AI.

## Features

- **Cyber-Retro Aesthetic**: Inspired by Midjourney and Nous Psyche with neon glowing effects
- **Drag & Drop Upload**: Intuitive image upload with visual feedback
- **Real-time Progress**: Animated progress indicator showing analysis steps
- **Enhanced Image Carousel**: View AI-enhanced product images
- **Smart Listing Generation**: AI-powered titles, descriptions, and pricing
- **Copy-to-Clipboard**: Easy copying of generated content
- **Responsive Design**: Works beautifully on all devices

## Tech Stack

- React with TypeScript
- Tailwind CSS for styling
- Framer Motion for animations
- Axios for API calls
- React Dropzone for file uploads
- React Hot Toast for notifications

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file:
```
REACT_APP_API_URL=http://localhost:8000
```

3. Start the development server:
```bash
npm start
```

The app will open at [http://localhost:3000](http://localhost:3000)

## Build for Production

```bash
npm run build
```

## Design Features

- **Particle Background**: Interactive particle system with connections
- **Gradient Animations**: Smooth color transitions and glow effects
- **Grid Pattern**: Animated cyberpunk grid overlay
- **Glass Morphism**: Frosted glass effect on components
- **Neon Borders**: Glowing borders on interactive elements
- **Custom Fonts**: Orbitron for headers, Space Grotesk for body text

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000` by default. Update the `REACT_APP_API_URL` environment variable to point to your backend.