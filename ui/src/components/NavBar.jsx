import { Link, useLocation } from 'react-router-dom';
import { FiHome, FiMessageSquare, FiBarChart2, FiTool, FiHelpCircle } from "react-icons/fi";
import edubotLogo from "../assets/edubot-logo.svg";

const NavBar = () => {
  const location = useLocation();
  
  const navItems = [
    { path: '/', label: 'Trang chủ', icon: <FiHome /> },
    { path: '/chat', label: 'Trò chuyện', icon: <FiMessageSquare /> },
    { path: '/stats', label: 'Thống kê', icon: <FiBarChart2 /> },
    { path: '/tools', label: 'Công cụ', icon: <FiTool /> },
    { path: '/faq', label: 'FAQs', icon: <FiHelpCircle /> },
  ];

  return (
    <div className="bg-gray-800 border-b border-gray-700 w-full">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo and brand name */}
          <div className="flex items-center">
            <Link to="/" className="flex-shrink-0 flex items-center">
              <img src={edubotLogo} alt="EduMentor" className="w-9 h-9 mr-2" />
              <span className="font-extrabold text-xl bg-gradient-to-r from-blue-400 via-blue-500 to-purple-600 bg-clip-text text-transparent">
                EduMentor AI
              </span>
            </Link>
          </div>

          {/* Desktop navigation */}
          <div className="hidden md:flex items-center">
            <div className="flex space-x-2">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`px-4 py-2 rounded-lg flex items-center transition-all duration-200 ${
                    location.pathname === item.path
                      ? "bg-blue-600 text-white shadow-md transform scale-105"
                      : "text-gray-300 hover:bg-gray-700 hover:text-white"
                  }`}
                >
                  <span className="mr-2">{item.icon}</span>
                  <span className="font-medium">{item.label}</span>
                </Link>
              ))}
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              className="text-gray-300 hover:text-white p-2"
            >
              <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16m-7 6h7"></path>
              </svg>
            </button>
          </div>

          {/* User actions */}
          <div className="hidden md:flex items-center">
            <button className="px-4 py-2 bg-blue-600 rounded-lg hover:bg-blue-700 transition-all duration-200 text-white shadow-md hover:shadow-lg transform hover:scale-105">
              Đăng nhập
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NavBar;