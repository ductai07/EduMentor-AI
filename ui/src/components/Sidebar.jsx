import { useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { FiMessageSquare, FiFile } from "react-icons/fi";
import edubotLogo from "../assets/edubot-logo.svg";

const Sidebar = ({ chatHistory = [], handleQuickQuestion }) => {
  const [savedChats, setSavedChats] = useState(() => {
    const saved = localStorage.getItem('chatHistory');
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    localStorage.setItem('chatHistory', JSON.stringify(savedChats));
  }, [savedChats]);

  const deleteChat = (index) => {
    const newChats = [...savedChats];
    newChats.splice(index, 1);
    setSavedChats(newChats);
  };

  const renameChat = (index, newName) => {
    const newChats = [...savedChats];
    newChats[index].title = newName;
    setSavedChats(newChats);
  };

  return (
    <div className="h-full bg-gray-900 text-gray-300 flex flex-col border-r border-gray-800 justify-between shadow-xl">
      <div className="p-4 flex flex-col h-full">
        {/* Logo and Title */}
        <div className="flex items-center mb-6">
          <img src={edubotLogo} alt="EduMentor" className="w-10 h-10 mr-3 animate-pulse" style={{ animationDuration: '3s' }} />
          <div>
            <h2 className="font-bold text-xl bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
              EduMentor AI
            </h2>
            <p className="text-xs text-gray-400">Trợ lý học tập thông minh</p>
          </div>
        </div>

        {/* Chat History Section */}
        <div className="flex-1 overflow-hidden flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <div className="p-1.5 bg-blue-600/20 rounded-lg mr-2">
                <FiMessageSquare className="text-blue-400" />
              </div>
              <h2 className="font-bold bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
                Lịch sử trò chuyện
              </h2>
            </div>
          </div>

          {(!savedChats || savedChats.length === 0) ? (
            <div className="text-sm text-gray-500 p-4 bg-gray-800/50 rounded-lg border border-gray-700 shadow-inner">
              <p className="text-center flex flex-col items-center">
                <FiMessageSquare className="mb-2 text-gray-500" size={20} />
                Chưa có cuộc trò chuyện nào
              </p>
            </div>
          ) : (
            <div className="flex-1 overflow-hidden">
              <div className="flex items-center justify-between text-xs text-gray-500 mb-2">
                <span>{savedChats.length} cuộc trò chuyện</span>
                <button
                  onClick={() => {
                    if (window.confirm('Xóa tất cả lịch sử trò chuyện?')) {
                      setSavedChats([]);
                    }
                  }}
                  className="hover:text-red-400 transition-colors duration-200"
                >
                  Xóa tất cả
                </button>
              </div>
              <div className="space-y-2 overflow-y-auto custom-scrollbar h-[calc(100vh-220px)]">
                {savedChats.map((chat, index) => (
                  <div
                    key={index}
                    className="group flex items-center justify-between p-2 rounded-lg hover:bg-gray-800 transition-all duration-200 border border-gray-800 hover:border-gray-700"
                  >
                    <button
                      onClick={() => handleQuickQuestion(chat.messages[0].content)}
                      className="flex-1 text-left truncate text-sm text-gray-300 hover:text-white transition-colors duration-200"
                    >
                      {chat.title || `Cuộc trò chuyện ${index + 1}`}
                    </button>
                    <div className="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                      <button
                        onClick={() => {
                          const newName = prompt('Nhập tên mới cho cuộc trò chuyện:', chat.title);
                          if (newName) renameChat(index, newName);
                        }}
                        className="p-1 hover:bg-gray-700 rounded-md text-gray-400 hover:text-blue-400 transition-colors duration-200"
                        title="Đổi tên"
                      >
                        <FiFile size={14} />
                      </button>
                      <button
                        onClick={() => {
                          if (window.confirm('Bạn có chắc muốn xóa cuộc trò chuyện này?')) {
                            deleteChat(index);
                          }
                        }}
                        className="p-1 hover:bg-gray-700 rounded-md text-gray-400 hover:text-red-400 transition-colors duration-200"
                        title="Xóa"
                      >
                        ×
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Sidebar;