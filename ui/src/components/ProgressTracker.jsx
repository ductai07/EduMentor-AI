import { useState, useEffect } from 'react';
import { FiClock, FiLoader, FiBarChart2, FiCheckCircle, FiAlertTriangle, FiActivity } from 'react-icons/fi';
import { useAuth } from '../contexts/AuthContext';

// Use props from parent (Tools.jsx)
const ProgressTracker = ({ onSubmit, result, loading, error }) => {
  const [subjectInput, setSubjectInput] = useState('');
  const [progressInput, setProgressInput] = useState('');
  const [progressData, setProgressData] = useState(null); // Store parsed progress data
  const [retrievedProgress, setRetrievedProgress] = useState(null); // Keep raw text for fallback
  const [successMessage, setSuccessMessage] = useState('');
  const { user, token } = useAuth();

  // Process the result prop when it changes
  useEffect(() => {
    console.log('ProgressTracker result changed:', result);
    setRetrievedProgress(null);
    setProgressData(null);
    setSuccessMessage('');
    
    if (!result) return;
    
    try {
      // First try to parse the result as JSON if it's a string
      if (typeof result === 'string') {
        if (result.includes('Đã cập nhật tiến độ cho') && result.includes('%')) {
          setSuccessMessage(result);
          return;
        }
        
        // Try to parse as JSON
        try {
          const jsonData = JSON.parse(result);
          if (jsonData && typeof jsonData === 'object') {
            processProgressObject(jsonData);
            return;
          }
        } catch (e) {
          // If not valid JSON, treat as text
          setRetrievedProgress(result);
          tryExtractProgressData(result);
        }
      } 
      else if (typeof result === 'object') {
        processProgressObject(result);
      }
    } catch (err) {
      console.error("Error processing progress tracker result:", err);
      setRetrievedProgress(typeof result === 'string' ? result : JSON.stringify(result, null, 2));
    }
  }, [result]);
  
  // Helper to process progress data object
  const processProgressObject = (obj) => {
    if (obj.error) {
      console.error("Error in progress tracker result:", obj.error);
    } 
    else if (obj.message || obj.response) {
      const message = obj.message || obj.response;
      
      if (typeof message === 'string') {
        if (message.includes('Đã cập nhật tiến độ cho')) {
          setSuccessMessage(message);
        } else {
          setRetrievedProgress(message);
          tryExtractProgressData(message);
        }
      } 
      else if (typeof message === 'object') {
        // If response is an object, attempt to extract progress data
        setProgressData(extractProgressFromObject(message));
        setRetrievedProgress(JSON.stringify(message, null, 2));
      }
    } 
    else if (obj.subjects || obj.progress) {
      // Direct subject data
      setProgressData(extractProgressFromObject(obj));
      setRetrievedProgress(JSON.stringify(obj, null, 2));
    } 
    else {
      setRetrievedProgress(JSON.stringify(obj, null, 2));
      tryExtractProgressData(JSON.stringify(obj, null, 2));
    }
  };
  
  // Try to extract subject progress data from text
  const tryExtractProgressData = (text) => {
    try {
      // Regex to find patterns like "Subject: 75%" or similar formats
      const progressPattern = /([^:]+):\s*(\d+)%/g;
      const matches = Array.from(text.matchAll(progressPattern));
      
      if (matches.length > 0) {
        const extracted = {};
        matches.forEach(match => {
          const subject = match[1].trim();
          const progress = parseInt(match[2], 10);
          if (!isNaN(progress)) {
            extracted[subject] = { progress };
          }
        });
        
        if (Object.keys(extracted).length > 0) {
          setProgressData({ subjects: extracted });
        }
      }
    } catch (e) {
      console.error("Failed to extract progress data from text:", e);
    }
  };

  // Extract progress data from object
  const extractProgressFromObject = (obj) => {
    // Case 1: Direct subjects object
    if (obj.subjects) {
      return { subjects: obj.subjects };
    }
    
    // Case 2: Nested in data
    if (obj.data && obj.data.subjects) {
      return { subjects: obj.data.subjects };
    }
    
    // Case 3: Subject keys directly at top level with progress values
    const extracted = {};
    let hasData = false;
    
    Object.entries(obj).forEach(([key, value]) => {
      // Check if the value is a number or has a progress property
      if (typeof value === 'number') {
        extracted[key] = { progress: value };
        hasData = true;
      } else if (value && typeof value === 'object' && 'progress' in value) {
        extracted[key] = { ...value };
        hasData = true;
      }
    });
    
    return hasData ? { subjects: extracted } : null;
  };

  // Handle fetching progress for a subject (or all)
  const handleFetchProgress = (e) => {
    e.preventDefault();
    if (!user || !token) {
      return;
    }
    setRetrievedProgress(null);
    setProgressData(null);
    setSuccessMessage('');
    onSubmit(subjectInput.trim());
  };

  // Handle updating progress for a subject
  const handleUpdateProgress = (e) => {
    e.preventDefault();
    if (!user || !token) {
      return;
    }
    const subjectToUpdate = subjectInput.trim();
    const progressToUpdate = progressInput.trim();

    if (!subjectToUpdate || !progressToUpdate) {
      return;
    }
    const progressValue = parseInt(progressToUpdate, 10);
    if (isNaN(progressValue) || progressValue < 0 || progressValue > 100) {
      return;
    }
    setRetrievedProgress(null);
    setProgressData(null);
    setSuccessMessage('');

    const updateInputString = `${subjectToUpdate}: ${progressValue}`;
    onSubmit(updateInputString);
  };

  // Get progress color based on percentage
  const getProgressColor = (percent) => {
    if (percent < 30) return 'bg-red-500';
    if (percent < 70) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  // Format date string
  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('vi-VN');
    } catch (e) {
      return dateStr;
    }
  };

  // Render progress data in a more visual way
  const renderProgressData = () => {
    if (!progressData || !progressData.subjects) {
      return null;
    }
    
    const subjects = progressData.subjects;
    
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold mb-2 text-gray-200 flex items-center">
          <FiActivity className="mr-2 text-blue-400" />
          Tiến độ học tập
        </h3>
        
        {Object.entries(subjects).map(([subject, data]) => (
          <div key={subject} className="bg-gray-700/70 p-4 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium text-lg">{subject}</span>
              <span className="bg-blue-900/30 px-2 py-1 rounded text-blue-300">
                {data.progress || 0}%
              </span>
            </div>
            
            <div className="w-full bg-gray-600 rounded-full h-3">
              <div 
                className={`${getProgressColor(data.progress || 0)} h-3 rounded-full transition-all duration-500`}
                style={{ width: `${data.progress || 0}%` }}
              />
            </div>
            
            {data.progress_updated_at && (
              <div className="mt-2 text-sm text-gray-400">
                Cập nhật lần cuối: {formatDate(data.progress_updated_at)}
              </div>
            )}
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="h-full flex flex-col p-4 md:p-6">
      <div className="bg-gray-800 rounded-lg p-4 md:p-6 mb-6 shadow-lg">
        <h2 className="text-xl font-bold mb-4 flex items-center text-gray-100">
          <FiBarChart2 className="mr-2 text-green-400" />
          Theo dõi & Cập nhật Tiến độ
        </h2>
        <p className="text-gray-300 mb-4 text-sm">
          Xem tiến độ học tập của bạn hoặc cập nhật tiến độ cho một môn học cụ thể.
        </p>

        {/* Form for Fetching Progress */}
        <form onSubmit={handleFetchProgress} className="mt-4 border-b border-gray-700 pb-4 mb-4">
           <label htmlFor="fetchSubject" className="block text-sm font-medium text-gray-300 mb-1">
             Xem tiến độ môn học (để trống để xem tất cả)
           </label>
          <div className="flex flex-col sm:flex-row gap-3">
            <input
              id="fetchSubject"
              type="text"
              value={subjectInput}
              onChange={(e) => setSubjectInput(e.target.value)}
              placeholder="Nhập tên môn học"
              className="flex-grow bg-gray-700 text-white rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent placeholder-gray-500"
              disabled={loading || !token}
            />
            <button
              type="submit"
              disabled={loading || !token}
              className={`bg-green-600 text-white rounded-md px-5 py-2 flex items-center justify-center transition duration-150 ease-in-out ${loading || !token ? 'opacity-60 cursor-not-allowed' : 'hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 focus:ring-offset-gray-800'}`}
            >
              {loading ? <FiLoader className="animate-spin" /> : 'Xem tiến độ'}
            </button>
          </div>
        </form>

        {/* Form for Updating Progress */}
        <form onSubmit={handleUpdateProgress} className="mt-4">
           <label htmlFor="updateSubject" className="block text-sm font-medium text-gray-300 mb-1">
             Cập nhật tiến độ môn học
           </label>
           <div className="flex flex-col sm:flex-row gap-3">
             <input
               id="updateSubject"
               type="text"
               value={subjectInput}
               onChange={(e) => setSubjectInput(e.target.value)}
               placeholder="Tên môn học cần cập nhật"
               className="flex-grow bg-gray-700 text-white rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent placeholder-gray-500"
               disabled={loading || !token}
               required
             />
             <input
               type="number"
               value={progressInput}
               onChange={(e) => setProgressInput(e.target.value)}
               placeholder="% Hoàn thành (0-100)"
               min="0"
               max="100"
               className="w-full sm:w-40 bg-gray-700 text-white rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent placeholder-gray-500"
               disabled={loading || !token}
               required
             />
             <button
               type="submit"
               disabled={loading || !token || !subjectInput.trim() || !progressInput.trim()}
               className={`bg-yellow-600 text-white rounded-md px-5 py-2 flex items-center justify-center transition duration-150 ease-in-out ${loading || !token || !subjectInput.trim() || !progressInput.trim() ? 'opacity-60 cursor-not-allowed' : 'hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500 focus:ring-offset-gray-800'}`}
             >
               {loading ? <FiLoader className="animate-spin" /> : 'Cập nhật'}
             </button>
           </div>
        </form>

        {!token && <p className="text-xs text-yellow-400 mt-4">Bạn cần đăng nhập để sử dụng tính năng này.</p>}

        {/* Display Error or Success Messages */}
        {error && !loading && (
          <div className="mt-4 text-red-400 bg-red-900/30 p-3 rounded-md flex items-center text-sm border border-red-700">
            <FiAlertTriangle className="mr-2 flex-shrink-0" />
             <span>{error}</span>
           </div>
         )}
          {successMessage && !loading && !error && (
           <div className="mt-4 text-green-300 bg-green-900/30 p-3 rounded-md flex items-center text-sm border border-green-700">
             <FiCheckCircle className="mr-2 flex-shrink-0" />
             <span>{successMessage}</span>
           </div>
         )}
      </div>

      {/* Display Area for Fetched Progress */}
      <div className="flex-1 mt-6 min-h-0 overflow-y-auto">
        {loading && (
          <div className="flex items-center justify-center h-full text-gray-400">
            <FiLoader className="animate-spin mr-2 h-8 w-8" />
             Đang tải...
           </div>
        )}
        
        {/* Visual Progress Display */}
        {!loading && !error && progressData && (
          <div className="bg-gray-700/50 p-4 rounded-lg shadow-lg">
            {renderProgressData()}
          </div>
        )}
        
        {/* Fallback Raw Text Display */}
        {!loading && !error && !progressData && retrievedProgress && (
          <div className="bg-gray-700/50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-2 text-gray-200">Kết quả tiến độ:</h3>
            <pre className="text-gray-300 whitespace-pre-wrap text-sm break-all">{retrievedProgress}</pre>
          </div>
        )}
        
        {!loading && !retrievedProgress && !progressData && !error && !successMessage && (
          <div className="flex items-center justify-center h-full text-gray-500">
            <FiBarChart2 className="text-5xl opacity-30" />
            <span className="ml-2">Nhập môn học để xem hoặc cập nhật tiến độ.</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProgressTracker;
