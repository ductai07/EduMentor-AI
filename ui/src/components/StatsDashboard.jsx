import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { getStats } from '../services/api';
import { FiBookOpen, FiCalendar, FiCheckCircle, FiClock, FiBriefcase, FiTrendingUp, 
         FiFileText, FiActivity, FiBook, FiX, FiInfo, FiChevronDown, FiChevronUp, FiBarChart2, FiRefreshCw } from 'react-icons/fi';
import { useTool } from '../services/api';

const StatsDashboard = () => {
  const { user, token, isAuthenticated } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [modalContent, setModalContent] = useState(null);
  const [expandedSubject, setExpandedSubject] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  
  // Sử dụng useRef để theo dõi trạng thái tải dữ liệu
  const hasFetchedRef = useRef(false);
  
  // Sử dụng useCallback để tối ưu function fetch dữ liệu
  const fetchStats = useCallback(async (forceRefresh = false) => {
    // Bỏ qua nếu đã tải và không yêu cầu refresh
    if (hasFetchedRef.current && !forceRefresh) {
      return;
    }
    
    // Kiểm tra đăng nhập
    if (!isAuthenticated || !token) {
      setError('Bạn cần đăng nhập để xem thống kê.');
      setLoading(false);
      return;
    }
    
    // Kiểm tra thông tin user
    if (!user || !user.username) {
      console.error("User data missing or incomplete:", user);
      setError('Không thể lấy thông tin người dùng.');
      setLoading(false);
      return;
    }
    
    try {
      if (forceRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      
      setError('');
      console.log(`Fetching stats for: ${user.username} ${forceRefresh ? '(refresh)' : ''}`);
      
      const toolResult = await useTool('stats', user.username);
      
      // Đánh dấu đã fetch
      hasFetchedRef.current = true;
      
      if (toolResult && toolResult.success && toolResult.response) {
        setStats(toolResult.response);
      } else {
        // Thử phương án B: gọi getStats trực tiếp với token
        const response = await getStats(user.username, token);
        if (response) {
          setStats(response);
          hasFetchedRef.current = true;
        } else {
          console.warn("Stats API returned unexpected structure");
          setError('Định dạng dữ liệu không hợp lệ');
        }
      }
    } catch (err) {
      console.error('Error fetching stats:', err);
      
      if (err.response?.status === 401) {
        setError('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.');
      } else {
        const errorMessage = err.response?.data?.detail || 'Không thể tải dữ liệu thống kê.';
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [user, token, isAuthenticated]);
  
  useEffect(() => {
    // Reset flag khi user hoặc token thay đổi
    if (user?.username && token && isAuthenticated) {
      // Chỉ reset nếu đã đổi user
      if (hasFetchedRef.current && stats?.username !== user.username) {
        hasFetchedRef.current = false;
      }
      
      if (!hasFetchedRef.current) {
        fetchStats();
      }
    } else {
      // Nếu không có user hoặc token, đảm bảo UI hiển thị trạng thái phù hợp
      setError('Vui lòng đăng nhập để xem thống kê học tập.');
      setLoading(false);
    }
  }, [fetchStats, user, token, isAuthenticated, stats]);
  
  // Hàm để cập nhật tiến độ cho một môn học
  const handleSubjectProgressUpdate = (subject, newProgress) => {
    if (!stats || !stats.subjects) return;
    
    setStats(prevStats => {
      const updatedSubjects = {
        ...prevStats.subjects,
        [subject]: {
          ...prevStats.subjects[subject],
          progress: newProgress,
          progress_updated_at: new Date().toISOString()
        }
      };
      
      return {
        ...prevStats,
        subjects: updatedSubjects,
        recent_activities: [
          {
            action: 'update_progress',
            subject: subject,
            progress: newProgress,
            timestamp: new Date().toISOString()
          },
          ...(prevStats.recent_activities || []).slice(0, 9) // Giữ tối đa 10 hoạt động
        ]
      };
    });
  };
  
  // Làm mới dữ liệu
  const handleRefresh = () => {
    fetchStats(true);
  };

  // Mở modal với nội dung cụ thể
  const openModal = (content, title) => {
    setModalContent({ content, title });
    setModalOpen(true);
  };

  // Toggle mở rộng/thu gọn thông tin của một môn học
  const toggleSubjectExpand = (subject) => {
    if (expandedSubject === subject) {
      setExpandedSubject(null);
    } else {
      setExpandedSubject(subject);
    }
  };

  // Hiển thị loading
  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500"></div>
        <p className="ml-4 text-gray-400">Đang tải thống kê học tập...</p>
      </div>
    );
  }
  
  // Hiển thị lỗi
  if (error) {
    return (
      <div className="bg-red-900/30 border border-red-700 p-4 rounded-lg my-4">
        <div className="flex items-center justify-between">
          <p className="text-red-400">{error}</p>
          <button 
            onClick={handleRefresh}
            className="bg-red-700 hover:bg-red-600 px-3 py-1 rounded text-sm ml-4"
          >
            Thử lại
          </button>
        </div>
        {(!isAuthenticated || !token) && (
          <p className="text-gray-400 mt-2">
            Nếu bạn đã đăng nhập mà vẫn thấy thông báo này, hãy thử tải lại trang hoặc đăng nhập lại.
          </p>
        )}
      </div>
    );
  }
  
  // Chưa có dữ liệu
  if (!stats) {
    return (
      <div className="bg-gray-800 p-6 rounded-lg my-4">
        <p>Chưa có dữ liệu thống kê học tập.</p>
      </div>
    );
  }

  // Kiểm tra các thuộc tính của stats
  const hasSubjects = stats.subjects && Object.keys(stats.subjects).length > 0;
  const hasRecentActivities = stats.recent_activities && stats.recent_activities.length > 0;
  const hasDocuments = stats.documents && stats.documents.length > 0;
  
  // Hiển thị thống kê
  return (
    <div className="container mx-auto px-4 py-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold flex items-center">
          <FiBarChart2 className="mr-2 text-blue-400" />
          Thống kê học tập của bạn
        </h2>
        <button 
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm"
          title="Làm mới dữ liệu"
        >
          <FiRefreshCw className={`mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          {refreshing ? 'Đang cập nhật...' : 'Cập nhật'}
        </button>
      </div>
      
      {/* Cards thống kê tổng quan - có thể click để xem chi tiết */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {/* Quiz đã hoàn thành */}
        <div 
          className="bg-gray-800 p-6 rounded-lg shadow-lg flex items-center hover:bg-gray-700 transition-colors cursor-pointer"
          onClick={() => openModal(
            stats.completed_quizzes > 0 
              ? <QuizDetails stats={stats} /> 
              : <p>Bạn chưa hoàn thành quiz nào.</p>,
            "Chi tiết Quiz đã hoàn thành"
          )}
        >
          <div className="rounded-full bg-blue-500/20 p-4 mr-4">
            <FiCheckCircle className="text-blue-500 text-2xl" />
          </div>
          <div>
            <h3 className="text-gray-400 font-medium">Quiz đã hoàn thành</h3>
            <p className="text-2xl font-bold">{stats.completed_quizzes || 0}</p>
          </div>
          <div className="ml-auto">
            <FiInfo className="text-gray-400 hover:text-blue-400" />
          </div>
        </div>
        
        {/* Cuộc hội thoại */}
        <div 
          className="bg-gray-800 p-6 rounded-lg shadow-lg flex items-center hover:bg-gray-700 transition-colors cursor-pointer"
          onClick={() => openModal(
            stats.chat_history_count > 0 
              ? <ChatHistory stats={stats} />
              : <p>Bạn chưa có cuộc hội thoại nào.</p>,
            "Lịch sử hội thoại"
          )}
        >
          <div className="rounded-full bg-green-500/20 p-4 mr-4">
            <FiBookOpen className="text-green-500 text-2xl" />
          </div>
          <div>
            <h3 className="text-gray-400 font-medium">Cuộc hội thoại</h3>
            <p className="text-2xl font-bold">{stats.chat_history_count || 0}</p>
          </div>
          <div className="ml-auto">
            <FiInfo className="text-gray-400 hover:text-blue-400" />
          </div>
        </div>
        
        {/* Tài liệu đã tải lên */}
        <div 
          className="bg-gray-800 p-6 rounded-lg shadow-lg flex items-center hover:bg-gray-700 transition-colors cursor-pointer"
          onClick={() => openModal(
            hasDocuments 
              ? <DocumentsList documents={stats.documents} />
              : <p>Bạn chưa tải lên tài liệu nào.</p>,
            "Tài liệu đã tải lên"
          )}
        >
          <div className="rounded-full bg-purple-500/20 p-4 mr-4">
            <FiFileText className="text-purple-500 text-2xl" />
          </div>
          <div>
            <h3 className="text-gray-400 font-medium">Tài liệu đã tải lên</h3>
            <p className="text-2xl font-bold">{stats.total_documents || (hasDocuments ? stats.documents.length : 0)}</p>
          </div>
          <div className="ml-auto">
            <FiInfo className="text-gray-400 hover:text-blue-400" />
          </div>
        </div>
      </div>
      
      {/* Tiến độ môn học - có thể click để mở rộng */}
      {hasSubjects && (
        <div className="mb-8">
          <h3 className="text-xl font-semibold mb-4 flex items-center">
            <FiBook className="mr-2 text-blue-400" />
            Tiến độ môn học
          </h3>
          <div className="bg-gray-800 p-6 rounded-lg shadow-lg divide-y divide-gray-700">
            {Object.entries(stats.subjects).map(([subject, data]) => (
              <div key={subject} className="py-4 first:pt-0 last:pb-0">
                <div 
                  onClick={() => toggleSubjectExpand(subject)}
                  className="flex justify-between items-center mb-2 cursor-pointer hover:bg-gray-700/50 p-2 rounded"
                >
                  <div className="flex items-center">
                    {expandedSubject === subject ? <FiChevronUp className="mr-2 text-blue-400" /> : <FiChevronDown className="mr-2 text-gray-400" />}
                    <span className="font-medium text-lg">{subject}</span>
                  </div>
                  <span className="bg-blue-900/30 px-2 py-1 rounded text-blue-300">{data.progress || 0}%</span>
                </div>
                
                {/* Luôn hiển thị thanh tiến độ */}
                <div className="w-full bg-gray-700 rounded-full h-3 mt-2">
                  <div 
                    className={`${getProgressColorClass(data.progress || 0)} h-3 rounded-full transition-all duration-500`}
                    style={{ width: `${data.progress || 0}%` }}
                  />
                </div>
                
                {/* Chỉ hiển thị chi tiết khi được mở rộng */}
                {expandedSubject === subject && (
                  <div className="mt-3 bg-gray-700/30 p-4 rounded-lg">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="text-sm font-medium text-gray-300 mb-1">Chi tiết môn học</h4>
                        <p className="text-gray-400">{data.description || 'Không có mô tả'}</p>
                        {data.progress_updated_at && (
                          <p className="text-sm text-gray-500 mt-2">
                            Cập nhật lần cuối: {formatDate(data.progress_updated_at)}
                          </p>
                        )}
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-gray-300 mb-1">Phân tích tiến độ</h4>
                        <div className="space-y-1">
                          <p className="text-xs flex items-center">
                            <span className={`inline-block w-3 h-3 rounded-full ${data.progress < 30 ? 'bg-red-500' : 'bg-gray-600'} mr-2`}></span>
                            <span>Bắt đầu (0-30%)</span>
                          </p>
                          <p className="text-xs flex items-center">
                            <span className={`inline-block w-3 h-3 rounded-full ${data.progress >= 30 && data.progress < 70 ? 'bg-yellow-500' : 'bg-gray-600'} mr-2`}></span>
                            <span>Đang tiến triển (30-70%)</span>
                          </p>
                          <p className="text-xs flex items-center">
                            <span className={`inline-block w-3 h-3 rounded-full ${data.progress >= 70 ? 'bg-green-500' : 'bg-gray-600'} mr-2`}></span>
                            <span>Gần hoàn thành (70-100%)</span>
                          </p>
                        </div>
                        
                        <button 
                          className="mt-3 bg-blue-600 hover:bg-blue-700 text-white text-sm px-3 py-1 rounded"
                          onClick={(e) => {
                            e.stopPropagation();
                            openModal(
                              <SubjectDetail 
                                subject={subject} 
                                data={data} 
                                onProgressUpdate={handleSubjectProgressUpdate}
                              />,
                              `Chi tiết môn ${subject}`
                            )
                          }}
                        >
                          Xem đầy đủ
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Hoạt động gần đây */}
      {hasRecentActivities && (
        <div className="mb-8">
          <h3 className="text-xl font-semibold mb-4 flex items-center">
            <FiActivity className="mr-2 text-yellow-400" />
            Hoạt động gần đây
          </h3>
          <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
            <ul className="divide-y divide-gray-700">
              {stats.recent_activities?.slice(0, 5).map((activity, index) => (
                <li key={index} className="py-3 first:pt-0 last:pb-0">
                  <div className="flex items-start">
                    <div className="mr-3 mt-1">
                      {getActivityIcon(activity.action)}
                    </div>
                    <div>
                      <p>{formatActivityMessage(activity)}</p>
                      <p className="text-xs text-gray-400">
                        {activity.timestamp && formatDate(activity.timestamp)}
                      </p>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
            
            {stats.recent_activities?.length > 5 && (
              <button 
                className="mt-4 text-blue-400 hover:text-blue-300 text-sm flex items-center"
                onClick={() => openModal(
                  <ActivitiesList activities={stats.recent_activities} />,
                  "Tất cả hoạt động"
                )}
              >
                Xem tất cả {stats.recent_activities.length} hoạt động
                <FiChevronDown className="ml-1" />
              </button>
            )}
          </div>
        </div>
      )}
      
      {/* Đề xuất học tập */}
      {stats.recommendations && stats.recommendations.length > 0 && (
        <div>
          <h3 className="text-xl font-semibold mb-4 flex items-center">
            <FiTrendingUp className="mr-2 text-yellow-400" />
            Đề xuất học tập
          </h3>
          <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
            <ul className="space-y-3">
              {stats.recommendations.map((rec, index) => (
                <li key={index} className="flex items-start">
                  <FiTrendingUp className="text-yellow-500 mt-1 mr-2 flex-shrink-0" />
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
      
      {/* Modal cho chi tiết */}
      {modalOpen && modalContent && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-lg shadow-xl max-w-3xl w-full max-h-[80vh] flex flex-col">
            <div className="flex items-center justify-between border-b border-gray-700 px-6 py-4">
              <h3 className="text-xl font-bold">{modalContent.title}</h3>
              <button 
                onClick={() => setModalOpen(false)}
                className="text-gray-400 hover:text-white"
              >
                <FiX className="text-xl" />
              </button>
            </div>
            <div className="p-6 overflow-y-auto flex-grow">
              {modalContent.content}
            </div>
            <div className="border-t border-gray-700 p-4 flex justify-end">
              <button 
                onClick={() => setModalOpen(false)}
                className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-md"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Component cho danh sách tài liệu
const DocumentsList = ({ documents }) => (
  <div className="overflow-x-auto">
    <table className="min-w-full divide-y divide-gray-700">
      <thead>
        <tr>
          <th className="px-3 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Tên tài liệu</th>
          <th className="px-3 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Môn học</th>
          <th className="px-3 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Ngày tải lên</th>
          <th className="px-3 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Số trang</th>
        </tr>
      </thead>
      <tbody className="divide-y divide-gray-700">
        {documents.map((doc, index) => (
          <tr key={index} className="hover:bg-gray-700/50">
            <td className="px-3 py-2">{doc.filename || 'N/A'}</td>
            <td className="px-3 py-2">{doc.subject || 'N/A'}</td>
            <td className="px-3 py-2">{doc.upload_date ? formatDate(doc.upload_date) : 'N/A'}</td>
            <td className="px-3 py-2">{doc.page_count || 'N/A'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

// Component cho danh sách hoạt động
const ActivitiesList = ({ activities }) => (
  <div className="space-y-4 max-h-96 overflow-y-auto pr-2">
    {activities.map((activity, index) => (
      <div key={index} className="bg-gray-700/50 p-3 rounded-lg">
        <div className="flex items-start">
          <div className="mr-3 mt-1">
            {getActivityIcon(activity.action)}
          </div>
          <div>
            <p className="font-medium">{formatActivityMessage(activity)}</p>
            <p className="text-xs text-gray-400 mt-1">
              {activity.timestamp && formatDate(activity.timestamp, true)}
            </p>
          </div>
        </div>
      </div>
    ))}
  </div>
);

// Component cho chi tiết quiz
const QuizDetails = ({ stats }) => {
  const quizzes = stats.completed_quizzes_details || [];
  
  return (
    <div>
      <div className="mb-4">
        <p className="text-gray-300">Bạn đã hoàn thành {stats.completed_quizzes || 0} bài kiểm tra.</p>
      </div>
      
      {quizzes.length > 0 ? (
        <div className="space-y-3">
          {quizzes.map((quiz, index) => (
            <div key={index} className="bg-gray-700/50 p-3 rounded">
              <div className="flex justify-between">
                <div className="font-medium">{quiz.quiz_id || `Quiz #${index + 1}`}</div>
                <div className={`px-2 py-1 rounded text-xs ${getScoreColorClass(quiz.score)}`}>
                  {quiz.score}%
                </div>
              </div>
              {quiz.completed_at && (
                <div className="text-xs text-gray-400 mt-1">
                  Hoàn thành: {formatDate(quiz.completed_at, true)}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-400 italic">Không có thông tin chi tiết về các bài quiz.</p>
      )}
    </div>
  );
};

// Component cho chi tiết môn học
const SubjectDetail = ({ subject, data, onProgressUpdate }) => {
  const [editingProgress, setEditingProgress] = useState(false);
  const [progress, setProgress] = useState(data.progress || 0);
  const [updatingProgress, setUpdatingProgress] = useState(false);
  
  const handleProgressChange = (e) => {
    const value = Math.max(0, Math.min(100, parseInt(e.target.value) || 0));
    setProgress(value);
  };
  
  const saveProgress = async () => {
    if (!onProgressUpdate) return;
    
    try {
      setUpdatingProgress(true);
      
      // Giả lập gọi API cập nhật tiến độ
      // Trong thực tế nên gọi API thật ở đây
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Cập nhật UI
      onProgressUpdate(subject, progress);
      
      // Kết thúc chỉnh sửa
      setEditingProgress(false);
    } catch (error) {
      console.error("Error updating progress:", error);
      // Có thể hiển thị thông báo lỗi ở đây
    } finally {
      setUpdatingProgress(false);
    }
  };
  
  return (
    <div>
      <div className="mb-6">
        <h3 className="text-xl font-bold mb-1">{subject}</h3>
        <div className="flex items-center">
          <div className="w-full bg-gray-700 rounded-full h-4 mr-2">
            <div 
              className={`${getProgressColorClass(data.progress || 0)} h-4 rounded-full transition-all duration-500`}
              style={{ width: `${progress}%` }}
            />
          </div>
          <span className="text-lg font-bold">{progress}%</span>
          
          <button 
            className="ml-2 text-blue-400 hover:text-blue-300 p-1 rounded hover:bg-blue-900/30"
            onClick={() => setEditingProgress(!editingProgress)}
            title={editingProgress ? "Hủy" : "Chỉnh sửa tiến độ"}
          >
            {editingProgress ? <FiX /> : <FiInfo />}
          </button>
        </div>
        
        {/* Form chỉnh sửa tiến độ */}
        {editingProgress && (
          <div className="mt-3 bg-blue-900/20 p-3 rounded-lg">
            <label className="text-sm text-gray-300 block mb-1">Cập nhật tiến độ:</label>
            <div className="flex items-center">
              <input 
                type="range" 
                min="0" 
                max="100" 
                value={progress} 
                onChange={handleProgressChange}
                className="flex-1 mr-3"
              />
              <input 
                type="number" 
                min="0" 
                max="100" 
                value={progress} 
                onChange={handleProgressChange}
                className="w-16 bg-gray-700 border border-gray-600 rounded px-2 py-1"
              />
              <span className="text-gray-400 ml-1">%</span>
            </div>
            <div className="flex justify-end mt-3">
              <button
                onClick={() => setEditingProgress(false)}
                className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded mr-2"
                disabled={updatingProgress}
              >
                Hủy
              </button>
              <button 
                onClick={saveProgress}
                disabled={updatingProgress}
                className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded flex items-center"
              >
                {updatingProgress ? 'Đang lưu...' : 'Cập nhật'} 
                {updatingProgress && <FiRefreshCw className="ml-2 animate-spin" />}
              </button>
            </div>
          </div>
        )}
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <h4 className="font-semibold text-gray-300 mb-2">Thông tin môn học</h4>
          <p className="text-gray-400">{data.description || 'Không có mô tả cho môn học này.'}</p>
          {data.progress_updated_at && (
            <p className="text-sm text-gray-500 mt-3">
              Cập nhật lần cuối: {formatDate(data.progress_updated_at, true)}
            </p>
          )}
        </div>
        
        <div>
          <h4 className="font-semibold text-gray-300 mb-2">Tình trạng</h4>
          <div className="space-y-2">
            <div className="flex items-center">
              <div className={`w-3 h-3 rounded-full ${getStatusColorClass(progress)} mr-2`}></div>
              <span>{getStatusText(progress)}</span>
            </div>
            
            <div className="mt-1 text-sm">
              {getProgressAdvice(progress)}
            </div>
          </div>
        </div>
      </div>
      
      {/* Giả lập dữ liệu học tập chi tiết */}
      <div>
        <h4 className="font-semibold text-gray-300 mb-2">Hoạt động gần đây</h4>
        <div className="bg-gray-700/30 rounded-lg p-4">
          <div className="text-gray-400 italic">
            {data.progress > 0 
              ? 'Dữ liệu hoạt động chi tiết sẽ được hiển thị ở đây khi có thêm thông tin.'
              : 'Chưa có hoạt động nào cho môn học này.'}
          </div>
        </div>
      </div>
    </div>
  );
};

// Component cho lịch sử chat
const ChatHistory = ({ stats }) => (
  <div className="text-center text-gray-400">
    <p>Bạn đã có {stats.chat_history_count || 0} cuộc hội thoại với trợ lý.</p>
    <p className="mt-3">Chức năng xem chi tiết lịch sử chat sẽ sớm được cập nhật.</p>
  </div>
);

// Các hàm helper
const getProgressColorClass = (percent) => {
  if (percent < 30) return 'bg-red-500';
  if (percent < 70) return 'bg-yellow-500';
  return 'bg-green-500';
};

const getScoreColorClass = (score) => {
  if (score < 50) return 'bg-red-900/40 text-red-300';
  if (score < 75) return 'bg-yellow-900/40 text-yellow-300';
  return 'bg-green-900/40 text-green-300';
};

const getStatusColorClass = (progress) => {
  if (progress < 30) return 'bg-red-500';
  if (progress < 70) return 'bg-yellow-500';
  if (progress < 100) return 'bg-green-500';
  return 'bg-blue-500';
};

const getStatusText = (progress) => {
  if (progress === 0) return 'Chưa bắt đầu';
  if (progress < 30) return 'Mới bắt đầu';
  if (progress < 70) return 'Đang tiến triển';
  if (progress < 100) return 'Sắp hoàn thành';
  return 'Đã hoàn thành';
};

const getProgressAdvice = (progress) => {
  if (progress === 0) return 'Bạn nên bắt đầu học môn này sớm.';
  if (progress < 30) return 'Hãy tiếp tục nỗ lực để đạt tiến độ cao hơn.';
  if (progress < 70) return 'Bạn đang học tốt, hãy duy trì đều đặn.';
  if (progress < 100) return 'Bạn đã gần hoàn thành, hãy cố gắng hết mình!';
  return 'Chúc mừng bạn đã hoàn thành môn học!';
};

const formatDate = (dateString, showTime = false) => {
  if (!dateString) return 'N/A';
  
  try {
    const date = new Date(dateString);
    
    if (isNaN(date.getTime())) return 'N/A';
    
    const options = {
      year: 'numeric', 
      month: '2-digit', 
      day: '2-digit',
      ...(showTime && { hour: '2-digit', minute: '2-digit' })
    };
    
    return date.toLocaleDateString('vi-VN', options);
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'N/A';
  }
};

const getActivityIcon = (action) => {
  switch (action) {
    case 'upload':
      return <FiFileText className="text-purple-400" />;
    case 'update_progress':
      return <FiActivity className="text-blue-400" />;
    case 'learn':
      return <FiBookOpen className="text-green-400" />;
    case 'create_plan':
      return <FiCalendar className="text-yellow-400" />;
    default:
      return <FiCheckCircle className="text-gray-400" />;
  }
};

const formatActivityMessage = (activity) => {
  switch (activity.action) {
    case 'upload':
      return `Đã tải lên tài liệu "${activity.document || ''}"`
        + (activity.subject ? ` cho môn ${activity.subject}` : '');
    case 'update_progress':
      return `Cập nhật tiến độ môn ${activity.subject || ''}: ${activity.progress || 0}%`;
    case 'learn':
      return `Đã học môn ${activity.subject || ''}` 
        + (activity.duration_minutes ? ` (${activity.duration_minutes} phút)` : '');
    case 'create_plan':
      return `Đã tạo kế hoạch học tập cho môn ${activity.subject || ''}`;
    default:
      return activity.action || 'Hoạt động không xác định';
  }
};

export default StatsDashboard;
