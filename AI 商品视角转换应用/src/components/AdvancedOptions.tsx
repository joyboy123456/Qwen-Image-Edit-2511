import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { GenerationParams, PARAM_RANGES } from '../types';
import { clampSteps, clampCfgScale, filterSeedInput } from '../utils/parameterUtils';

interface AdvancedOptionsProps {
  params: GenerationParams;
  onChange: (params: GenerationParams) => void;
}

export function AdvancedOptions({ params, onChange }: AdvancedOptionsProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  /**
   * Handle steps slider change with value clamping
   * Requirements: 3.3 - Steps slider value synchronization
   */
  const handleStepsChange = (value: number) => {
    onChange({ ...params, steps: clampSteps(value) });
  };

  /**
   * Handle CFG scale slider change with value clamping
   * Requirements: 3.4 - CFG scale slider value synchronization
   */
  const handleCfgScaleChange = (value: number) => {
    onChange({ ...params, cfgScale: clampCfgScale(value) });
  };

  /**
   * Handle seed input change with numeric filtering
   * Requirements: 3.5 - Seed input numeric filtering
   */
  const handleSeedChange = (value: string) => {
    onChange({ ...params, seed: filterSeedInput(value) });
  };

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      {/* 折叠标题栏 */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full h-10 px-4 bg-gray-50 hover:bg-gray-100 
          flex items-center justify-between transition-colors"
      >
        <span className="text-sm font-medium text-gray-700">
          ⚙️ 高级选项
        </span>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 text-gray-500" />
        ) : (
          <ChevronDown className="w-4 h-4 text-gray-500" />
        )}
      </button>

      {/* 展开内容 */}
      {isExpanded && (
        <div className="p-4 space-y-5 bg-white">
          {/* 生成步数 */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-gray-700">
                生成步数
              </label>
              <span className="text-sm font-bold text-blue-600">
                {params.steps}
              </span>
            </div>
            <input
              type="range"
              min={PARAM_RANGES.steps.min}
              max={PARAM_RANGES.steps.max}
              step="1"
              value={params.steps}
              onChange={(e) => handleStepsChange(Number(e.target.value))}
              data-testid="steps-slider"
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer
                [&::-webkit-slider-thumb]:appearance-none
                [&::-webkit-slider-thumb]:w-4
                [&::-webkit-slider-thumb]:h-4
                [&::-webkit-slider-thumb]:rounded-full
                [&::-webkit-slider-thumb]:bg-blue-600
                [&::-webkit-slider-thumb]:cursor-pointer
                [&::-webkit-slider-thumb]:hover:bg-blue-700
                [&::-moz-range-thumb]:w-4
                [&::-moz-range-thumb]:h-4
                [&::-moz-range-thumb]:rounded-full
                [&::-moz-range-thumb]:bg-blue-600
                [&::-moz-range-thumb]:border-0
                [&::-moz-range-thumb]:cursor-pointer"
            />
            <p className="text-xs text-gray-500 mt-1">
              步数越多质量越高，但速度越慢
            </p>
          </div>

          {/* CFG 强度 */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-gray-700">
                CFG 强度
              </label>
              <span className="text-sm font-bold text-blue-600">
                {params.cfgScale.toFixed(1)}
              </span>
            </div>
            <input
              type="range"
              min={PARAM_RANGES.cfgScale.min}
              max={PARAM_RANGES.cfgScale.max}
              step="0.5"
              value={params.cfgScale}
              onChange={(e) => handleCfgScaleChange(Number(e.target.value))}
              data-testid="cfg-scale-slider"
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer
                [&::-webkit-slider-thumb]:appearance-none
                [&::-webkit-slider-thumb]:w-4
                [&::-webkit-slider-thumb]:h-4
                [&::-webkit-slider-thumb]:rounded-full
                [&::-webkit-slider-thumb]:bg-blue-600
                [&::-webkit-slider-thumb]:cursor-pointer
                [&::-webkit-slider-thumb]:hover:bg-blue-700
                [&::-moz-range-thumb]:w-4
                [&::-moz-range-thumb]:h-4
                [&::-moz-range-thumb]:rounded-full
                [&::-moz-range-thumb]:bg-blue-600
                [&::-moz-range-thumb]:border-0
                [&::-moz-range-thumb]:cursor-pointer"
            />
            <p className="text-xs text-gray-500 mt-1">
              控制生成结果与描述的贴合度
            </p>
          </div>

          {/* 随机种子 */}
          <div>
            <label className="text-sm font-medium text-gray-700 block mb-2">
              随机种子（可选）
            </label>
            <input
              type="text"
              value={params.seed}
              onChange={(e) => handleSeedChange(e.target.value)}
              placeholder="留空则随机"
              data-testid="seed-input"
              className="w-full px-3 py-2 rounded-lg border border-gray-300 
                focus:border-blue-500 focus:ring-2 focus:ring-blue-200 focus:outline-none
                text-sm transition-all"
            />
          </div>
        </div>
      )}
    </div>
  );
}
