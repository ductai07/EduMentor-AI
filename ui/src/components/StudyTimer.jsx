import React, { useState, useEffect, useRef } from 'react';
import { FiPlay, FiPause, FiRefreshCw, FiCoffee, FiBook } from 'react-icons/fi';

const StudyTimer = () => {
  const [mode, setMode] = useState('focus'); // 'focus' or 'break'
  const [timeLeft, setTimeLeft] = useState(25 * 60); // 25 minutes in seconds
  const [isActive, setIsActive] = useState(false);
  const [cycles, setCycles] = useState(0);
  const audioRef = useRef(null);

  useEffect(() => {
    // Create audio element for notification
    audioRef.current = new Audio('/notification.mp3');
    
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
      }
    };
  }, []);

  useEffect(() => {
    let interval = null;
    
    if (isActive && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft(timeLeft => timeLeft - 1);
      }, 1000);
    } else if (isActive && timeLeft === 0) {
      // Play notification sound
      if (audioRef.current) {
        audioRef.current.play().catch(e => console.log("Audio play failed:", e));
      }
      
      // Switch modes
      if (mode === 'focus') {
        setMode('break');
        setTimeLeft(5 * 60); // 5 minute break
        setCycles(cycles + 1);
      } else {
        setMode('focus');
        setTimeLeft(25 * 60); // Back to 25 minute focus
      }
    }
    
    return () => clearInterval(interval);
  }, [isActive, timeLeft, mode, cycles]);

  const toggleTimer = () => {
    setIsActive(!isActive);
  };

  const resetTimer = () => {
    setIsActive(false);
    setMode('focus');
    setTimeLeft(25 * 60);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getProgressPercentage = () => {
    const totalTime = mode === 'focus' ? 25 * 60 : 5 * 60;
    return ((totalTime - timeLeft) / totalTime) * 100;
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <h2 className="text-xl font-bold mb-4">Study Timer</h2>
      
      <div className="flex justify-center mb-6">
        <div className="relative w-48 h-48">
          {/* Progress circle */}
          <svg className="w-full h-full" viewBox="0 0 100 100">
            <circle 
              cx="50" cy="50" r="45" 
              fill="transparent" 
              stroke="#2d3748" 
              strokeWidth="8"
            />
            <circle 
              cx="50" cy="50" r="45" 
              fill="transparent" 
              stroke={mode === 'focus' ? "#3182ce" : "#38a169"} 
              strokeWidth="8"
              strokeDasharray="283"
              strokeDashoffset={283 - (283 * getProgressPercentage() / 100)}
              transform="rotate(-90 50 50)"
            />
          </svg>
          
          {/* Timer text */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <div className="text-3xl font-bold">{formatTime(timeLeft)}</div>
            <div className="text-sm text-gray-400 mt-2 capitalize">
              {mode === 'focus' ? <FiBook className="inline mr-1" /> : <FiCoffee className="inline mr-1" />}
              {mode} Time
            </div>
          </div>
        </div>
      </div>
      
      {/* Controls */}
      <div className="flex justify-center space-x-4">
        <button 
          onClick={toggleTimer}
          className={`p-3 rounded-full ${
            isActive 
              ? "bg-red-600 hover:bg-red-700" 
              : "bg-green-600 hover:bg-green-700"
          }`}
        >
          {isActive ? <FiPause /> : <FiPlay />}
        </button>
        <button 
          onClick={resetTimer}
          className="p-3 rounded-full bg-gray-600 hover:bg-gray-700"
        >
          <FiRefreshCw />
        </button>
      </div>
      
      {/* Stats */}
      <div className="mt-6 text-center text-gray-400">
        <p>Completed cycles: {cycles}</p>
        <p className="text-xs mt-1">Each cycle: 25min focus + 5min break</p>
      </div>
    </div>
  );
};

export default StudyTimer;