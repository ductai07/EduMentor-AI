import { useState, useEffect } from 'react';
import { useStudyPlanTool } from '../services/api';
import { FiBookOpen, FiClock, FiLoader } from 'react-icons/fi';

const StudyPlanCreator = ({ onSubmit, result, loading, error: parentError }) => {
  const [subject, setSubject] = useState('');
  const [studyPlan, setStudyPlan] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Sử dụng kết quả từ component cha nếu có
  useEffect(() => {
    if (result) {
      setStudyPlan(result);
    }
  }, [result]);
  
  // Sử dụng trạng thái loading từ component cha
  useEffect(() => {
    if (loading !== undefined) {
      setIsLoading(loading);
    }
  }, [loading]);
  
  // Sử dụng lỗi từ component cha
  useEffect(() => {
    if (parentError) {
      setError(parentError);
    }
  }, [parentError]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!subject.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await useStudyPlanTool(subject);
      setStudyPlan(response.response);
    } catch (err) {
      console.error('Error creating study plan:', err);
      setError('Đã xảy ra lỗi khi tạo kế hoạch học tập. Vui lòng thử lại sau.');
    } finally {
      setIsLoading(false);
    }
  };

  const renderStudyPlan = () => {
    if (!studyPlan) return null;

    return (
      <div className="mt-6 bg-gray-800 rounded-lg p-6 prose prose-invert max-w-none">
        <h3 className="text-xl font-bold mb-4 flex items-center">
          <FiBookOpen className="mr-2" />
          Kế hoạch học tập: {subject}
        </h3>
        <div className="whitespace-pre-wrap">
          {studyPlan.split('\n').map((paragraph, idx) => {
            if (paragraph.trim() === '') return <br key={idx} />;
            if (paragraph.startsWith('#')) {
              return <h4 key={idx} className="font-bold mt-4">{paragraph.replace(/^#+\s/, '')}</h4>;
            }
            if (paragraph.startsWith('-')) {
              // Xác định mức độ thụt lề dựa trên số lượng khoảng trắng đầu dòng
              const indentMatch = paragraph.match(/^(\s*)-/);
              const indentLevel = indentMatch ? Math.floor(indentMatch[1].length / 2) : 0;
              
              return (
                <div 
                  key={idx} 
                  className="flex items-start mt-2"
                  style={{ marginLeft: `${indentLevel * 1.5 + 1}rem` }}
                >
                  <span className="mr-2 flex-shrink-0">•</span>
                  <span className="flex-1">{paragraph.replace(/^\s*-\s*/, '')}</span>
                </div>
              );
            }
            if (paragraph.match(/^\d+\.\s/)) {
              return (
                <div key={idx} className="flex items-start ml-4 mt-2">
                  <span className="mr-2 flex-shrink-0">{paragraph.match(/^(\d+)\./)[1] + '.'}</span>
                  <span className="flex-1">{paragraph.replace(/^\d+\.\s/, '')}</span>
                </div>
              );
            }
            return <p key={idx} className="mb-2">{paragraph}</p>;
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="h-full flex flex-col">
      <div className="bg-gray-800 rounded-lg p-6 mb-6">
        <h2 className="text-xl font-bold mb-4 flex items-center">
          <FiClock className="mr-2" />
          Tạo kế hoạch học tập
        </h2>
        <p className="text-gray-300 mb-4">
          Nhập chủ đề bạn muốn học và hệ thống sẽ tạo kế hoạch học tập chi tiết dựa trên tài liệu có sẵn.
        </p>
        
        <form onSubmit={handleSubmit} className="mt-4">
          <div className="flex flex-col md:flex-row gap-4">
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="Nhập chủ đề học tập (ví dụ: Machine Learning, Calculus, etc.)"
              className="flex-1 bg-gray-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !subject.trim()}
              className={`bg-blue-600 text-white rounded-lg px-6 py-2 flex items-center justify-center ${isLoading || !subject.trim() ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-700'}`}
            >
              {isLoading ? (
                <>
                  <FiLoader className="animate-spin mr-2" />
                  Đang tạo...
                </>
              ) : (
                'Tạo kế hoạch'
              )}
            </button>
          </div>
        </form>

        {error && (
          <div className="mt-4 text-red-400 bg-red-900/20 p-3 rounded-lg">
            {error}
          </div>
        )}
      </div>

      {isLoading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="flex flex-col items-center">
            <FiLoader className="animate-spin text-4xl text-blue-500 mb-4" />
            <p className="text-gray-300">Đang tạo kế hoạch học tập...</p>
          </div>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto">
          {renderStudyPlan()}
          
          {!studyPlan && !isLoading && (
            <div className="flex-1 flex items-center justify-center text-gray-400">
              <div className="text-center">
                <FiBookOpen className="text-5xl mb-4 mx-auto opacity-20" />
                <p>Nhập chủ đề và nhấn "Tạo kế hoạch" để bắt đầu</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default StudyPlanCreator;