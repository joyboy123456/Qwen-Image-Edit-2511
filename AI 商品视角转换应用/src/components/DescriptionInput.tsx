import React from 'react';

interface DescriptionInputProps {
  value: string;
  onChange: (value: string) => void;
}

export function DescriptionInput({ value, onChange }: DescriptionInputProps) {
  const maxLength = 200;

  return (
    <div>
      <h3 className="text-base font-bold text-gray-800 mb-3">
        ✏️ 描述你想要的视角
      </h3>
      <div className="relative">
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value.slice(0, maxLength))}
          placeholder="例如：将镜头向左旋转 45 度，或者从上方俯视拍摄"
          className="w-full h-[120px] px-4 py-3 rounded-lg border border-gray-300 
            focus:border-blue-500 focus:ring-2 focus:ring-blue-200 focus:outline-none
            resize-none transition-all"
        />
        <div className="absolute bottom-3 right-3 text-xs text-gray-400">
          {value.length}/{maxLength}
        </div>
      </div>
    </div>
  );
}
