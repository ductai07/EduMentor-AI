import { useState, useEffect } from 'react';
import { useTool } from '../services';
import { FiClock, FiLoader, FiBarChart2, FiCheckCircle } from 'react-icons/fi';

const ProgressTracker = ({ onSubmit, result, loading, error: parentError }) => {
  const [subject, setSubject] = useState('');
  const [progress, setProgress] = useState('');
  const [learningProgress, setLearningProgress] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  
  // Sử dụng kết quả từ component cha nếu có
  useEffect(() => {
    if (result) {
      setLearningProgress(result);
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

  // Lấy tiến độ học tập khi component được mount
  useEffect(() => {
    fetchProgress();
  }, []);

  const fetchProgress = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await useTool('progress', '');
      setLearningProgress(response.response);
    } catch (err) {
      console.error('Error fetching learning progress:', err);
      setError('Đã xảy ra lỗi khi lấy tiến độ học tập. Vui lòng thử lại sau.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!subject.trim()) return;

    setIsLoading(true);
    setError(null);
    setSuccessMessage('');

    try {
      // Nếu có progress, cập nhật tiến độ cho môn học
      const input = progress ? `${subject}: ${progress}` : subject;
      const response = await useTool('progress', input);
      setLearningProgress(response.response);
      
      if (progress) {
        setSuccessMessage(`Đã cập nhật tiến độ cho ${subject}: ${progress}%`);
        setSubject('');
        setProgress('');
      }
    } catch (err) {
      console.error('Error updating learning progress:', err);
      setError('Đã xảy ra lỗi khi cập nhật tiến độ học tập. Vui lòng thử lại sau.');
    } finally {
      setIsLoading(false);
    }
  };

  // Hàm xử lý văn bản để định dạng danh sách đánh số
  const formatText = (text) => {
    if (!text) return '';
    
    // Xử lý danh sách đánh số để hiển thị mỗi mục trên một dòng riêng
    // Tìm các mục danh sách đánh số (1. 2. 3. 4.) và đảm bảo chúng được hiển thị trên các dòng riêng biệt
    let formattedText = text.replace(/(\d+\.)\s+([^\n]+)(?=\s*(?:\d+\.|$))/g, function(match, number, content) {
      return number + ' ' + content.trim() + '\n';
    });
    
    // Đảm bảo không có dòng trống liên tiếp
    formattedText = formattedText.replace(/\n\s*\n/g, '\n');
    
    return formattedText;
  };
  
  const renderProgressList = () => {
    if (!learningProgress || learningProgress === 'Chưa có dữ liệu tiến độ học tập.') {
      return (
        <div className="text-center text-gray-400 py-8">
          <FiBarChart2 className="text-5xl mb-4 mx-auto opacity-20" />
          <p>Chưa có dữ liệu tiến độ học tập</p>
        </div>
      );
    }

    // Phân tích chuỗi tiến độ học tập
    const formattedProgress = formatText(learningProgress);
    const progressLines = formattedProgress.split('\n').filter(line => line.trim());
    
    return (
      <div className="space-y-4">
        {progressLines.map((line, idx) => {
          const match = line.match(/- (.+): (\d+)%/);
          if (!match) return null;
          
          const [, subject, percentage] = match;
          const percentNum = parseInt(percentage, 10);
          
          return (
            <div key={idx} className="bg-gray-800 rounded-lg p-4">
              <div className="flex justify-between items-center mb-2">
                <h4 className="font-medium">{subject}</h4>
                <span className="text-sm font-bold">{percentage}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2.5">
                <div 
                  className={`h-2.5 rounded-full ${getProgressColor(percentNum)}`}
                  style={{ width: `${percentNum}%` }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  // Hàm trả về màu dựa trên phần trăm tiến độ
  const getProgressColor = (percent) => {
    if (percent < 30) return 'bg-red-500';
    if (percent < 70) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <div className="h-full flex flex-col">
      <div className="bg-gray-800 rounded-lg p-6 mb-6">
        <h2 className="text-xl font-bold mb-4 flex items-center">
          <FiClock className="mr-2" />
          Theo dõi tiến độ học tập
        </h2>
        <p className="text-gray-300 mb-4">
          Cập nhật và theo dõi tiến độ học tập của bạn cho từng môn học.
        </p>
        
        <form onSubmit={handleSubmit} className="mt-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-1">
              <input
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="Tên môn học"
                className="w-full bg-gray-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isLoading}
              />
            </div>
            <div className="md:col-span-1">
              <input
                type="number"
                value={progress}
                onChange={(e) => setProgress(e.target.value)}
                placeholder="Tiến độ (%)"
                min="0"
                max="100"
                className="w-full bg-gray-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isLoading}
              />
            </div>
            <div className="md:col-span-1">
              <button
                type="submit"
                disabled={isLoading || !subject.trim()}
                className={`w-full bg-blue-600 text-white rounded-lg px-6 py-2 flex items-center justify-center ${isLoading || !subject.trim() ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-700'}`}
              >
                {isLoading ? (
                  <>
                    <FiLoader className="animate-spin mr-2" />
                    Đang xử lý...
                  </>
                ) : progress ? (
                  'Cập nhật tiến độ'
                ) : (
                  'Xem tiến độ'
                )}
              </button>
            </div>
          </div>
        </form>

        {error && (
          <div className="mt-4 text-red-400 bg-red-900/20 p-3 rounded-lg">
            {error}
          </div>
        )}

        {successMessage && (
          <div className="mt-4 text-green-400 bg-green-900/20 p-3 rounded-lg flex items-center">
            <FiCheckCircle className="mr-2" />
            {successMessage}
          </div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <FiBarChart2 className="mr-2" />
          Tiến độ học tập hiện tại
        </h3>
        
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <FiLoader className="animate-spin text-3xl text-blue-500" />
          </div>
        ) : (
          <div className="whitespace-pre-wrap">
            {renderProgressList()}
          </div>
        )}
        
        <div className="mt-4 text-right">
          <button 
            onClick={fetchProgress}
            className="text-sm text-blue-400 hover:text-blue-300 flex items-center ml-auto"
            disabled={isLoading}
          >
            <FiLoader className={`mr-1 ${isLoading ? 'animate-spin' : ''}`} />
            Làm mới dữ liệu
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProgressTracker;