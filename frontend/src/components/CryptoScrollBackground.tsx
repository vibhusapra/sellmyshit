import React from 'react';
import { motion } from 'framer-motion';

const CryptoScrollBackground: React.FC = () => {
  // Fake trading data and scam messages
  const tradingLines = [
    'BTC/USDT +12.47% 🚀 ETH/USDT +8.93% 💎 DOGE/USDT +156.82% 🌙',
    'WHALE ALERT: 1,000 BTC moved • PUMP INCOMING • NOT FINANCIAL ADVICE',
    '🔥 SHIB TO $1 CONFIRMED 🔥 DIAMOND HANDS ONLY 💎 HODL THE LINE',
    'BREAKING: Elon tweets again • DOGE +400% • TO THE MOON 🚀🚀🚀',
    '0x1a2b...7f9c BOUGHT 420,690 PEPE • WHALE MOVES • FOLLOW THE MONEY',
    'BULL RUN ACTIVATED ✅ ALTSEASON INCOMING ✅ 100X GUARANTEED ✅',
    'LAST CHANCE: Buy before 1000X • Trust me bro • Not financial advice'
  ];

  const priceLines = [
    'BTC: $69,420 (+4.20%) ETH: $3,333 (+7.77%) SOL: $222 (+12.34%)',
    'DOGE: $0.420 (+69%) SHIB: $0.00069 (+420%) PEPE: $0.000069 (+1337%)',
    'APE: $13.37 (+42%) LINK: $14.88 (+33%) ADA: $0.69 (+21%)',
    'MATIC: $1.234 (+15%) DOT: $6.66 (+18%) AVAX: $42.0 (+25%)'
  ];

  const scamMessages = [
    '🚨 URGENT: Last 24hrs to join exclusive pump group 🚨',
    '💰 MY PORTFOLIO: +69,420% this year (PROOF IN BIO) 💰',
    '🔮 NEXT 1000X GEM REVEALED (Limited time) 🔮',
    '⚡ WHALE SIGNALS: 95% accuracy • Join now ⚡'
  ];

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden opacity-70">
      {/* Fast scrolling trading data */}
      {tradingLines.map((line, index) => (
        <motion.div
          key={`trading-${index}`}
          className="absolute whitespace-nowrap text-green-400 font-mono text-sm"
          style={{
            top: `${15 + index * 8}%`,
            fontSize: '11px',
            fontFamily: 'Courier New, monospace'
          }}
          animate={{
            x: [window.innerWidth, -2000],
          }}
          transition={{
            duration: 15 + index * 2,
            repeat: Infinity,
            ease: 'linear',
            delay: index * 3
          }}
        >
          {line}
        </motion.div>
      ))}

      {/* Price tickers */}
      {priceLines.map((line, index) => (
        <motion.div
          key={`price-${index}`}
          className="absolute whitespace-nowrap text-amber-400 font-mono text-xs"
          style={{
            top: `${50 + index * 6}%`,
            fontSize: '10px',
            fontFamily: 'Courier New, monospace'
          }}
          animate={{
            x: [-1500, window.innerWidth],
          }}
          transition={{
            duration: 20 + index * 3,
            repeat: Infinity,
            ease: 'linear',
            delay: index * 4
          }}
        >
          {line}
        </motion.div>
      ))}

      {/* Scam messages (slower, more prominent) */}
      {scamMessages.map((message, index) => (
        <motion.div
          key={`scam-${index}`}
          className="absolute whitespace-nowrap text-yellow-300 font-mono text-sm font-bold"
          style={{
            top: `${75 + index * 5}%`,
            fontSize: '12px',
            fontFamily: 'Courier New, monospace',
            textShadow: '0 0 10px currentColor'
          }}
          animate={{
            x: [window.innerWidth, -2500],
          }}
          transition={{
            duration: 25 + index * 2,
            repeat: Infinity,
            ease: 'linear',
            delay: index * 6
          }}
        >
          {message}
        </motion.div>
      ))}

      {/* Binary/hex data streams */}
      {[...Array(5)].map((_, index) => (
        <motion.div
          key={`binary-${index}`}
          className="absolute whitespace-nowrap text-green-600 font-mono text-xs opacity-40"
          style={{
            top: `${10 + index * 20}%`,
            fontSize: '9px',
            fontFamily: 'Courier New, monospace'
          }}
          animate={{
            x: [window.innerWidth, -1000],
          }}
          transition={{
            duration: 30 + index * 5,
            repeat: Infinity,
            ease: 'linear',
            delay: index * 2
          }}
        >
          {Array.from({ length: 100 }, () => 
            Math.random() > 0.5 ? '1' : '0'
          ).join('').match(/.{1,8}/g)?.join(' ')}
        </motion.div>
      ))}
    </div>
  );
};

export default CryptoScrollBackground;