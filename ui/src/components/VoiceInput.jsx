import React, { useState, useEffect } from 'react';
import { FiMic, FiMicOff, FiLoader } from 'react-icons/fi';

const VoiceInput = ({ onTranscript, disabled = false }) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState(null);
  const [recognition, setRecognition] = useState(null);

  useEffect(() => {
    // Check if browser supports speech recognition
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setError('Speech recognition is not supported in this browser.');
      return;
    }

    // Initialize speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognitionInstance = new SpeechRecognition();
    
    recognitionInstance.continuous = true;
    recognitionInstance.interimResults = true;
    recognitionInstance.lang = 'vi-VN'; // Set to Vietnamese
    
    recognitionInstance.onresult = (event) => {
      const current = event.resultIndex;
      const transcriptText = event.results[current][0].transcript;
      setTranscript(transcriptText);
    };
    
    recognitionInstance.onerror = (event) => {
      console.error('Speech recognition error', event.error);
      setError(`Error: ${event.error}`);
      setIsListening(false);
    };
    
    recognitionInstance.onend = () => {
      if (isListening) {
        recognitionInstance.start();
      }
    };
    
    setRecognition(recognitionInstance);
    
    return () => {
      if (recognitionInstance) {
        recognitionInstance.stop();
      }
    };
  }, []);

  useEffect(() => {
    if (transcript) {
      onTranscript(transcript);
    }
  }, [transcript, onTranscript]);

  const toggleListening = () => {
    if (!recognition) return;
    
    if (isListening) {
      recognition.stop();
      setIsListening(false);
      
      // Submit final transcript
      if (transcript) {
        onTranscript(transcript);
        setTranscript('');
      }
    } else {
      setTranscript('');
      recognition.start();
      setIsListening(true);
    }
  };

  if (error) {
    return (
      <button 
        className="p-3 rounded-full bg-gray-700 text-gray-500 cursor-not-allowed"
        disabled={true}
        title={error}
      >
        <FiMicOff />
      </button>
    );
  }

  return (
    <button 
      onClick={toggleListening}
      disabled={disabled}
      className={`p-3 rounded-full transition-all duration-300 ${
        disabled 
          ? "bg-gray-700 text-gray-500 cursor-not-allowed" 
          : isListening
            ? "bg-red-600 hover:bg-red-700 animate-pulse"
            : "bg-blue-600 hover:bg-blue-700"
      }`}
      title={isListening ? "Stop listening" : "Start voice input"}
    >
      {isListening ? <FiMic /> : <FiMic />}
    </button>
  );
};

export default VoiceInput;