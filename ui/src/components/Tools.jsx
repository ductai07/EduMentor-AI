import { useState } from "react";
import { FiFileText, FiBookOpen, FiMap, FiList, FiCpu, FiLayers, FiClock, FiUpload, FiBarChart2 } from "react-icons/fi";
import FileUploader from "./FileUploader";
import StudyPlanCreator from "./StudyPlanCreator";
import ProgressTracker from "./ProgressTracker";
import FlashcardGenerator from "./FlashcardGenerator";
import ConceptExplainer from "./ConceptExplainer";
import SummaryGenerator from "./SummaryGenerator";
import MindMapCreator from "./MindMapCreator";
import { useTool } from "../services/api";

const Tools = () => {
  const [activeToolId, setActiveToolId] = useState("quiz_generator");

  const tools = [
    { id: "quiz_generator", icon: <FiFileText />, name: "Quiz Generator", description: "Tạo bài kiểm tra từ tài liệu học tập" },
    { id: "flashcard_generator", icon: <FiLayers />, name: "Flashcard Generator", description: "Tạo thẻ ghi nhớ từ khái niệm quan trọng" },
    { id: "study_plan_creator", icon: <FiClock />, name: "Study Plan Creator", description: "Lập kế hoạch học tập hiệu quả" },
    { id: "progress_tracker", icon: <FiBarChart2 />, name: "Progress Tracker", description: "Theo dõi tiến độ học tập" },
    { id: "concept_explainer", icon: <FiBookOpen />, name: "Concept Explainer", description: "Giải thích khái niệm phức tạp" },
    { id: "summary_generator", icon: <FiList />, name: "Summary Generator", description: "Tóm tắt nội dung tài liệu" },
    { id: "mind_map_creator", icon: <FiMap />, name: "Mind Map Creator", description: "Tạo sơ đồ tư duy từ chủ đề" },
  ];

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleToolAction = async (toolId, input) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Chuyển đổi ID công cụ từ UI sang định dạng API
      const toolActionMap = {
        "quiz_generator": "quiz",
        "flashcard_generator": "flashcards",
        "study_plan_creator": "study_plan",
        "progress_tracker": "progress",
        "concept_explainer": "concept",
        "summary_generator": "summary",
        "mind_map_creator": "mindmap"
      };
      
      const action = toolActionMap[toolId];
      if (!action) {
        throw new Error(`Công cụ không được hỗ trợ: ${toolId}`);
      }
      
      // Chuẩn bị input dựa trên loại công cụ
      let processedInput;
      
      // Chuyển đổi tất cả input thành chuỗi để phù hợp với API
      if (typeof input === 'object') {
        // Nếu input là object, chuyển đổi thành chuỗi chủ đề/câu hỏi
        if (input.topic) {
          processedInput = input.topic;
        } else if (input.subject) {
          processedInput = input.subject;
        } else if (input.concept) {
          processedInput = input.concept;
        } else if (input.question) {
          processedInput = input.question;
        } else {
          // Nếu không có các trường trên, sử dụng trường đầu tiên
          const firstKey = Object.keys(input)[0];
          processedInput = input[firstKey] || "";
        }
      } else {
        // Nếu input đã là chuỗi, giữ nguyên
        processedInput = input;
      }
      
      console.log(`Gửi yêu cầu đến API: action=${action}, input=${processedInput}`);
      
      // Sử dụng hàm useTool từ API service với input đã xử lý
      const response = await useTool(action, processedInput);
      
      // Xử lý kết quả từ API một cách nhất quán
      if (response && response.response !== undefined) {
        console.log('Kết quả từ API:', response);
        // Đảm bảo chỉ truyền phần response từ API để tất cả các component con xử lý nhất quán
        setResult(response.response);
      } else {
        console.error('Kết quả API không đúng định dạng:', response);
        setError('Lỗi định dạng dữ liệu từ API');
      }
    } catch (err) {
      console.error('Lỗi khi sử dụng công cụ:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const renderToolContent = (toolId) => {
    // Kiểm tra và log kết quả để debug
    console.log(`Rendering tool ${toolId} with result:`, result);
    console.log('Loading state:', loading);
    console.log('Error state:', error);
    
    switch (toolId) {
      case "quiz_generator":
        return <QuizGenerator 
          onSubmit={(input) => handleToolAction(toolId, input)} 
          result={result} 
          loading={loading} 
          error={error} 
        />;
      case "flashcard_generator":
        return <FlashcardGenerator 
          onSubmit={(topic) => handleToolAction(toolId, topic)} 
          result={result} 
          loading={loading} 
          error={error} 
        />;
      case "study_plan_creator":
        return <StudyPlanCreator 
          onSubmit={(subject) => handleToolAction(toolId, subject)} 
          result={result} 
          loading={loading} 
          error={error} 
        />;
      case "progress_tracker":
        return <ProgressTracker 
          onSubmit={(input) => handleToolAction(toolId, input)} 
          result={result} 
          loading={loading} 
          error={error} 
        />;
      case "concept_explainer":
        return <ConceptExplainer 
          onSubmit={(concept) => handleToolAction(toolId, concept)} 
          result={result} 
          loading={loading} 
          error={error} 
        />;
      case "summary_generator":
        return <SummaryGenerator 
          onSubmit={(topic) => handleToolAction(toolId, topic)} 
          result={result} 
          loading={loading} 
          error={error} 
        />;
      case "mind_map_creator":
        return <MindMapCreator 
          onSubmit={(topic) => handleToolAction(toolId, topic)} 
          result={result} 
          loading={loading} 
          error={error} 
        />;
      default:
        return <div className="flex items-center justify-center h-full text-gray-400">
          <div className="text-center">
            <FiCpu className="text-5xl mb-4 mx-auto opacity-20" />
            <p>Chọn công cụ học tập từ menu bên trái để bắt đầu</p>
          </div>
        </div>;
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-full">
      <div className="lg:col-span-1 bg-gray-800 rounded-lg p-4 overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">Công cụ học tập</h2>
        <div className="space-y-2">
          {tools.map((tool) => (
            <button
              key={tool.id}
              onClick={() => setActiveToolId(tool.id)}
              className={`w-full flex items-center p-3 rounded-lg transition-colors duration-200 ${
                activeToolId === tool.id
                  ? "bg-blue-600 text-white"
                  : "bg-gray-700 text-gray-300 hover:bg-gray-600"
              }`}
            >
              <span className="text-xl mr-3">{tool.icon}</span>
              <div className="text-left">
                <div className="font-medium">{tool.name}</div>
                <div className="text-xs opacity-75">{tool.description}</div>
              </div>
            </button>
          ))}
        </div>
      </div>

      <div className="lg:col-span-3 bg-gray-800 rounded-lg p-6 overflow-y-auto">
        {renderToolContent(activeToolId)}
      </div>
    </div>
  );
};

// Placeholder components for each tool
const QuizGenerator = ({ onSubmit }) => {
  const [topic, setTopic] = useState("");
  const [numQuestions, setNumQuestions] = useState(5);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!topic.trim()) return;
    
    setIsLoading(true);
    setResult(null);
    setError(null);
    
    try {
      if (onSubmit) {
        // Sử dụng hàm onSubmit từ props
        const input = { topic, num_questions: numQuestions };
        onSubmit(input);
      } else {
        // Gọi API trực tiếp nếu không có onSubmit
        const response = await fetch("http://localhost:5000/tools", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            action: "quiz",
            input: {
              topic: topic,
              num_questions: numQuestions
            }
          }),
        });
        
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        
        const data = await response.json();
        setResult(data.response);
      }
    } catch (err) {
      console.error("Error creating quiz:", err);
      setError("Đã xảy ra lỗi khi tạo quiz. Vui lòng thử lại sau.");
    } finally {
      setIsLoading(false);
    }
  };
  
  const renderQuiz = () => {
    if (!result) {
      console.log('Không có kết quả để hiển thị');
      return null;
    }
    
    console.log('Đang xử lý kết quả quiz:', result);
    
    // Xử lý kết quả dựa trên cấu trúc dữ liệu
    let questions = [];
    let displayText = '';
    
    // Xử lý các trường hợp khác nhau của kết quả
    if (typeof result === 'object' && result !== null) {
      console.log('Kết quả là object');
      // Nếu result là đối tượng có thuộc tính questions
      if (result.questions) {
        questions = result.questions;
      } else if (result.response) {
        // Nếu result có thuộc tính response
        if (typeof result.response === 'string') {
          displayText = result.response;
        } else if (typeof result.response === 'object' && result.response.questions) {
          questions = result.response.questions;
        } else {
          displayText = JSON.stringify(result.response, null, 2);
        }
      } else {
        // Nếu không có cấu trúc rõ ràng, hiển thị toàn bộ object
        displayText = JSON.stringify(result, null, 2);
      }
    } else if (typeof result === 'string') {
      console.log('Kết quả là string');
      // Nếu result là chuỗi, thử phân tích nó
      try {
        // Thử phân tích chuỗi JSON
        const parsedResult = JSON.parse(result);
        if (parsedResult.questions) {
          questions = parsedResult.questions;
        } else {
          // Nếu không có thuộc tính questions, hiển thị chuỗi gốc
          displayText = result;
        }
      } catch (e) {
        console.log('Không thể parse chuỗi JSON:', e);
        // Nếu không phải JSON, xử lý như văn bản thông thường
        displayText = result;
      }
    } else {
      console.log('Kết quả có kiểu dữ liệu không xác định:', typeof result);
      // Trường hợp khác, chuyển đổi thành chuỗi
      displayText = String(result);
    }
    
    // Nếu không có questions hoặc questions rỗng, hiển thị văn bản với định dạng cải thiện
    if (questions.length === 0) {
      return (
        <div className="mt-6 p-4 bg-gray-700 rounded-lg">
          <h3 className="text-xl font-bold mb-4">Quiz của bạn</h3>
          <div className="whitespace-pre-wrap text-gray-300 prose prose-invert max-w-none">
            {displayText.split('\n').map((paragraph, idx) => {
              if (paragraph.trim() === '') return <br key={idx} />;
              if (paragraph.startsWith('#')) {
                return <h4 key={idx} className="font-bold mt-4">{paragraph.replace(/^#+\s/, '')}</h4>;
              }
              if (paragraph.startsWith('-') || paragraph.match(/^\d+\.\s/)) {
                return (
                  <div key={idx} className="flex items-start ml-4 mt-2">
                    <span className="mr-2">{paragraph.startsWith('-') ? '•' : paragraph.match(/^(\d+)\./)[1] + '.'}</span>
                    <span>{paragraph.replace(/^-\s|^\d+\.\s/, '')}</span>
                  </div>
                );
              }
              return <p key={idx} className="mb-2">{paragraph}</p>;
            })}
          </div>
        </div>
      );
    }
    
    return (
      <div className="mt-6 p-4 bg-gray-700 rounded-lg">
        <h3 className="text-xl font-bold mb-4">Quiz của bạn</h3>
        <div className="space-y-4">
          {questions.map((question, index) => (
            <div key={index} className="p-3 bg-gray-800 rounded-lg">
              <p className="font-medium mb-3">{index + 1}. {question.question}</p>
              <div className="ml-4 space-y-2">
                {question.options.map((option, optIndex) => (
                  <div key={optIndex} className="flex items-start mb-2">
                    <div className={`px-2 py-1 mr-3 rounded-full text-xs ${question.answer === optIndex ? 'bg-green-900 text-green-300' : 'bg-gray-700 text-gray-300'}`}>
                      {String.fromCharCode(65 + optIndex)}
                    </div>
                    <p className={`${question.answer === optIndex ? 'text-green-300' : ''} flex-1`}>{option}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };
  
  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Quiz Generator</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-gray-400 mb-2">Chủ đề</label>
          <input 
            type="text" 
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Nhập chủ đề (ví dụ: Machine Learning)" 
            className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white" 
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-400 mb-2">Số lượng câu hỏi</label>
          <select 
            value={numQuestions}
            onChange={(e) => setNumQuestions(Number(e.target.value))}
            className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white"
          >
            <option value={5}>5</option>
            <option value={10}>10</option>
            <option value={15}>15</option>
            <option value={20}>20</option>
          </select>
        </div>
        <button 
          type="submit"
          disabled={isLoading || !topic.trim()}
          className={`px-4 py-2 rounded-lg transition ${isLoading || !topic.trim() ? 'bg-gray-600 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 text-white'}`}
        >
          {isLoading ? 'Đang tạo...' : 'Tạo Quiz'}
        </button>
      </form>
      
      {result && renderQuiz()}
      
      {error && (
        <div className="mt-4 p-3 bg-red-900/50 text-red-300 rounded-lg">
          <div className="font-bold mb-1">Lỗi:</div>
          <div>{error}</div>
        </div>
      )}
      
      {/* Hiển thị thông tin debug khi không có kết quả nhưng không có lỗi */}
      {!result && !error && !isLoading && topic.trim() && (
        <div className="mt-4 p-3 bg-blue-900/50 text-blue-300 rounded-lg">
          <div className="font-bold mb-1">Thông tin:</div>
          <div>Đã gửi yêu cầu nhưng chưa nhận được kết quả. Vui lòng kiểm tra kết nối mạng và thử lại.</div>
        </div>
      )}
    </div>
  );
};

// Các component đã được chuyển thành component riêng biệt



// Đã được chuyển thành component riêng biệt

// Đã được chuyển thành component riêng biệt

// Đã được chuyển thành component riêng biệt

// Đã được chuyển thành component riêng biệt

export default Tools;