import React, { useRef, useEffect, useState } from 'react';
import { Markmap } from 'markmap-view';
import { Transformer } from 'markmap-lib';
import { FiZoomIn, FiZoomOut, FiMaximize2, FiDownload, FiInfo } from 'react-icons/fi';

// Mẫu markdown để sử dụng khi không có dữ liệu hoặc có lỗi
const FALLBACK_MARKDOWN = `# 🧠 Mind Map Mẫu
- 📊 Nhánh 1: Khái niệm chính
  - 📌 Chi tiết 1.1: *Thông tin bổ sung*
  - 🔍 Chi tiết 1.2: **Điểm quan trọng**
- 🛠️ Nhánh 2: Công cụ
  - 📱 Ứng dụng thực tiễn
- 📝 Nhánh 3: Tổng kết`;

// Tạo transformer với các plugin cần thiết
const transformer = new Transformer();

// Hàm tiện ích để tạo ảnh PNG từ SVG
const downloadAsPng = (svg, filename = 'mindmap.png') => {
  const canvas = document.createElement('canvas');
  const svgRect = svg.getBoundingClientRect();
  canvas.width = svgRect.width * 2; // Scale up for better quality
  canvas.height = svgRect.height * 2;
  
  const ctx = canvas.getContext('2d');
  ctx.scale(2, 2); // Higher resolution
  
  // Đặt nền trắng cho màu xuất ra
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  
  // Chuyển đổi SVG thành ảnh
  const data = new XMLSerializer().serializeToString(svg);
  const img = new Image();
  img.onload = () => {
    ctx.drawImage(img, 0, 0);
    // Tạo link tải xuống
    const a = document.createElement('a');
    a.download = filename;
    a.href = canvas.toDataURL('image/png');
    a.click();
  };
  img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(data)));
};

const MindMapViewer = ({ markdown }) => {
  const svgRef = useRef(null);
  const containerRef = useRef(null);
  const mmRef = useRef(null); // Ref to store the Markmap instance
  const [error, setError] = useState(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [debugInfo, setDebugInfo] = useState({
    hasMarkdown: Boolean(markdown),
    markdownLength: markdown?.length || 0,
    svgReady: false,
    renderAttempts: 0
  });

  // Xử lý vào/ra fullscreen
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen().catch(err => {
        console.error(`Lỗi chuyển sang chế độ toàn màn hình:`, err);
      });
    } else {
      document.exitFullscreen();
    }
  };

  // Lắng nghe thay đổi fullscreen
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
      // Điều chỉnh lại kích thước khi vào/ra chế độ toàn màn hình
      if (mmRef.current) {
        setTimeout(() => {
          mmRef.current.fit();
        }, 100);
      }
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, []);

  useEffect(() => {
    // Cập nhật thông tin debug khi markdown thay đổi
    setDebugInfo(prev => ({
      ...prev,
      hasMarkdown: Boolean(markdown),
      markdownLength: markdown?.length || 0,
      renderAttempts: prev.renderAttempts + 1
    }));

    // Nếu không có svg ref, không làm gì cả
    if (!svgRef.current) {
      console.error("MindMapViewer: SVG ref is null");
      setError("Không thể tạo khu vực vẽ mind map");
      return;
    }

    // Reset error state
    setError(null);

    // Ensure previous instance is destroyed if markdown changes
    if (mmRef.current) {
      mmRef.current.destroy();
      mmRef.current = null;
    }

    // Reset SVG content để tránh lỗi
    while (svgRef.current.firstChild) {
      svgRef.current.removeChild(svgRef.current.lastChild);
    }

    // Thêm thuộc tính width và height để đảm bảo SVG hiển thị đúng
    svgRef.current.setAttribute('width', '100%');
    svgRef.current.setAttribute('height', '100%');
    
    try {
      // Sử dụng markdown từ props hoặc fallback nếu không có
      const mdContent = markdown?.trim() || FALLBACK_MARKDOWN;
      
      console.log("MindMapViewer: Rendering markdown:", mdContent.substring(0, 100) + "...");
      
      // Transform Markdown to Markmap data structure
      const { root, features } = transformer.transform(mdContent);

      if (!root) {
        throw new Error("Failed to transform markdown to mind map structure");
      }

      console.log("MindMapViewer: Transformed data:", { 
        rootKeys: Object.keys(root),
        childrenCount: root.children?.length || 0
      });

      // Đánh dấu SVG đã sẵn sàng
      setDebugInfo(prev => ({ ...prev, svgReady: true }));

      // Tùy chỉnh hiển thị các nút nhỏ tượng trưng
      const enhancedOptions = {
        autoFit: true, // Auto fit content on initial render
        color: (node) => {
          // Custom color scheme based on depth & content
          const colors = [
            '#8b5cf6', // Tím - Chủ đề chính 
            '#6366f1', // Tím nhạt - Nhánh chính
            '#ec4899', // Hồng - Nhánh phụ cấp 1
            '#f97316', // Cam - Nhánh phụ cấp 2
            '#14b8a6', // Xanh ngọc - Nhánh phụ cấp 3
            '#06b6d4'  // Xanh dương - Nhánh phụ cấp 4
          ];
          
          // Dùng độ sâu của node để quyết định màu sắc
          const depth = node.depth || 0;
          
          // Nếu node có chứa các ký tự emoji nhất định, ưu tiên màu sắc theo chức năng
          const text = node.data.text || '';
          if (text.includes('💡') || text.includes('🔍') || text.includes('❓')) {
            return '#f59e0b'; // Vàng cho những điểm quan trọng, câu hỏi
          }
          if (text.includes('📊') || text.includes('📈') || text.includes('📉')) {
            return '#10b981'; // Xanh lá cho thống kê, số liệu
          }
          if (text.includes('⚠️') || text.includes('🚫') || text.includes('⛔')) {
            return '#ef4444'; // Đỏ cho cảnh báo, lưu ý
          }
          
          return colors[depth % colors.length];
        },
        paddingX: 16, // Add some padding
        duration: 500, // Animation duration in ms
        maxWidth: 300, // Max width for text content
        nodeFont: (node) => { 
          // Thay đổi font chữ theo cấp độ
          const depth = node.depth || 0;
          if (depth === 0) return 'bold 16px Sans-serif'; // Tiêu đề lớn hơn
          return '14px Sans-serif'; // Font chữ mặc định
        },
        nodeMinHeight: 18, // Chiều cao tối thiểu của node
        spacingVertical: 7, // Khoảng cách dọc giữa các node
        spacingHorizontal: 120, // Khoảng cách ngang giữa các node
        embedGlobalCSS: false, // Tắt nhúng CSS toàn cục để tránh xung đột
        initialExpandLevel: 2, // Mở rộng 2 cấp đầu tiên
        linkShape: 'diagonal', // Hình dạng đường kết nối - diagonal hoặc bracket
        // Các tùy chọn không còn được hỗ trợ trong phiên bản mới
        // richText: true, 
        // lineWidth: (node) => {
        //   const depth = node.depth || 0;
        //   return 2 - Math.min(depth / 5, 0.5);
        // },
      };

      // Tạo instance Markmap với các tùy chọn nâng cao - thêm timeout để đảm bảo DOM đã sẵn sàng
      setTimeout(() => {
        try {
          mmRef.current = Markmap.create(svgRef.current, enhancedOptions, root);
          
          // Đảm bảo map được hiển thị đúng sau khi render
          setTimeout(() => {
            if (mmRef.current) {
              mmRef.current.fit(); // Fit map to view
            }
          }, 100);
          
        } catch (err) {
          console.error("Error creating Markmap instance:", err);
          setError(`Lỗi tạo mind map: ${err.message}`);
        }
      }, 0);

    } catch (error) {
      console.error("Error rendering Markmap:", error);
      setError(`Lỗi hiển thị mind map: ${error.message}`);
    }

    // Cleanup function to destroy Markmap instance on unmount
    return () => {
      if (mmRef.current) {
        mmRef.current.destroy();
        mmRef.current = null;
      }
    };
  }, [markdown]); // Re-run effect when markdown content changes

  // Xử lý phóng to, thu nhỏ
  const handleZoomIn = () => {
    if (mmRef.current) {
      const { scale } = mmRef.current.state;
      mmRef.current.setZoom(scale * 1.25);
    }
  };

  const handleZoomOut = () => {
    if (mmRef.current) {
      const { scale } = mmRef.current.state;
      mmRef.current.setZoom(scale / 1.25);
    }
  };

  // Xử lý tải xuống ảnh PNG
  const handleDownload = () => {
    if (svgRef.current) {
      // Lấy tên chủ đề từ markdown nếu có
      let filename = 'mindmap.png';
      if (markdown) {
        const match = markdown.match(/^#\s*([^\n]+)/);
        if (match && match[1]) {
          // Làm sạch tiêu đề (loại bỏ emoji và ký tự đặc biệt)
          let title = match[1].replace(/[^\p{L}\p{N}\s]/gu, '').trim();
          if (title) filename = `${title.slice(0, 30)}.png`;
        }
      }
      downloadAsPng(svgRef.current, filename);
    }
  };

  // Hiển thị thông tin debug
  const toggleDebugInfo = () => {
    console.log("MindMap Debug Info:", {
      ...debugInfo,
      markdownSample: markdown ? markdown.substring(0, 200) + "..." : "None",
      svgElement: svgRef.current,
      markmapInstance: mmRef.current
    });
    
    // Thông báo đã log debug info
    alert("Đã log thông tin debug vào console. Nhấn F12 để xem.");
  };

  return (
    <div className="w-full h-full flex flex-col" ref={containerRef}>
      {error && (
        <div className="bg-red-900/30 text-red-400 p-3 mb-3 rounded-md border border-red-700 text-sm">
          <p>{error}</p>
          <p className="mt-1 text-xs">
            <button 
              className="text-blue-400 underline" 
              onClick={() => {
                // Thử render lại với markdown mẫu
                setError(null);
                const md = FALLBACK_MARKDOWN;
                const { root } = transformer.transform(md);
                if (mmRef.current) mmRef.current.destroy();
                mmRef.current = Markmap.create(svgRef.current, { autoFit: true }, root);
              }}
            >
              Thử hiển thị mind map mẫu
            </button>
          </p>
        </div>
      )}
      
      <div className="w-full flex-1 border border-gray-700 rounded-lg overflow-hidden bg-gray-800/50 relative">
        {/* Controls - với nhiều nút hơn và tooltip */}
        <div className="absolute top-3 right-3 z-10 bg-gray-800/80 rounded-md p-1.5 flex gap-2 backdrop-blur-sm">
          <button 
            className="bg-purple-600/70 hover:bg-purple-600 text-white p-1.5 rounded flex items-center justify-center" 
            onClick={handleZoomIn}
            title="Phóng to"
          >
            <FiZoomIn size={16} />
          </button>
          <button 
            className="bg-purple-600/70 hover:bg-purple-600 text-white p-1.5 rounded flex items-center justify-center"
            onClick={handleZoomOut}
            title="Thu nhỏ"
          >
            <FiZoomOut size={16} />
          </button>
          <button 
            className="bg-purple-600/70 hover:bg-purple-600 text-white p-1.5 rounded flex items-center justify-center"
            onClick={() => mmRef.current?.fit()}
            title="Khớp với màn hình"
          >
            <FiMaximize2 size={16} />
          </button>
          <button 
            className="bg-green-600/70 hover:bg-green-600 text-white p-1.5 rounded flex items-center justify-center"
            onClick={handleDownload}
            title="Tải xuống dưới dạng ảnh PNG"
          >
            <FiDownload size={16} />
          </button>
          <button 
            className="bg-blue-600/70 hover:bg-blue-600 text-white p-1.5 rounded flex items-center justify-center"
            onClick={toggleDebugInfo}
            title="Hiển thị thông tin debug"
          >
            <FiInfo size={16} />
          </button>
        </div>
        
        {/* SVG container for Markmap - thêm className để đảm bảo hiển thị */}
        <svg 
          ref={svgRef} 
          className="w-full h-full markmap-svg" 
          width="100%" 
          height="100%" 
          viewBox="0 0 800 600"
        />
        
        {/* Help text - cải thiện với thêm thông tin */}
        <div className="absolute bottom-2 left-2 text-xs text-gray-400 bg-gray-800/80 p-1.5 rounded backdrop-blur-sm max-w-xs">
          <p className="mb-1"><strong>Điều khiển:</strong> Kéo để di chuyển | Scroll để phóng to/thu nhỏ</p>
          <p>Click vào nút <span className="inline-block w-2 h-2 bg-purple-400 rounded-full mx-1"></span> để mở rộng/thu gọn nhánh</p>
        </div>
      </div>
    </div>
  );
};

export default MindMapViewer;
