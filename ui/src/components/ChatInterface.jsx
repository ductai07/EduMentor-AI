import React, { useState, useEffect, useRef, useCallback } from 'react';
import { FiSend, FiLoader } from 'react-icons/fi';
import { askQuestion, getChatHistory } from '../services/api'; // Import getChatHistory
import { useAuth } from '../contexts/AuthContext'; // Import useAuth
import { TypeAnimation } from 'react-type-animation';

function ChatInterface() {
  const { currentUser, token } = useAuth(); // Get user and token
  const [messages, setMessages] = useState([]); // Initialize empty
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // --- Fetch Chat History ---
  useEffect(() => {
    const loadHistory = async () => {
      if (currentUser && token) {
        try {
          setIsLoading(true); // Show loading indicator while fetching history
          setError(null);
          const history = await getChatHistory(currentUser.username, token);
          // Map fetched history to the component's message format
          const formattedHistory = history.map(entry => [
            { role: 'user', content: entry.user, timestamp: entry.timestamp },
            { role: 'assistant', content: entry.assistant, timestamp: entry.timestamp }
          ]).flat(); // Flatten the array of pairs
          setMessages(formattedHistory);
        } catch (err) {
          console.error("Lỗi khi tải lịch sử trò chuyện:", err);
          setError("Không thể tải lịch sử trò chuyện.");
          setMessages([]); // Clear messages on error
        } finally {
          setIsLoading(false);
        }
      } else {
        // Clear messages if user logs out
        setMessages([]);
      }
    };
    loadHistory();
  }, [currentUser, token]); // Re-fetch when user or token changes

  // --- Scroll Logic ---
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    // Scroll after messages are updated, especially after loading history
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // --- Textarea Height Adjustment ---
  const adjustTextareaHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'; // Reset chiều cao
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`; // Đặt chiều cao mới
    }
  };

  useEffect(() => {
    adjustTextareaHeight(); // Điều chỉnh khi input thay đổi
  }, [input]);

  // --- Xử lý gửi tin nhắn ---
  // Hàm xử lý format nội dung tin nhắn
  const formatMessage = (content) => {
    // Loại bỏ khoảng trắng thừa và xuống dòng không cần thiết
    let formattedContent = content
      .trim()
      .replace(/\n\s*\n/g, '\n')
      .replace(/```[^`]*```/g, '') // Loại bỏ code blocks
      .replace(/\*\*/g, '') // Loại bỏ markdown bold
      .replace(/\*/g, '') // Loại bỏ markdown italic
      .trim();
      
    // Xử lý danh sách đánh số để hiển thị mỗi mục trên một dòng riêng
    // Tìm các mục danh sách đánh số (1. 2. 3. 4.) và đảm bảo chúng được hiển thị trên các dòng riêng biệt
    formattedContent = formattedContent.replace(/(\d+\.)\s+([^\n]+)(?=\s*(?:\d+\.|$))/g, function(match, number, content) {
      return number + ' ' + content.trim() + '\n';
    });
    
    // Đảm bảo không có dòng trống liên tiếp
    formattedContent = formattedContent.replace(/\n\s*\n/g, '\n');
    
    return formattedContent;
  };

  const handleSend = useCallback(async () => {
    const trimmedInput = input.trim();
    if (!trimmedInput || isLoading) return;

    const userMessage = { role: 'user', content: trimmedInput };
    setMessages(prev => [...prev, userMessage]);
    setInput(''); // Xóa input ngay sau khi gửi
    setIsLoading(true);
    setError(null);

    // Reset chiều cao textarea sau khi gửi
    if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
    }

    try {
      // Hiển thị tin nhắn đang chờ từ assistant
      const loadingMessage = { role: 'assistant', content: 'Đang xử lý...', isLoading: true };
      setMessages(prev => [...prev, loadingMessage]);

      // Pass the token to askQuestion
      const response = await askQuestion(userMessage.content, token);
      console.log('API response:', response); // Ghi log để debug
      const aiContent = formatMessage(response.response || "Xin lỗi, tôi chưa nhận được phản hồi hợp lệ.");

      // Thay thế tin nhắn đang chờ bằng tin nhắn thực tế
      setMessages(prev => prev.map(msg =>
        (msg.isLoading) ? { role: 'assistant', content: aiContent, isTyping: true } : msg
      ));
    } catch (err) {
      console.error("Lỗi khi gửi tin nhắn:", err);
      const errorDetail = err.response?.data?.detail || err.message; // Get more specific error if available
      const errorMessage = errorDetail || 'Đã có lỗi xảy ra khi kết nối tới máy chủ. Vui lòng thử lại.';
      setError(errorMessage);
      
      // Thay thế tin nhắn đang chờ bằng tin nhắn lỗi
      setMessages(prev => prev.map(msg => 
        (msg.isLoading) ? { role: 'assistant', content: `Lỗi: ${errorMessage}`, isError: true } : msg
      )); // End of setMessages call
    } // Add missing closing brace for catch block
    finally {
      setIsLoading(false);
    }
  }, [input, isLoading, token]); // Add token to dependencies

  const handleInputChange = (e) => {
    setInput(e.target.value);
    // Việc điều chỉnh chiều cao đã được xử lý bởi useEffect [input]
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault(); // Ngăn xuống dòng mặc định khi nhấn Enter
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-800 text-white">
      <div className="flex-grow overflow-y-auto p-4 md:p-6 space-y-4 custom-scrollbar">
        <div className="space-y-4">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex animate-fadeIn ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {msg.role === 'assistant' && (
                <div className="flex-shrink-0 w-8 h-8 mr-3 rounded-full bg-blue-600 flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                  </svg>
                </div>
              )}
              <div
                className={`max-w-xl px-4 py-2 rounded-lg shadow-md ${msg.role === 'user' ? 'bg-blue-600 text-white' : msg.isError ? 'bg-red-700 text-white' : msg.isLoading ? 'bg-gray-600 text-gray-200' : 'bg-gray-700 text-gray-200'}`}
              >
                {msg.role === 'assistant' && msg.isTyping ? (
                  <TypeAnimation
                    sequence={[msg.content]}
                    wrapper="pre"
                    speed={50}
                    className="whitespace-pre-wrap font-sans text-sm md:text-base break-words"
                    cursor={false}
                    repeat={1}
                  />
                ) : msg.isLoading ? (
                  <div className="flex items-center">
                    <span className="mr-2">{msg.content}</span>
                    <div className="animate-pulse flex space-x-1">
                      <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
                      <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
                      <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
                    </div>
                  </div>
                ) : (
                  <pre className="whitespace-pre-wrap font-sans text-sm md:text-base break-words">
                    {msg.content}
                  </pre>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
      {/* Khu vực nhập liệu */}
      <div className="p-4 border-t border-gray-700 bg-gray-800">
         {/* Hiển thị lỗi chung nếu có (ngoài tin nhắn lỗi) */}
         {error && !messages.some(msg => msg.isError && msg.content.includes(error)) && (
           <div className="text-red-400 text-sm mb-2 animate-fadeIn">
             {error}
           </div>
         )}

        {/* Input và nút gửi */}
        <div className="flex items-end bg-gray-700 rounded-lg p-2 focus-within:ring-2 focus-within:ring-blue-500">
          <textarea
            ref={textareaRef}
            className="flex-grow bg-transparent text-white placeholder-gray-400 focus:outline-none resize-none overflow-y-auto max-h-40 custom-scrollbar pr-2 text-sm md:text-base"
            rows="1"
            placeholder="Nhập câu hỏi của bạn..."
            value={input}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            style={{ height: 'auto' }} // Cho phép tự động điều chỉnh chiều cao ban đầu
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className={`ml-2 p-2 rounded-lg text-white flex-shrink-0 ${
              isLoading || !input.trim()
                ? 'bg-gray-600 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            } transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-700`}
            aria-label="Gửi tin nhắn"
          >
            {isLoading ? (
              <FiLoader className="h-5 w-5 animate-spin" />
            ) : (
              <FiSend className="h-5 w-5" />
            )}
          </button>
        </div>
         {/* Gợi ý sử dụng Shift + Enter */}
         <p className="text-xs text-gray-400 mt-1 text-center md:text-left">Nhấn Enter để gửi, Shift + Enter để xuống dòng.</p>
      </div>
    </div>
  );
}

export default ChatInterface;
