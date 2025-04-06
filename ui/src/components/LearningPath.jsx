import React, { useState, useEffect, useCallback, useRef } from 'react';
import { FiCheckCircle, FiCircle, FiArrowRight, FiRefreshCw, FiAlertCircle } from 'react-icons/fi';
import { useTool } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const LearningPath = ({ subject, onProgressUpdate }) => {
  const [path, setPath] = useState([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [progressValue, setProgressValue] = useState(0);
  const [updating, setUpdating] = useState(false);
  const { token, isAuthenticated, user } = useAuth();
  
  // Sử dụng useRef để kiểm soát việc gọi API
  const hasFetchedRef = useRef(false);

  // Fetch learning path with authentication
  const fetchLearningPath = useCallback(async () => {
    if (!subject || !isAuthenticated || !token) {
      setError("Bạn cần đăng nhập để xem lộ trình học.");
      setLoading(false);
      return;
    }
    
    // Tránh gọi API nhiều lần nếu đã có dữ liệu
    if (hasFetchedRef.current && path.length > 0) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const result = await useTool('study_plan', subject);
      
      if (!result || !result.response || !result.response.plan) {
        throw new Error("Invalid response format");
      }
      
      // Transform the study plan into a sequential path
      const pathSteps = Object.entries(result.response.plan || {}).map(([key, value]) => ({
        title: key,
        description: value,
        completed: false
      }));
      
      setPath(pathSteps);
      
      // Fetch current progress for this subject
      try {
        // Đảm bảo username được truyền đúng format
        const progressInput = subject;
        const progressResult = await useTool('progress', progressInput);
        
        if (progressResult && progressResult.response && progressResult.response.progress) {
          const progress = progressResult.response.progress;
          setProgressValue(progress);
          
          // Update steps completed based on progress
          if (progress > 0) {
            const stepsToComplete = Math.floor((progress / 100) * pathSteps.length);
            const updatedPath = pathSteps.map((step, idx) => ({
              ...step,
              completed: idx < stepsToComplete
            }));
            setPath(updatedPath);
            setCurrentStep(Math.min(stepsToComplete, pathSteps.length - 1));
          }
        }
        
        // Đánh dấu đã fetch thành công
        hasFetchedRef.current = true;
      } catch (progressError) {
        console.warn("Could not fetch current progress:", progressError);
      }
    } catch (error) {
      console.error("Error fetching learning path:", error);
      setError("Không thể tải lộ trình học tập. Vui lòng thử lại sau.");
      hasFetchedRef.current = false;
    } finally {
      setLoading(false);
    }
  }, [subject, isAuthenticated, token, path.length]);

  // Reset fetch flag when subject changes
  useEffect(() => {
    hasFetchedRef.current = false;
  }, [subject]);

  // Initial fetch
  useEffect(() => {
    if (!hasFetchedRef.current) {
      fetchLearningPath();
    }
  }, [fetchLearningPath]);

  // Mark step as complete and update progress
  const markStepComplete = async (index) => {
    if (updating || !isAuthenticated || !token) {
      setError("Bạn cần đăng nhập để cập nhật tiến độ.");
      return;
    }
    
    try {
      setUpdating(true);
      
      // Calculate new progress percentage based on completed steps
      const totalSteps = path.length;
      const completedSteps = path.filter(step => step.completed).length + 1; // +1 for current step
      const newProgressValue = Math.round((completedSteps / totalSteps) * 100);
      
      // Update local state first for better UX
      setPath(prev => prev.map((step, i) => 
        i === index ? {...step, completed: true} : step
      ));
      setCurrentStep(index + 1 < path.length ? index + 1 : index);
      setProgressValue(newProgressValue);
      
      // Fix: Tạo đúng định dạng progress input
      // Format: { subject, progress } thay vì string 
      const progressInput = {
        subject: subject,
        progress: newProgressValue
      };
      
      const result = await useTool('progress', progressInput);
      
      if (result && result.success) {
        // Notify parent component about progress update
        if (onProgressUpdate) {
          onProgressUpdate(subject, newProgressValue);
        }
        console.log(`Progress updated successfully: ${subject} - ${newProgressValue}%`);
      } else {
        console.error("Failed to update progress:", result);
        // Revert UI if server update fails
        setPath(prev => prev.map((step, i) => 
          i === index ? {...step, completed: false} : step
        ));
        setCurrentStep(index);
        setError("Không thể cập nhật tiến độ. Máy chủ không phản hồi.");
      }
    } catch (error) {
      console.error("Error updating progress:", error);
      setError("Không thể cập nhật tiến độ. Vui lòng thử lại.");
      
      // Revert UI changes on error
      setPath(prev => prev.map((step, i) => 
        i === index ? {...step, completed: false} : step
      ));
      setCurrentStep(index);
    } finally {
      setUpdating(false);
    }
  };

  // Force refresh and clear cached state
  const handleRefresh = () => {
    hasFetchedRef.current = false;
    fetchLearningPath();
  };

  // Kiểm tra xác thực
  if (!isAuthenticated || !token) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="text-center py-6">
          <FiAlertCircle className="text-yellow-400 text-3xl mx-auto mb-2" />
          <p className="text-gray-300">Bạn cần đăng nhập để xem lộ trình học tập.</p>
        </div>
      </div>
    );
  }

  // Rest of component
  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Lộ trình học: {subject}</h2>
        <div className="flex items-center">
          {progressValue > 0 && (
            <div className="mr-4 bg-gray-700 rounded-full h-2 w-24 overflow-hidden">
              <div 
                className={`h-full ${
                  progressValue < 30 ? 'bg-red-500' : 
                  progressValue < 70 ? 'bg-yellow-500' : 'bg-green-500'
                }`} 
                style={{ width: `${progressValue}%` }}
              ></div>
            </div>
          )}
          <span className="text-gray-300 text-sm mr-2">{progressValue}%</span>
          <button 
            onClick={handleRefresh} 
            className="p-1 hover:bg-gray-700 rounded-full"
            title="Làm mới"
            disabled={loading}
          >
            <FiRefreshCw className={`text-gray-400 ${loading ? 'animate-spin' : 'hover:text-blue-400'}`} />
          </button>
        </div>
      </div>
      
      {error && (
        <div className="bg-red-900/30 border border-red-700 p-4 rounded-lg mb-4 flex items-center">
          <FiAlertCircle className="text-red-500 mr-2" />
          <p className="text-red-300">{error}</p>
          <button 
            onClick={handleRefresh}
            className="ml-auto bg-red-700 hover:bg-red-600 px-3 py-1 rounded text-sm"
          >
            Thử lại
          </button>
        </div>
      )}
      
      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : path.length === 0 ? (
        <div className="text-center py-8 text-gray-400">
          <p>Chưa có lộ trình học tập cho môn này.</p>
          <button 
            onClick={handleRefresh}
            className="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
            Tạo lộ trình mới
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {path.map((step, index) => (
            <div 
              key={index} 
              className={`flex items-start p-4 rounded-lg transition-all duration-300 ${
                currentStep === index ? 'bg-blue-900 bg-opacity-30 border border-blue-500' : 
                step.completed ? 'bg-green-900 bg-opacity-20' : 'bg-gray-700'
              }`}
            >
              <div className="mr-3 mt-1">
                {step.completed ? 
                  <FiCheckCircle className="text-green-400 text-xl" /> : 
                  index === currentStep ? 
                    <FiCircle className="text-blue-400 text-xl animate-pulse" /> :
                    <FiCircle className="text-gray-400 text-xl" />
                }
              </div>
              <div className="flex-1">
                <h3 className="font-bold text-lg">{step.title}</h3>
                <p className="text-gray-300 mt-1">{step.description}</p>
                
                {index === currentStep && !step.completed && (
                  <div className="mt-3 flex justify-end">
                    <button 
                      onClick={() => markStepComplete(index)}
                      disabled={updating}
                      className={`bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center ${
                        updating ? 'opacity-70 cursor-not-allowed' : ''
                      }`}
                    >
                      {updating ? 'Đang lưu...' : 'Hoàn thành'} 
                      {updating ? (
                        <FiRefreshCw className="ml-2 animate-spin" />
                      ) : (
                        <FiArrowRight className="ml-2" />
                      )}
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default LearningPath;