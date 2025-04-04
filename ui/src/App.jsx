import { useState, useRef, useEffect } from "react"; // Giữ lại hooks nếu cần ở đâu đó, hoặc xóa nếu App không dùng trực tiếp
import Sidebar from "./components/Sidebar";
// import ChatWindow from "./components/ChatWindow"; // Xóa import ChatWindow cũ nếu có
import ChatInterface from "./components/ChatInterface"; // *** THÊM IMPORT NÀY ***
import StatsDashboard from "./components/StatsDashboard";
import Tools from "./components/Tools";
import NavBar from "./components/NavBar";
import FileUploader from "./components/FileUploader";
import { BrowserRouter, Routes, Route, Navigate, Link } from "react-router-dom"; // Thêm Link nếu dùng trong FeatureCard
import { TypeAnimation } from "react-type-animation";
// import ScaleLoader from "react-spinners/ScaleLoader"; // Xóa nếu không dùng trực tiếp trong App.jsx (ChatInterface đã import riêng)

// Import images - bạn cần thêm chúng vào thư mục assets
import robotImage from "./assets/robot_image.png"; // Giữ lại nếu dùng ở đâu đó
import avatarImage from "./assets/avatar.jpg"; // Giữ lại nếu dùng ở đâu đó
import edubotLogo from "./assets/edubot-logo.svg";

// --- HomePage Component (Giữ nguyên) ---
const HomePage = () => {
  const [showUploader, setShowUploader] = useState(false);

  return (
    <div className="flex flex-col items-center justify-center h-full text-center p-8">
      <div className="mb-8">
        <img src={edubotLogo} alt="AI Assistant" className="w-40 h-40 mx-auto mb-4 animate-pulse" style={{animationDuration: '3s'}} />
        <TypeAnimation
          sequence={[
            'Welcome to EduMentor AI', 1000,
            'Your intelligent learning assistant', 1000,
            'Ask me anything about your studies', 1000
          ]}
          wrapper="h1"
          speed={50}
          className="text-4xl font-bold mb-6 bg-gradient-to-r from-blue-400 via-blue-500 to-purple-600 bg-clip-text text-transparent"
          repeat={Infinity}
        />
      </div>
      <p className="text-xl text-gray-300 max-w-2xl mb-8 animate-fadeIn" style={{animationDelay: '0.5s'}}>
        Your intelligent learning assistant that helps you understand complex concepts,
        create study materials, and master your subjects more effectively.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full max-w-4xl animate-fadeIn" style={{animationDelay: '0.8s'}}>
        <FeatureCard
          title="Smart Chat"
          description="Ask questions about your learning materials and get intelligent answers"
          icon="chat"
          linkTo="/chat" // Sử dụng Link thay vì <a> nếu muốn SPA navigation
        />
        <FeatureCard
          title="Learning Tools"
          description="Create quizzes, flashcards, mind maps and more"
          icon="tools"
          linkTo="/tools" // Sử dụng Link thay vì <a>
        />
        <FeatureCard
          title="Upload Documents"
          description="Add your learning materials to enhance your experience"
          icon="upload"
          onClick={() => setShowUploader(true)}
        />
      </div>

      {/* Upload Modal */}
      {showUploader && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 rounded-lg w-full max-w-3xl max-h-[90vh] overflow-y-auto custom-scrollbar"> {/* Thêm custom-scrollbar */}
            <div className="sticky top-0 bg-gray-900 flex justify-between items-center p-4 border-b border-gray-700 z-10"> {/* Header modal */}
              <h2 className="text-xl font-bold">Upload Learning Materials</h2>
              <button
                onClick={() => setShowUploader(false)}
                className="text-gray-400 hover:text-white"
                aria-label="Close uploader"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="p-4">
              {/* Đảm bảo FileUploader được import và hoạt động */}
              <FileUploader />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// --- App Component (Đã sửa đổi) ---
function App() {
  // Giữ lại state này để truyền vào ChatInterface
  const [commonQuestions, setCommonQuestions] = useState([
    "Làm thế nào để tạo bài kiểm tra?",
    "Cách tạo flashcard hiệu quả?",
    "Giải thích khái niệm Machine Learning",
    "Tóm tắt nội dung về Neural Networks",
    "Tạo sơ đồ tư duy về Data Science",
    "Lập kế hoạch học tập cho môn Toán",
  ]);

  return (
    <BrowserRouter>
      <div className="flex flex-col h-screen bg-gradient-to-b from-gray-900 to-gray-800 text-white">
        {/* NavBar cố định ở trên cùng */}
        <NavBar />

        {/* Layout chính: Sidebar (desktop) + Content Area */}
        <div className="flex flex-1 overflow-hidden"> {/* Ngăn scroll ở đây */}
          {/* Sidebar chỉ hiển thị trên màn hình lớn */}
          <div className="hidden md:block w-64 flex-shrink-0 bg-gray-900"> {/* Thêm màu nền cho Sidebar */}
            <Sidebar />
          </div>

          {/* Khu vực nội dung chính (chiếm phần còn lại và quản lý scroll nội bộ) */}
          <div className="flex-1 flex flex-col overflow-hidden"> {/* Ngăn scroll ở đây */}
            {/* Phần nội dung chính cho Routes */}
            <main className="flex-1 overflow-hidden"> {/* Cho phép content bên trong tự scroll nếu cần (ChatInterface tự xử lý) */}
              <Routes>
                <Route path="/" element={<HomePage />} />
                {/* *** SỬ DỤNG ChatInterface VÀ TRUYỀN commonQuestions *** */}
                <Route path="/chat" element={<ChatInterface commonQuestions={commonQuestions} />} />
                <Route path="/stats" element={<StatsDashboard />} />
                <Route path="/tools" element={<Tools />} />
                {/* Route mặc định chuyển hướng về trang chủ */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>

            {/* Footer đặt bên ngoài main để không bị ảnh hưởng bởi scroll của main */}
            <footer className="bg-gray-800 bg-opacity-50 text-center text-gray-400 text-xs py-1 border-t border-gray-700 flex-shrink-0"> {/* flex-shrink-0 để footer không bị co lại */}
              <div className="flex items-center justify-center">
                <img src={edubotLogo} alt="EduMentor" className="w-3 h-3 mr-1.5" /> {/* Tăng kích thước logo một chút */}
                <span>EduMentor AI © 2025</span>
              </div>
            </footer>
          </div>
        </div>
      </div>
    </BrowserRouter>
  );
}

// --- FeatureCard Component (Sửa đổi để dùng Link) ---
const FeatureCard = ({ title, description, icon, linkTo, onClick }) => {
  const getIcon = () => {
    // (Giữ nguyên logic getIcon)
    switch (icon) {
      case "chat":
        return (
          <svg className="w-12 h-12 text-blue-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
          </svg>
        );
      case "tools":
        return (
          <svg className="w-12 h-12 text-purple-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z"></path>
          </svg>
        );
      case "upload":
        return (
          <svg className="w-12 h-12 text-green-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
          </svg>
        );
      default: return null;
    }
  };

  const cardContent = (
    <div className="flex flex-col items-center">
      {getIcon()}
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-gray-400 text-center text-sm">{description}</p> {/* Giảm cỡ chữ description */}
    </div>
  );

  // Sử dụng Link của react-router-dom thay vì thẻ <a>
  if (linkTo) {
    return (
      <Link // *** THAY ĐỔI TỪ <a> SANG <Link> ***
        to={linkTo}
        className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-blue-500 hover:shadow-lg hover:shadow-blue-500/20 transition-all duration-300 block transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-900"
      >
        {cardContent}
      </Link>
    );
  }

  // Giữ nguyên div cho trường hợp onClick
  return (
    <div
      className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-blue-500 hover:shadow-lg hover:shadow-blue-500/20 transition-all duration-300 cursor-pointer transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-900"
      onClick={onClick}
      role="button" // Thêm role cho accessibility
      tabIndex={0} // Cho phép focus bằng bàn phím
      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') onClick(); }} // Kích hoạt bằng Enter/Space
    >
      {cardContent}
    </div>
  );
};


// --- XÓA BỎ TOÀN BỘ COMPONENT EnhancedChatWindow ở đây ---


export default App;