import React, { useRef, useState } from 'react';
import { Upload, X } from 'lucide-react';

interface UploadAreaProps {
  image: string | null;
  onImageChange: (image: string | null) => void;
}

export function UploadArea({ image, onImageChange }: UploadAreaProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileSelect = (file: File) => {
    if (!file.type.startsWith('image/')) {
      alert('请上传图片文件');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      alert('图片大小不能超过 10MB');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      onImageChange(e.target?.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const file = e.dataTransfer.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleRemove = () => {
    onImageChange(null);
  };

  // 支持粘贴上传
  React.useEffect(() => {
    const handlePaste = (e: ClipboardEvent) => {
      const items = e.clipboardData?.items;
      if (!items) return;

      for (let i = 0; i < items.length; i++) {
        if (items[i].type.startsWith('image/')) {
          const file = items[i].getAsFile();
          if (file) {
            handleFileSelect(file);
          }
          break;
        }
      }
    };

    window.addEventListener('paste', handlePaste);
    return () => window.removeEventListener('paste', handlePaste);
  }, []);

  return (
    <div>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileInput}
        className="hidden"
      />
      
      <div
        onClick={!image ? handleClick : undefined}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          relative h-[300px] rounded-xl border-2 border-dashed transition-all cursor-pointer overflow-hidden
          ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50'}
          ${image ? '' : 'hover:border-blue-400 hover:bg-blue-50/50'}
        `}
      >
        {image ? (
          <>
            <img 
              src={image} 
              alt="Uploaded" 
              className="w-full h-full object-contain"
            />
            <button
              onClick={handleRemove}
              className="absolute top-3 right-3 w-8 h-8 rounded-full bg-red-500 hover:bg-red-600 
                flex items-center justify-center text-white shadow-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </>
        ) : (
          <div className="h-full flex flex-col items-center justify-center gap-3">
            <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center">
              <Upload className="w-8 h-8 text-blue-600" />
            </div>
            <div className="text-center">
              <p className="text-lg font-bold text-gray-700">拖拽图片到这里</p>
              <p className="text-sm text-gray-500 mt-1">或点击选择文件</p>
              <p className="text-xs text-gray-400 mt-2">支持 JPG、PNG，最大 10MB</p>
              <p className="text-xs text-gray-400 mt-1">也可使用 Ctrl+V 粘贴图片</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
