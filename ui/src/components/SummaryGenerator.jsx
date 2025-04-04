import { useState, useEffect } from 'react';
import { useSummaryTool } from '../services/api';
import { FiList, FiLoader, FiAlertTriangle } from 'react-icons/fi';

const SummaryGenerator = ({ onSubmit, result, loading, error: parentError }) => {
  const [topic, setTopic] = useState('');
  const [summary, setSummary] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Sử dụng kết quả từ component cha nếu có
  useEffect(() => {
    if (result) {
      console.log('SummaryGenerator nhận kết quả:', result);
      // Xử lý các trường hợp khác nhau của kết quả
      if (typeof result === 'object' && result !== null) {
        // Nếu result là object và có thuộc tính response
        if (result.response) {
          setSummary(result.response);
        } else {
          // Nếu không có thuộc tính response, sử dụng toàn bộ object
          setSummary(JSON.stringify(result, null, 2));
        }
      } else if (typeof result === 'string') {
        // Nếu result là string, sử dụng trực tiếp
        setSummary(result);
      } else {
        // Trường hợp khác, chuyển đổi thành chuỗi
        setSummary(String(result));
      }
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
    if (!topic.trim()) return;

    setIsLoading(true);
    setError(null);
    setSummary(null);

    try {
      // Sử dụng hàm onSubmit từ props nếu được cung cấp, nếu không thì gọi API trực tiếp
      if (onSubmit) {
        onSubmit(topic);
      } else {
        const response = await useSummaryTool(topic);
        setSummary(response.response);
      }
    } catch (err) {
      console.error('Error generating summary:', err);
      setError('Đã xảy ra lỗi khi tạo tóm tắt. Vui lòng thử lại sau.');
    } finally {
      setIsLoading(false);
    }
  };

  const renderSummary = () => {
    if (!summary) return null;

    return (
      <div className="mt-6 bg-gray-800 rounded-lg p-6 prose prose-invert max-w-none">
        <h3 className="text-xl font-bold mb-4 flex items-center">
          <FiList className="mr-2" />
          Tóm tắt: {topic}
        </h3>
        <div className="whitespace-pre-wrap">
          {summary.split('\n').map((paragraph, idx) => {
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
          <FiList className="mr-2" />
          Tạo tóm tắt
        </h2>
        <p className="text-gray-300 mb-4">
          Nhập chủ đề bạn muốn tóm tắt và hệ thống sẽ tạo bản tóm tắt ngắn gọn dựa trên tài liệu có sẵn.
        </p>
        
        <form onSubmit={handleSubmit} className="mt-4">
          <div className="flex flex-col md:flex-row gap-4">
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Nhập chủ đề cần tóm tắt (ví dụ: Machine Learning, Neural Networks, etc.)"
              className="flex-1 bg-gray-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !topic.trim()}
              className={`bg-blue-600 text-white rounded-lg px-6 py-2 flex items-center justify-center ${isLoading || !topic.trim() ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-700'}`}
            >
              {isLoading ? (
                <>
                  <FiLoader className="animate-spin mr-2" />
                  Đang xử lý...
                </>
              ) : (
                'Tạo tóm tắt'
              )}
            </button>
          </div>
        </form>

        {error && (
          <div className="mt-4 text-red-400 bg-red-900/20 p-3 rounded-lg flex items-center">
            <FiAlertTriangle className="mr-2" />
            {error}
          </div>
        )}
      </div>

      {renderSummary()}
    </div>
  );
};

export default SummaryGenerator;