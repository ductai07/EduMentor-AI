import { useState, useEffect } from "react";
import { FiCalendar, FiClock, FiBarChart2, FiPieChart, FiTrendingUp, FiPlus, FiX } from "react-icons/fi";
import { Bar, Pie, Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const StatsDashboard = () => {
  const [timeRange, setTimeRange] = useState("week");
  const [schedules, setSchedules] = useState([]);
  const [progressData, setProgressData] = useState({
    labels: ["T2", "T3", "T4", "T5", "T6", "T7", "CN"],
    datasets: [
      {
        label: "Số câu hỏi",
        data: [],
        backgroundColor: "rgba(54, 162, 235, 0.5)",
        borderColor: "rgba(54, 162, 235, 1)",
        borderWidth: 2,
        tension: 0.3,
        fill: true,
      },
    ],
  });
  const [showAddSchedule, setShowAddSchedule] = useState(false);
  const [showAddProgress, setShowAddProgress] = useState(false);
  const [newSchedule, setNewSchedule] = useState({
    title: "",
    date: "",
    startTime: "",
    endTime: "",
    color: "blue"
  });
  const [newProgress, setNewProgress] = useState({
    day: "T2",
    count: 0
  });

  // Sample data for charts
 

  // Load saved data from localStorage on component mount
  useEffect(() => {
    const savedSchedules = localStorage.getItem('eduMentorSchedules');
    const savedProgress = localStorage.getItem('eduMentorProgress');
    
    if (savedSchedules) {
      setSchedules(JSON.parse(savedSchedules));
    }
    
    if (savedProgress) {
      setProgressData(JSON.parse(savedProgress));
    }
  }, []);

  // Save data to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('eduMentorSchedules', JSON.stringify(schedules));
  }, [schedules]);

  useEffect(() => {
    localStorage.setItem('eduMentorProgress', JSON.stringify(progressData));
  }, [progressData]);

  const handleAddSchedule = (e) => {
    e.preventDefault();
    if (!newSchedule.title || !newSchedule.date || !newSchedule.startTime || !newSchedule.endTime) {
      return;
    }

    const formattedDate = new Date(newSchedule.date).toLocaleDateString('vi-VN');
    const timeString = `${formattedDate}, ${newSchedule.startTime} - ${newSchedule.endTime}`;
    
    const newScheduleItem = {
      ...newSchedule,
      id: Date.now(),
      timeString: timeString
    };
    
    setSchedules([...schedules, newScheduleItem]);
    setNewSchedule({ title: "", date: "", startTime: "", endTime: "", color: "blue" });
    setShowAddSchedule(false);
  };

  const handleAddProgress = (e) => {
    e.preventDefault();
    if (!newProgress.day || !newProgress.count || isNaN(newProgress.count)) {
      return;
    }

    const updatedData = { ...progressData };
    const dayIndex = updatedData.labels.indexOf(newProgress.day);
    
    if (dayIndex !== -1) {
      updatedData.datasets[0].data[dayIndex] = parseInt(newProgress.count);
      setProgressData(updatedData);
    }
    
    setNewProgress({ day: "T2", count: 0 });
    setShowAddProgress(false);
  };

  const removeSchedule = (id) => {
    setSchedules(schedules.filter(schedule => schedule.id !== id));
  };

  // Chart options
  const barOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
        labels: {
          color: "#e5e7eb",
        },
      },
    },
    scales: {
      y: {
        ticks: {
          color: "#9ca3af",
        },
        grid: {
          color: "rgba(75, 85, 99, 0.2)",
        },
      },
      x: {
        ticks: {
          color: "#9ca3af",
        },
        grid: {
          color: "rgba(75, 85, 99, 0.2)",
        },
      },
    },
  };

  const lineOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
        labels: {
          color: "#e5e7eb",
        },
      },
    },
    scales: {
      y: {
        ticks: {
          color: "#9ca3af",
        },
        grid: {
          color: "rgba(75, 85, 99, 0.2)",
        },
      },
      x: {
        ticks: {
          color: "#9ca3af",
        },
        grid: {
          color: "rgba(75, 85, 99, 0.2)",
        },
      },
    },
  };

  const pieOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
        labels: {
          color: "#e5e7eb",
        },
      },
    },
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Thống kê học tập</h2>
        <div className="flex space-x-2">
          <button
            onClick={() => setTimeRange("week")}
            className={`px-3 py-1 rounded-lg ${
              timeRange === "week"
                ? "bg-blue-600 text-white"
                : "bg-gray-700 text-gray-300 hover:bg-gray-600"
            }`}
          >
            Tuần
          </button>
          <button
            onClick={() => setTimeRange("month")}
            className={`px-3 py-1 rounded-lg ${
              timeRange === "month"
                ? "bg-blue-600 text-white"
                : "bg-gray-700 text-gray-300 hover:bg-gray-600"
            }`}
          >
            Tháng
          </button>
          <button
            onClick={() => setTimeRange("year")}
            className={`px-3 py-1 rounded-lg ${
              timeRange === "year"
                ? "bg-blue-600 text-white"
                : "bg-gray-700 text-gray-300 hover:bg-gray-600"
            }`}
          >
            Năm
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-800 rounded-lg p-4 shadow-lg">
          <div className="flex items-center mb-4">
            <FiClock className="text-blue-400 text-xl mr-2" />
            <h3 className="text-lg font-semibold">Tổng thời gian học</h3>
          </div>
          <div className="text-3xl font-bold">24 giờ</div>
          <div className="text-green-400 text-sm flex items-center mt-2">
            <FiTrendingUp className="mr-1" /> +12% so với tuần trước
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4 shadow-lg">
          <div className="flex items-center mb-4">
            <FiBarChart2 className="text-purple-400 text-xl mr-2" />
            <h3 className="text-lg font-semibold">Số câu hỏi đã trả lời</h3>
          </div>
          <div className="text-3xl font-bold">98</div>
          <div className="text-green-400 text-sm flex items-center mt-2">
            <FiTrendingUp className="mr-1" /> +8% so với tuần trước
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4 shadow-lg">
          <div className="flex items-center mb-4">
            <FiPieChart className="text-green-400 text-xl mr-2" />
            <h3 className="text-lg font-semibold">Tỷ lệ đúng Quiz</h3>
          </div>
          <div className="text-3xl font-bold">75%</div>
          <div className="text-green-400 text-sm flex items-center mt-2">
            <FiTrendingUp className="mr-1" /> +5% so với tuần trước
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-4 shadow-lg">
          <h3 className="text-lg font-semibold mb-4">Thời gian học theo chủ đề</h3>
          <div className="h-64">
            <Bar data={subjectData} options={barOptions} />
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4 shadow-lg">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold">Tiến độ học tập</h3>
            <button 
              onClick={() => setShowAddProgress(!showAddProgress)}
              className="p-1 bg-blue-600 rounded-full text-white hover:bg-blue-700"
            >
              <FiPlus size={18} />
            </button>
          </div>
          
          {showAddProgress && (
            <form onSubmit={handleAddProgress} className="mb-4 p-3 bg-gray-700 rounded-lg">
              <div className="grid grid-cols-2 gap-2 mb-2">
                <div>
                  <label className="block text-sm text-gray-300 mb-1">Ngày</label>
                  <select 
                    value={newProgress.day}
                    onChange={(e) => setNewProgress({...newProgress, day: e.target.value})}
                    className="w-full p-2 bg-gray-800 rounded text-white border border-gray-600"
                  >
                    {["T2", "T3", "T4", "T5", "T6", "T7", "CN"].map(day => (
                      <option key={day} value={day}>{day}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-gray-300 mb-1">Số câu hỏi</label>
                  <input 
                    type="number" 
                    value={newProgress.count}
                    onChange={(e) => setNewProgress({...newProgress, count: e.target.value})}
                    className="w-full p-2 bg-gray-800 rounded text-white border border-gray-600"
                    min="0"
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-2">
                <button 
                  type="button"
                  onClick={() => setShowAddProgress(false)}
                  className="px-3 py-1 bg-gray-600 text-white rounded hover:bg-gray-500"
                >
                  Hủy
                </button>
                <button 
                  type="submit"
                  className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Lưu
                </button>
              </div>
            </form>
          )}
          
          {progressData.datasets[0].data.length > 0 ? (
            <div className="h-64">
              <Line data={progressData} options={lineOptions} />
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center flex-col text-gray-400">
              <FiBarChart2 size={40} className="mb-2" />
              <p>Chưa có dữ liệu tiến độ</p>
              <p className="text-sm">Nhấn nút + để thêm dữ liệu tiến độ học tập</p>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-gray-800 rounded-lg p-4 shadow-lg">
          <h3 className="text-lg font-semibold mb-4">Kết quả Quiz</h3>
          <div className="h-64 flex items-center justify-center">
            <Pie data={quizData} options={pieOptions} />
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4 shadow-lg col-span-2">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold">Lịch học gần đây</h3>
            <button 
              onClick={() => setShowAddSchedule(!showAddSchedule)}
              className="p-1 bg-blue-600 rounded-full text-white hover:bg-blue-700"
            >
              <FiPlus size={18} />
            </button>
          </div>
          
          {showAddSchedule && (
            <form onSubmit={handleAddSchedule} className="mb-4 p-3 bg-gray-700 rounded-lg">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                <div>
                  <label className="block text-sm text-gray-300 mb-1">Tiêu đề</label>
                  <input 
                    type="text" 
                    value={newSchedule.title}
                    onChange={(e) => setNewSchedule({...newSchedule, title: e.target.value})}
                    className="w-full p-2 bg-gray-800 rounded text-white border border-gray-600"
                    placeholder="Tên môn học"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-300 mb-1">Ngày</label>
                  <input 
                    type="date" 
                    value={newSchedule.date}
                    onChange={(e) => setNewSchedule({...newSchedule, date: e.target.value})}
                    className="w-full p-2 bg-gray-800 rounded text-white border border-gray-600"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-300 mb-1">Giờ bắt đầu</label>
                  <input 
                    type="time" 
                    value={newSchedule.startTime}
                    onChange={(e) => setNewSchedule({...newSchedule, startTime: e.target.value})}
                    className="w-full p-2 bg-gray-800 rounded text-white border border-gray-600"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-300 mb-1">Giờ kết thúc</label>
                  <input 
                    type="time" 
                    value={newSchedule.endTime}
                    onChange={(e) => setNewSchedule({...newSchedule, endTime: e.target.value})}
                    className="w-full p-2 bg-gray-800 rounded text-white border border-gray-600"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-300 mb-1">Màu sắc</label>
                  <select 
                    value={newSchedule.color}
                    onChange={(e) => setNewSchedule({...newSchedule, color: e.target.value})}
                    className="w-full p-2 bg-gray-800 rounded text-white border border-gray-600"
                  >
                    <option value="blue">Xanh dương</option>
                    <option value="purple">Tím</option>
                    <option value="green">Xanh lá</option>
                    <option value="red">Đỏ</option>
                    <option value="yellow">Vàng</option>
                  </select>
                </div>
              </div>
              <div className="flex justify-end space-x-2">
                <button 
                  type="button"
                  onClick={() => setShowAddSchedule(false)}
                  className="px-3 py-1 bg-gray-600 text-white rounded hover:bg-gray-500"
                >
                  Hủy
                </button>
                <button 
                  type="submit"
                  className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Lưu
                </button>
              </div>
            </form>
          )}
          
          {schedules.length > 0 ? (
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {schedules.map(schedule => (
                <div key={schedule.id} className="flex items-center p-3 bg-gray-700 rounded-lg">
                  <div className={`p-2 bg-${schedule.color}-600 rounded-lg mr-3`}>
                    <FiCalendar />
                  </div>
                  <div className="flex-1">
                    <div className="font-medium">{schedule.title}</div>
                    <div className="text-sm text-gray-400">{schedule.timeString}</div>
                  </div>
                  <button 
                    onClick={() => removeSchedule(schedule.id)} 
                    className="text-gray-400 hover:text-red-400"
                    aria-label="Remove schedule"
                  >
                    <FiX />
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="h-48 flex items-center justify-center flex-col text-gray-400">
              <FiCalendar size={40} className="mb-2" />
              <p>Chưa có lịch học nào</p>
              <p className="text-sm">Nhấn nút + để thêm lịch học mới</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StatsDashboard;