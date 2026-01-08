import React from 'react';
import { Perspective, PRESET_PERSPECTIVES } from '../types';

interface PresetButtonsProps {
  /** 当前选中的视角列表 */
  selectedPerspectives: Perspective[];
  /** 视角选择变化回调 */
  onSelectionChange: (perspectives: Perspective[]) => void;
  /** 兼容旧版单选回调（可选） */
  onSelect?: (preset: string) => void;
}

/**
 * 预设视角按钮组件
 * 支持多选视角，显示选中状态和选中数量
 * Requirements: 2.1, 2.3, 2.4, 2.5, 2.6
 */
export function PresetButtons({ 
  selectedPerspectives, 
  onSelectionChange,
  onSelect 
}: PresetButtonsProps) {
  
  /**
   * 检查视角是否已选中
   */
  const isSelected = (perspective: Perspective): boolean => {
    return selectedPerspectives.some(p => p.id === perspective.id);
  };

  /**
   * 处理视角点击 - 切换选中状态
   * Requirements: 2.3, 2.4
   */
  const handleClick = (perspective: Perspective) => {
    if (isSelected(perspective)) {
      // 取消选中 - Requirements: 2.4
      const newSelection = selectedPerspectives.filter(p => p.id !== perspective.id);
      onSelectionChange(newSelection);
    } else {
      // 添加选中 - Requirements: 2.3
      const newSelection = [...selectedPerspectives, perspective];
      onSelectionChange(newSelection);
      
      // 兼容旧版单选回调
      if (onSelect) {
        onSelect(perspective.prompt);
      }
    }
  };

  /**
   * 全选/取消全选
   */
  const handleSelectAll = () => {
    if (selectedPerspectives.length === PRESET_PERSPECTIVES.length) {
      // 已全选，取消全选
      onSelectionChange([]);
    } else {
      // 全选
      onSelectionChange([...PRESET_PERSPECTIVES]);
    }
  };

  const selectedCount = selectedPerspectives.length;
  const isAllSelected = selectedCount === PRESET_PERSPECTIVES.length;

  return (
    <div>
      {/* 标题和选中数量显示 - Requirements: 2.5 */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-gray-700">
          ⚡ 选择目标视角
        </h3>
        <div className="flex items-center gap-2">
          {/* 选中数量徽章 */}
          {selectedCount > 0 && (
            <span className="px-2 py-0.5 text-xs font-medium bg-blue-100 text-blue-700 rounded-full">
              已选 {selectedCount} 个
            </span>
          )}
          {/* 全选按钮 */}
          <button
            onClick={handleSelectAll}
            className="text-xs text-blue-600 hover:text-blue-800 hover:underline"
          >
            {isAllSelected ? '取消全选' : '全选'}
          </button>
        </div>
      </div>
      
      {/* 视角按钮网格 - Requirements: 2.1, 2.6 */}
      <div className="grid grid-cols-3 gap-3">
        {PRESET_PERSPECTIVES.map((perspective) => {
          const selected = isSelected(perspective);
          return (
            <button
              key={perspective.id}
              onClick={() => handleClick(perspective)}
              title={perspective.prompt}
              className={`
                h-12 px-3 rounded-lg border text-sm font-medium
                transition-all duration-200 hover:scale-[1.02]
                ${selected
                  ? 'bg-blue-600 text-white border-blue-600 shadow-lg ring-2 ring-blue-300'
                  : 'bg-white text-gray-700 border-gray-300 hover:border-blue-500 hover:bg-blue-50'
                }
              `}
              aria-pressed={selected}
              aria-label={`${perspective.name}${selected ? ' (已选中)' : ''}`}
            >
              <span className="mr-1">{perspective.icon}</span>
              {perspective.name}
            </button>
          );
        })}
      </div>
      
      {/* 提示文字 */}
      {selectedCount === 0 && (
        <p className="mt-2 text-xs text-gray-500">
          点击选择一个或多个视角进行批量生成
        </p>
      )}
    </div>
  );
}
