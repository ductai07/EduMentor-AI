/**
 * API Service - Xử lý các yêu cầu HTTP đến backend
 */

const API_BASE_URL = 'http://localhost:5000';

/**
 * Gửi câu hỏi đến API và nhận phản hồi
 * @param {string} question - Câu hỏi của người dùng
 * @returns {Promise<Object>} - Phản hồi từ API
 */
export const askQuestion = async (question) => {
  try {
    const controller = new AbortController();
    // Không đặt timeout cứng, để backend quyết định thời gian phản hồi
    
    const response = await fetch(`${API_BASE_URL}/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question }),
      signal: controller.signal
    });
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Không thể đọc phản hồi lỗi');
      throw new Error(`Lỗi HTTP! Trạng thái: ${response.status}. ${errorText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Lỗi khi gửi câu hỏi:', error);
    if (error.name === 'AbortError') {
      throw new Error('Yêu cầu đã hết thời gian chờ. Vui lòng kiểm tra kết nối mạng và thử lại.');
    }
    throw error;
  }
};

/**
 * Sử dụng công cụ cụ thể (phương thức chung)
 * @param {string} action - Tên công cụ (quiz, flashcards, study_plan, etc.)
 * @param {string} input - Đầu vào cho công cụ
 * @param {string} context - Ngữ cảnh bổ sung (tùy chọn)
 * @param {Object} options - Tùy chọn bổ sung (tùy chọn)
 * @returns {Promise<Object>} - Phản hồi từ API
 * @deprecated Sử dụng các hàm riêng biệt cho từng công cụ thay vì hàm chung này
 */
export const useTool = async (action, input, context = null, options = null) => {
  try {
    const controller = new AbortController();
    // Không đặt timeout cứng, để backend quyết định thời gian phản hồi
    
    const payload = { input };
    if (context) payload.context = context;
    if (options) payload.options = options;

    // Sử dụng endpoint mới /tools/{tool_name} thay vì /tools
    const response = await fetch(`${API_BASE_URL}/tools/${action}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      signal: controller.signal
    });
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Không thể đọc phản hồi lỗi');
      throw new Error(`Lỗi HTTP! Trạng thái: ${response.status}. ${errorText}`);
    }

    const result = await response.json();
    return cleanResponse(result);
  } catch (error) {
    console.error('Lỗi khi sử dụng công cụ:', error);
    if (error.name === 'AbortError') {
      throw new Error('Yêu cầu đã hết thời gian chờ. Vui lòng kiểm tra kết nối mạng và thử lại.');
    }
    throw error;
  }
};

/**
 * Hàm làm sạch dữ liệu trả về từ API
 * @param {Object} response - Dữ liệu trả về từ API
 * @returns {Object} - Dữ liệu đã được làm sạch
 */
const cleanResponse = (response) => {
  if (!response) return null;
  
  // Nếu response có thuộc tính response, lấy giá trị đó
  if (response.response) {
    // Làm sạch dữ liệu nếu là chuỗi
    if (typeof response.response === 'string') {
      // Loại bỏ các ký tự đặc biệt không mong muốn
      let cleanedText = response.response.trim();
      // Loại bỏ các ký tự điều khiển nếu có
      cleanedText = cleanedText.replace(/[\x00-\x1F\x7F-\x9F]/g, '');
      return { ...response, response: cleanedText };
    }
    return response;
  }
  
  // Trường hợp response không có thuộc tính response
  return response;
};

/**
 * Tạo quiz về một chủ đề
 * @param {string} topic - Chủ đề cần tạo quiz
 * @param {Object} options - Tùy chọn bổ sung (tùy chọn)
 * @returns {Promise<Object>} - Phản hồi từ API
 */
export const useQuizTool = async (topic, options = null) => {
  try {
    const controller = new AbortController();
    
    const payload = { input: topic };
    if (options) payload.options = options;

    const response = await fetch(`${API_BASE_URL}/tool/quiz`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      signal: controller.signal
    });
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Không thể đọc phản hồi lỗi');
      throw new Error(`Lỗi HTTP! Trạng thái: ${response.status}. ${errorText}`);
    }

    const result = await response.json();
    return cleanResponse(result);
  } catch (error) {
    console.error('Lỗi khi tạo quiz:', error);
    if (error.name === 'AbortError') {
      throw new Error('Yêu cầu đã hết thời gian chờ. Vui lòng kiểm tra kết nối mạng và thử lại.');
    }
    throw error;
  }
};

/**
 * Tạo flashcard về một chủ đề
 * @param {string} topic - Chủ đề cần tạo flashcard
 * @param {Object} options - Tùy chọn bổ sung (tùy chọn)
 * @returns {Promise<Object>} - Phản hồi từ API
 */
export const useFlashcardTool = async (topic, options = null) => {
  try {
    const controller = new AbortController();
    
    const payload = { input: topic };
    if (options) payload.options = options;

    const response = await fetch(`${API_BASE_URL}/tool/flashcard`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      signal: controller.signal
    });
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Không thể đọc phản hồi lỗi');
      throw new Error(`Lỗi HTTP! Trạng thái: ${response.status}. ${errorText}`);
    }

    const result = await response.json();
    return cleanResponse(result);
  } catch (error) {
    console.error('Lỗi khi tạo flashcard:', error);
    if (error.name === 'AbortError') {
      throw new Error('Yêu cầu đã hết thời gian chờ. Vui lòng kiểm tra kết nối mạng và thử lại.');
    }
    throw error;
  }
};

/**
 * Tạo kế hoạch học tập về một chủ đề
 * @param {string} topic - Chủ đề cần tạo kế hoạch học tập
 * @param {Object} options - Tùy chọn bổ sung (tùy chọn)
 * @returns {Promise<Object>} - Phản hồi từ API
 */
export const useStudyPlanTool = async (topic, options = null) => {
  try {
    const controller = new AbortController();
    
    const payload = { input: topic };
    if (options) payload.options = options;

    const response = await fetch(`${API_BASE_URL}/tool/study_plan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      signal: controller.signal
    });
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Không thể đọc phản hồi lỗi');
      throw new Error(`Lỗi HTTP! Trạng thái: ${response.status}. ${errorText}`);
    }

    const result = await response.json();
    return cleanResponse(result);
  } catch (error) {
    console.error('Lỗi khi tạo kế hoạch học tập:', error);
    if (error.name === 'AbortError') {
      throw new Error('Yêu cầu đã hết thời gian chờ. Vui lòng kiểm tra kết nối mạng và thử lại.');
    }
    throw error;
  }
};

/**
 * Giải thích khái niệm
 * @param {string} concept - Khái niệm cần giải thích
 * @param {Object} options - Tùy chọn bổ sung (tùy chọn)
 * @returns {Promise<Object>} - Phản hồi từ API
 */
export const useConceptTool = async (concept, options = null) => {
  try {
    const controller = new AbortController();
    
    const payload = { input: concept };
    if (options) payload.options = options;

    const response = await fetch(`${API_BASE_URL}/tool/concept`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      signal: controller.signal
    });
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Không thể đọc phản hồi lỗi');
      throw new Error(`Lỗi HTTP! Trạng thái: ${response.status}. ${errorText}`);
    }

    const result = await response.json();
    return cleanResponse(result);
  } catch (error) {
    console.error('Lỗi khi giải thích khái niệm:', error);
    if (error.name === 'AbortError') {
      throw new Error('Yêu cầu đã hết thời gian chờ. Vui lòng kiểm tra kết nối mạng và thử lại.');
    }
    throw error;
  }
};

/**
 * Tạo tóm tắt về một chủ đề
 * @param {string} topic - Chủ đề cần tóm tắt
 * @param {Object} options - Tùy chọn bổ sung (tùy chọn)
 * @returns {Promise<Object>} - Phản hồi từ API
 */
export const useSummaryTool = async (topic, options = null) => {
  try {
    const controller = new AbortController();
    
    const payload = { input: topic };
    if (options) payload.options = options;

    const response = await fetch(`${API_BASE_URL}/tool/summary`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      signal: controller.signal
    });
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Không thể đọc phản hồi lỗi');
      throw new Error(`Lỗi HTTP! Trạng thái: ${response.status}. ${errorText}`);
    }

    const result = await response.json();
    return cleanResponse(result);
  } catch (error) {
    console.error('Lỗi khi tạo tóm tắt:', error);
    if (error.name === 'AbortError') {
      throw new Error('Yêu cầu đã hết thời gian chờ. Vui lòng kiểm tra kết nối mạng và thử lại.');
    }
    throw error;
  }
};

/**
 * Tạo sơ đồ tư duy về một chủ đề
 * @param {string} topic - Chủ đề cần tạo sơ đồ tư duy
 * @param {Object} options - Tùy chọn bổ sung (tùy chọn)
 * @returns {Promise<Object>} - Phản hồi từ API
 */
export const useMindMapTool = async (topic, options = null) => {
  try {
    const controller = new AbortController();
    
    const payload = { input: topic };
    if (options) payload.options = options;

    const response = await fetch(`${API_BASE_URL}/tool/mindmap`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      signal: controller.signal
    });
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Không thể đọc phản hồi lỗi');
      throw new Error(`Lỗi HTTP! Trạng thái: ${response.status}. ${errorText}`);
    }

    const result = await response.json();
    return cleanResponse(result);
  } catch (error) {
    console.error('Lỗi khi tạo sơ đồ tư duy:', error);
    if (error.name === 'AbortError') {
      throw new Error('Yêu cầu đã hết thời gian chờ. Vui lòng kiểm tra kết nối mạng và thử lại.');
    }
    throw error;
  }
};

/**
 * Tải lên tài liệu
 * @param {File} file - File cần tải lên
 * @returns {Promise<Object>} - Phản hồi từ API
 */
export const uploadDocument = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error uploading document:', error);
    throw error;
  }
};

/**
 * Kiểm tra trạng thái API
 * @returns {Promise<Object>} - Phản hồi từ API
 */
export const checkApiStatus = async () => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 giây timeout
    
    const response = await fetch(`${API_BASE_URL}/`, {
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      throw new Error(`Lỗi HTTP! Trạng thái: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Lỗi khi kiểm tra trạng thái API:', error);
    if (error.name === 'AbortError') {
      throw new Error('Không thể kết nối đến máy chủ. Vui lòng kiểm tra xem máy chủ đã được khởi động chưa.');
    }
    throw error;
  }
};