import { useState, useEffect } from 'react';
import { useTool } from '../services';
import { FiLayers, FiLoader, FiCheck, FiAlertTriangle } from 'react-icons/fi';

const FlashcardGenerator = ({ onSubmit, result, loading, error: parentError }) => {
  const [topic, setTopic] = useState('');
  const [flashcards, setFlashcards] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeCardIndex, setActiveCardIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  
  // Sử dụng kết quả từ component cha nếu có
  useEffect(() => {
    if (result) {
      setFlashcards(parseFlashcards(result));
      setActiveCardIndex(0);
      setShowAnswer(false);
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
    setFlashcards(null);

    try {
      const response = await useTool('flashcard', topic);
      setFlashcards(parseFlashcards(response.response));
      setActiveCardIndex(0);
      setShowAnswer(false);
    } catch (err) {
      console.error('Error creating flashcards:', err);
      setError('Đã xảy ra lỗi khi tạo thẻ ghi nhớ. Vui lòng thử lại sau.');
    } finally {
      setIsLoading(false);
    }
  };

  // Hàm phân tích chuỗi phản hồi thành mảng flashcards
  const parseFlashcards = (responseText) => {
    // Nếu phản hồi đã là đối tượng có thuộc tính flashcards
    if (typeof responseText === 'object' && responseText.flashcards) {
      return responseText.flashcards;
    }

    // Nếu phản hồi là chuỗi, phân tích nó
    const cards = [];
    const lines = responseText.split('\n');
    let currentCard = null;
    let collectingFront = false;
    let collectingBack = false;
    
    // Regex để nhận dạng các dòng đặc biệt
    const flashcardRegex = /FLASHCARD\s+#\d+:?/i;
    const frontRegex = /Mặt\s+trước:?/i;
    const backRegex = /Mặt\s+sau:?/i;
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      // Bỏ qua dòng trống
      if (!line) continue;
      
      // Bắt đầu flashcard mới
      if (flashcardRegex.test(line)) {
        // Lưu flashcard trước đó nếu có
        if (currentCard && currentCard.term && currentCard.definition) {
          cards.push(currentCard);
        }
        
        // Tạo flashcard mới
        currentCard = { term: '', definition: '' };
        collectingFront = false;
        collectingBack = false;
        continue;
      }
      
      // Bắt đầu phần mặt trước
      if (frontRegex.test(line)) {
        collectingFront = true;
        collectingBack = false;
        // Lấy nội dung sau "Mặt trước:" nếu có
        const content = line.replace(frontRegex, '').trim();
        if (content) {
          currentCard.term = content;
        }
        continue;
      }
      
      // Bắt đầu phần mặt sau
      if (backRegex.test(line)) {
        collectingFront = false;
        collectingBack = true;
        // Lấy nội dung sau "Mặt sau:" nếu có
        const content = line.replace(backRegex, '').trim();
        if (content) {
          currentCard.definition = content;
        }
        continue;
      }
      
      // Thu thập nội dung cho mặt trước hoặc mặt sau
      if (collectingFront) {
        currentCard.term += (currentCard.term ? '\n' : '') + line;
      } else if (collectingBack) {
        currentCard.definition += (currentCard.definition ? '\n' : '') + line;
      }
    }
    
    // Thêm flashcard cuối cùng nếu có
    if (currentCard && currentCard.term && currentCard.definition) {
      cards.push(currentCard);
    }
    
    // Nếu không tìm thấy flashcard theo định dạng trên, thử phân tích theo định dạng khác
    if (cards.length === 0) {
      // Thử tìm theo định dạng gạch đầu dòng
      let currentTerm = '';
      let currentDefinition = '';
      
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line.startsWith('- ')) {
          // Lưu flashcard trước đó nếu có
          if (currentTerm && currentDefinition) {
            cards.push({ term: currentTerm, definition: currentDefinition });
            currentDefinition = '';
          }
          // Lấy term mới
          currentTerm = line.substring(2).split(':')[0].trim();
          // Lấy phần định nghĩa (nếu có)
          const defPart = line.split(':').slice(1).join(':').trim();
          currentDefinition = defPart;
        } else if (line && currentTerm) {
          // Thêm vào definition
          currentDefinition += ' ' + line;
        }
      }
      
      // Thêm flashcard cuối cùng
      if (currentTerm && currentDefinition) {
        cards.push({ term: currentTerm, definition: currentDefinition });
      }
    }

    return cards;
  };

  const nextCard = () => {
    if (flashcards && activeCardIndex < flashcards.length - 1) {
      setActiveCardIndex(activeCardIndex + 1);
      setShowAnswer(false);
    }
  };

  const prevCard = () => {
    if (flashcards && activeCardIndex > 0) {
      setActiveCardIndex(activeCardIndex - 1);
      setShowAnswer(false);
    }
  };

  const toggleAnswer = () => {
    setShowAnswer(!showAnswer);
  };

  return (
    <div className="h-full flex flex-col">
      <div className="bg-gray-800 rounded-lg p-6 mb-6">
        <h2 className="text-xl font-bold mb-4 flex items-center">
          <FiLayers className="mr-2" />
          Tạo thẻ ghi nhớ
        </h2>
        <p className="text-gray-300 mb-4">
          Nhập chủ đề bạn muốn tạo thẻ ghi nhớ và hệ thống sẽ tạo các thẻ ghi nhớ dựa trên tài liệu có sẵn.
        </p>
        
        <form onSubmit={handleSubmit} className="mt-4">
          <div className="flex flex-col md:flex-row gap-4">
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Nhập chủ đề (ví dụ: Machine Learning, Neural Networks, etc.)"
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
                  Đang tạo...
                </>
              ) : (
                'Tạo thẻ ghi nhớ'
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

      {isLoading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="flex flex-col items-center">
            <FiLoader className="animate-spin text-4xl text-blue-500 mb-4" />
            <p className="text-gray-300">Đang tạo thẻ ghi nhớ...</p>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex flex-col">
          {flashcards && flashcards.length > 0 ? (
            <div className="flex-1 flex flex-col">
              <div className="mb-4 flex justify-between items-center">
                <h3 className="text-lg font-semibold">Thẻ ghi nhớ: {topic}</h3>
                <div className="text-sm text-gray-400">
                  {activeCardIndex + 1} / {flashcards.length}
                </div>
              </div>
              
              <div className="flex-1 flex flex-col">
                <div className="flex-1 bg-gray-700 rounded-lg overflow-hidden flex flex-col mb-4">
                  <div className="p-6 bg-blue-900/30 border-b border-gray-600">
                    <h4 className="text-xl font-medium text-center">{flashcards[activeCardIndex].term}</h4>
                  </div>
                  
                  {showAnswer ? (
                    <div className="p-6 flex-1 flex items-center justify-center bg-gray-800">
                      <div className="text-gray-200 text-center whitespace-pre-wrap">
                        <div className="prose prose-invert max-w-none">
                          {flashcards[activeCardIndex].definition.split('\n').map((paragraph, idx) => {
                            if (paragraph.trim() === '') return <br key={idx} />;
                            if (paragraph.startsWith('-') || paragraph.match(/^\d+\.\s/)) {
                              return (
                                <div key={idx} className="flex items-start text-left ml-4 mt-2">
                                  <span className="mr-2">{paragraph.startsWith('-') ? '•' : paragraph.match(/^(\d+)\./)[1] + '.'}</span>
                                  <span>{paragraph.replace(/^-\s|^\d+\.\s/, '')}</span>
                                </div>
                              );
                            }
                            return <p key={idx} className="mb-2 text-left">{paragraph}</p>;
                          })}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="p-6 flex-1 flex items-center justify-center bg-gray-800">
                      <button 
                        onClick={toggleAnswer}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white transition-colors"
                      >
                        Hiển thị đáp án
                      </button>
                    </div>
                  )}
                </div>
                
                <div className="flex justify-between">
                  <button
                    onClick={prevCard}
                    disabled={activeCardIndex === 0}
                    className={`px-4 py-2 rounded-lg ${activeCardIndex === 0 ? 'bg-gray-700 text-gray-500 cursor-not-allowed' : 'bg-gray-700 hover:bg-gray-600 text-white'}`}
                  >
                    Trước
                  </button>
                  
                  <button
                    onClick={toggleAnswer}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white"
                  >
                    {showAnswer ? 'Ẩn đáp án' : 'Hiển thị đáp án'}
                  </button>
                  
                  <button
                    onClick={nextCard}
                    disabled={activeCardIndex === flashcards.length - 1}
                    className={`px-4 py-2 rounded-lg ${activeCardIndex === flashcards.length - 1 ? 'bg-gray-700 text-gray-500 cursor-not-allowed' : 'bg-gray-700 hover:bg-gray-600 text-white'}`}
                  >
                    Tiếp theo
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-400">
              <div className="text-center">
                <FiLayers className="text-5xl mb-4 mx-auto opacity-20" />
                <p>Nhập chủ đề và nhấn "Tạo thẻ ghi nhớ" để bắt đầu</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FlashcardGenerator;