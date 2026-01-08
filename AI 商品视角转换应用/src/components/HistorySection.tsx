import React from 'react';
import { X, Clock, Image as ImageIcon } from 'lucide-react';
import { GenerationResult } from '../types';

/**
 * HistorySection 组件属性接口
 * Requirements: 8.1, 8.2, 8.3, 8.4, 8.5
 */
interface HistorySectionProps {
  /** 历史记录列表（最多 10 条） */
  history: GenerationResult[];
  /** 点击历史项回调 - 恢复结果和参数 */
  onItemClick: (item: GenerationResult) => void;
  /** 删除历史项回调 */
  onDelete: (id: string) => void;
}

/**
 * 将 base64 图片数据转换为完整的 data URL
 */
function toDataUrl(imageData: string): string {
  if (imageData.startsWith('data:')) {
    return imageData;
  }
  return `data:image/png;base64,${imageData}`;
}

/**
 * 计算相对时间显示
 */
function getTimeAgo(timestamp: Date): string {
  const seconds = Math.floor((Date.now() - timestamp.getTime()) / 1000);
  
  if (seconds < 60) return '刚刚';
  if (seconds < 3600) return `${Math.floor(seconds / 60)} 分钟前`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)} 小时前`;
  return `${Math.floor(seconds / 86400)} 天前`;
}

/**
 * 历史记录组件
 * 
 * 功能：
 * - 显示最近 10 条生成记录 (Requirements: 8.1)
 * - 新生成结果添加到列表 (Requirements: 8.2)
 * - 点击历史项加载结果到主显示区 (Requirements: 8.3)
 * - 点击历史项恢复输入参数 (Requirements: 8.4)
 * - 支持删除历史项 (Requirements: 8.5)
 */
export function HistorySection({ history, onItemClick, onDelete }: HistorySectionProps) {
  if (history.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">
      <h2 className="text-base font-bold text-gray-800 mb-4 flex items-center gap-2">
        <Clock className="w-5 h-5" />
        最近生成
        <span className="text-sm font-normal text-gray-500">
          ({history.length} 条记录)
        </span>
      </h2>
      
      <div className="flex gap-4 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
        {history.map((item) => (
          <HistoryItem
            key={item.id}
            item={item}
            onClick={() => onItemClick(item)}
            onDelete={() => onDelete(item.id)}
          />
        ))}
      </div>
    </div>
  );
}

/**
 * 单个历史记录项组件
 */
interface HistoryItemProps {
  item: GenerationResult;
  onClick: () => void;
  onDelete: () => void;
}

function HistoryItem({ item, onClick, onDelete }: HistoryItemProps) {
  const imageCount = item.generatedImages.length;
  // 最多显示 4 张缩略图
  const displayImages = item.generatedImages.slice(0, 4);
  const hasMoreImages = imageCount > 4;

  return (
    <div className="flex-shrink-0 group relative">
      {/* 主容器 - 点击回溯 */}
      <div
        onClick={onClick}
        className="w-[160px] rounded-lg border border-gray-200 overflow-hidden 
          cursor-pointer hover:shadow-lg hover:border-blue-300 transition-all duration-200
          bg-white"
      >
        {/* 多图缩略图网格 */}
        <div className="relative">
          {imageCount === 1 ? (
            // 单图：显示完整图片
            <div className="w-full h-[120px]">
              <img 
                src={toDataUrl(item.generatedImages[0].image)} 
                alt={item.generatedImages[0].perspectiveName}
                className="w-full h-full object-cover"
              />
            </div>
          ) : (
            // 多图：2x2 网格布局
            <div className="grid grid-cols-2 gap-0.5 bg-gray-100">
              {displayImages.map((img, index) => (
                <div 
                  key={`${img.perspectiveId}-${index}`}
                  className="aspect-square relative"
                >
                  <img 
                    src={toDataUrl(img.image)} 
                    alt={img.perspectiveName}
                    className="w-full h-full object-cover"
                  />
                </div>
              ))}
              {/* 如果不足 4 张，用占位符填充 */}
              {displayImages.length < 4 && displayImages.length > 1 && (
                Array.from({ length: 4 - displayImages.length }).map((_, index) => (
                  <div 
                    key={`placeholder-${index}`}
                    className="aspect-square bg-gray-100 flex items-center justify-center"
                  >
                    <ImageIcon className="w-6 h-6 text-gray-300" />
                  </div>
                ))
              )}
            </div>
          )}
          
          {/* 图片数量标签 */}
          <div className="absolute bottom-1 right-1 bg-black/60 text-white text-xs px-1.5 py-0.5 rounded">
            {imageCount} 张
          </div>
          
          {/* 更多图片指示器 */}
          {hasMoreImages && (
            <div className="absolute bottom-1 left-1 bg-blue-500/80 text-white text-xs px-1.5 py-0.5 rounded">
              +{imageCount - 4}
            </div>
          )}
        </div>
        
        {/* 信息区域 */}
        <div className="p-2 space-y-1">
          {/* 视角名称列表 */}
          <p className="text-xs text-gray-700 truncate font-medium">
            {item.selectedPerspectives.map(p => p.name).join(', ')}
          </p>
          
          {/* 时间和参数 */}
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>{getTimeAgo(item.timestamp)}</span>
            <span>{item.params.steps}步 / CFG {item.params.cfgScale}</span>
          </div>
        </div>
      </div>
      
      {/* 删除按钮 - Requirements: 8.5 */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          onDelete();
        }}
        className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-red-500 hover:bg-red-600 
          text-white flex items-center justify-center opacity-0 group-hover:opacity-100 
          transition-opacity shadow-lg z-10"
        title="删除此记录"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}
