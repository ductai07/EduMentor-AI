import React, { useState, useEffect } from 'react';
import { FiBookOpen, FiTrendingUp, FiClock } from 'react-icons/fi';
import { useNavigate } from 'react-router-dom';

const StudyRecommendations = ({ recentTopics = [], studyHistory = [] }) => {
  const [recommendations, setRecommendations] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    // This would ideally come from your backend AI
    // For now, we'll simulate recommendations based on recent activity
    const generateRecommendations = () => {
      // Sample recommendations based on recent topics
      const topicBasedRecs = recentTopics.map(topic => ({
        type: 'topic',
        title: `Deepen your knowledge of ${topic}`,
        description: `Create a mind map to connect concepts in ${topic}`,
        action: () => navigate('/tools', { state: { tool: 'mind_map', input: topic } }),
        icon: <FiTrendingUp className="text-purple-500" />
      }));

      // Time-based recommendations
      const timeBasedRecs = [
        {
          type: 'review',
          title: 'Time for a review session',
          description: 'Generate a quiz on your recent topics to test your knowledge',
          action: () => navigate('/tools', { state: { tool: 'quiz' } }),
          icon: <FiClock className="text-blue-500" />
        },
        {
          type: 'new',
          title: 'Explore a related topic',
          description: 'Based on your interests, you might enjoy learning about Neural Networks',
          action: () => navigate('/chat', { state: { question: 'Tell me about Neural Networks' } }),
          icon: <FiBookOpen className="text-green-500" />
        }
      ];

      return [...topicBasedRecs, ...timeBasedRecs].slice(0, 3); // Limit to 3 recommendations
    };

    setRecommendations(generateRecommendations());
  }, [recentTopics, studyHistory, navigate]);

  if (recommendations.length === 0) return null;

  return (
    <div className="bg-gray-800 rounded-lg p-5 border border-gray-700 mb-6">
      <h2 className="text-xl font-bold mb-4">Recommended for You</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {recommendations.map((rec, index) => (
          <div 
            key={index}
            onClick={rec.action}
            className="bg-gray-700 hover:bg-gray-600 rounded-lg p-4 cursor-pointer transition-all duration-300 transform hover:scale-105"
          >
            <div className="flex items-center mb-3">
              <div className="p-2 rounded-full bg-gray-800">
                {rec.icon}
              </div>
              <h3 className="ml-3 font-semibold">{rec.title}</h3>
            </div>
            <p className="text-sm text-gray-300">{rec.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StudyRecommendations;