import React, { useState } from 'react';
import { Download, RefreshCw, Heart, Image as ImageIcon, ZoomIn, X, Package } from 'lucide-react';
import { GenerationResult, GeneratedImage } from '../types';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';

/**
 * ResultDisplay 组件属性接口
 * Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7
 */
interface ResultDisplayProps {
  /** 生成结果（新格式，支持多图） */
  result: GenerationResult | null;
  /** 下载回调 */
  onDownload: () => void;
  /** 重新生成回调 */
  onRegenerate: () => void;
  /** 收藏回调 */
  onFavorite: () => void;
}

/**
 * 图片预览模态框状态
 */
interface PreviewState {
  isOpen: boolean;
  image: GeneratedImage | null;
  isOriginal: boolean;
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
 * 下载单张图片
 * Requirements: 7.5, 7.7
 */
function downloadImage(imageData: string, filename: string): void {
  const link = document.createElement('a');
  link.href = toDataUrl(imageData);
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

/**
 * 将 base64 转换为 Blob
 */
function base64ToBlob(base64: string, mimeType: string = 'image/png'): Blob {
  const base64Data = base64.replace(/^data:image\/\w+;base64,/, '');
  const byteCharacters = atob(base64Data);
  const byteNumbers = new Array(byteCharacters.length);
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  const byteArray = new Uint8Array(byteNumbers);
  return new Blob([byteArray], { type: mimeType });
}

/**
 * 简单的 ZIP 文件创建器（不依赖外部库）
 * 使用 ZIP 文件格式规范创建基本的 ZIP 文件
 */
class SimpleZip {
  private files: { name: string; data: Uint8Array }[] = [];

  addFile(name: string, data: Uint8Array): void {
    this.files.push({ name, data });
  }

  generate(): Blob {
    const encoder = new TextEncoder();
    const parts: Uint8Array[] = [];
    const centralDirectory: Uint8Array[] = [];
    let offset = 0;

    // 写入每个文件
    for (const file of this.files) {
      const nameBytes = encoder.encode(file.name);
      
      // Local file header
      const localHeader = new Uint8Array(30 + nameBytes.length);
      const view = new DataView(localHeader.buffer);
      
      view.setUint32(0, 0x04034b50, true); // Local file header signature
      view.setUint16(4, 20, true); // Version needed to extract
      view.setUint16(6, 0, true); // General purpose bit flag
      view.setUint16(8, 0, true); // Compression method (stored)
      view.setUint16(10, 0, true); // File last modification time
      view.setUint16(12, 0, true); // File last modification date
      view.setUint32(14, 0, true); // CRC-32 (0 for simplicity)
      view.setUint32(18, file.data.length, true); // Compressed size
      view.setUint32(22, file.data.length, true); // Uncompressed size
      view.setUint16(26, nameBytes.length, true); // File name length
      view.setUint16(28, 0, true); // Extra field length
      localHeader.set(nameBytes, 30);

      parts.push(localHeader);
      parts.push(file.data);

      // Central directory entry
      const centralEntry = new Uint8Array(46 + nameBytes.length);
      const centralView = new DataView(centralEntry.buffer);
      
      centralView.setUint32(0, 0x02014b50, true); // Central directory signature
      centralView.setUint16(4, 20, true); // Version made by
      centralView.setUint16(6, 20, true); // Version needed to extract
      centralView.setUint16(8, 0, true); // General purpose bit flag
      centralView.setUint16(10, 0, true); // Compression method
      centralView.setUint16(12, 0, true); // File last modification time
      centralView.setUint16(14, 0, true); // File last modification date
      centralView.setUint32(16, 0, true); // CRC-32
      centralView.setUint32(20, file.data.length, true); // Compressed size
      centralView.setUint32(24, file.data.length, true); // Uncompressed size
      centralView.setUint16(28, nameBytes.length, true); // File name length
      centralView.setUint16(30, 0, true); // Extra field length
      centralView.setUint16(32, 0, true); // File comment length
      centralView.setUint16(34, 0, true); // Disk number start
      centralView.setUint16(36, 0, true); // Internal file attributes
      centralView.setUint32(38, 0, true); // External file attributes
      centralView.setUint32(42, offset, true); // Relative offset of local header
      centralEntry.set(nameBytes, 46);

      centralDirectory.push(centralEntry);
      offset += localHeader.length + file.data.length;
    }

    // Add central directory
    const centralDirOffset = offset;
    let centralDirSize = 0;
    for (const entry of centralDirectory) {
      parts.push(entry);
      centralDirSize += entry.length;
    }

    // End of central directory record
    const endRecord = new Uint8Array(22);
    const endView = new DataView(endRecord.buffer);
    endView.setUint32(0, 0x06054b50, true); // End of central directory signature
    endView.setUint16(4, 0, true); // Number of this disk
    endView.setUint16(6, 0, true); // Disk where central directory starts
    endView.setUint16(8, this.files.length, true); // Number of central directory records on this disk
    endView.setUint16(10, this.files.length, true); // Total number of central directory records
    endView.setUint32(12, centralDirSize, true); // Size of central directory
    endView.setUint32(16, centralDirOffset, true); // Offset of start of central directory
    endView.setUint16(20, 0, true); // Comment length

    parts.push(endRecord);

    // Convert Uint8Array[] to BlobPart[] by creating a single ArrayBuffer
    const totalLength = parts.reduce((acc, arr) => acc + arr.length, 0);
    const result = new Uint8Array(totalLength);
    let resultOffset = 0;
    for (const part of parts) {
      result.set(part, resultOffset);
      resultOffset += part.length;
    }

    return new Blob([result.buffer], { type: 'application/zip' });
  }
}

/**
 * 批量下载所有图片为 ZIP 文件
 * Requirements: 7.6
 */
async function downloadAllAsZip(
  originalImage: string,
  generatedImages: GeneratedImage[],
  resultId: string
): Promise<void> {
  const zip = new SimpleZip();
  
  // 添加原图
  const originalBlob = base64ToBlob(originalImage);
  const originalData = new Uint8Array(await originalBlob.arrayBuffer());
  zip.addFile('original.png', originalData);
  
  // 添加所有生成的图片
  for (let i = 0; i < generatedImages.length; i++) {
    const img = generatedImages[i];
    const blob = base64ToBlob(img.image);
    const data = new Uint8Array(await blob.arrayBuffer());
    const filename = `${i + 1}_${img.perspectiveName.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '_')}.png`;
    zip.addFile(filename, data);
  }
  
  // 生成并下载 ZIP 文件
  const content = zip.generate();
  const link = document.createElement('a');
  link.href = URL.createObjectURL(content);
  link.download = `ai-generated-${resultId}.zip`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(link.href);
}

/**
 * 结果展示组件
 * 
 * 功能：
 * - 网格布局展示多张生成图片 (Requirements: 7.1)
 * - 显示原图对比 (Requirements: 7.2)
 * - 每张图片标注视角名称 (Requirements: 7.3)
 * - 点击放大查看 (Requirements: 7.4)
 * - 单张下载 (Requirements: 7.5)
 * - 批量下载 ZIP (Requirements: 7.6)
 * - 下载文件名包含视角名称 (Requirements: 7.7)
 */
export function ResultDisplay({ result, onDownload, onRegenerate, onFavorite }: ResultDisplayProps) {
  // 图片预览模态框状态 - Requirements: 7.4
  const [preview, setPreview] = useState<PreviewState>({
    isOpen: false,
    image: null,
    isOriginal: false
  });
  
  // 下载中状态
  const [isDownloading, setIsDownloading] = useState(false);

  /**
   * 打开图片预览
   * Requirements: 7.4
   */
  const openPreview = (image: GeneratedImage | null, isOriginal: boolean = false) => {
    setPreview({
      isOpen: true,
      image,
      isOriginal
    });
  };

  /**
   * 关闭图片预览
   */
  const closePreview = () => {
    setPreview({
      isOpen: false,
      image: null,
      isOriginal: false
    });
  };

  /**
   * 下载单张图片
   * Requirements: 7.5, 7.7
   */
  const handleDownloadSingle = (image: GeneratedImage) => {
    const filename = `ai-generated-${result?.id || 'image'}-${image.perspectiveName.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '_')}.png`;
    downloadImage(image.image, filename);
  };

  /**
   * 下载原图
   */
  const handleDownloadOriginal = () => {
    if (!result) return;
    downloadImage(result.originalImage, `original-${result.id}.png`);
  };

  /**
   * 批量下载所有图片
   * Requirements: 7.6
   */
  const handleDownloadAll = async () => {
    if (!result) return;
    
    setIsDownloading(true);
    try {
      await downloadAllAsZip(result.originalImage, result.generatedImages, result.id);
    } catch (error) {
      console.error('Failed to download ZIP:', error);
      alert('下载失败，请重试');
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* 结果展示区 */}
      {!result ? (
        // 默认状态 - 无结果时显示占位符
        <div className="h-[500px] rounded-xl border border-gray-300 overflow-hidden bg-gray-50 flex flex-col items-center justify-center">
          <div className="w-24 h-24 rounded-full bg-gray-200 flex items-center justify-center mb-4">
            <ImageIcon className="w-12 h-12 text-gray-400" />
          </div>
          <p className="text-gray-500">生成结果将显示在这里</p>
        </div>
      ) : (
        <>
          {/* 原图展示区 - Requirements: 7.2 */}
          <div className="space-y-2">
            <h3 className="text-sm font-medium text-gray-700 flex items-center gap-2">
              <span>📷</span>
              <span>原图</span>
            </h3>
            <div 
              className="relative h-32 rounded-lg border border-gray-200 overflow-hidden bg-gray-50 cursor-pointer group"
              onClick={() => openPreview(null, true)}
            >
              <img 
                src={toDataUrl(result.originalImage)}
                alt="原图"
                className="w-full h-full object-contain"
              />
              <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center">
                <div className="opacity-0 group-hover:opacity-100 transition-opacity bg-black/50 text-white px-3 py-1 rounded-lg text-sm flex items-center gap-2">
                  <ZoomIn className="w-4 h-4" />
                  点击放大
                </div>
              </div>
            </div>
          </div>

          {/* 生成结果网格 - Requirements: 7.1, 7.3 */}
          <div className="space-y-2">
            <h3 className="text-sm font-medium text-gray-700 flex items-center gap-2">
              <span>✨</span>
              <span>生成结果 ({result.generatedImages.length} 张)</span>
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {result.generatedImages.map((image, index) => (
                <div 
                  key={`${image.perspectiveId}-${index}`}
                  className="relative rounded-lg border border-gray-200 overflow-hidden bg-gray-50 group"
                >
                  {/* 图片 */}
                  <div 
                    className="aspect-square cursor-pointer"
                    onClick={() => openPreview(image)}
                  >
                    <img 
                      src={toDataUrl(image.image)}
                      alt={image.perspectiveName}
                      className="w-full h-full object-cover"
                    />
                    {/* 悬停遮罩 */}
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center">
                      <div className="opacity-0 group-hover:opacity-100 transition-opacity bg-black/50 text-white px-3 py-1 rounded-lg text-sm flex items-center gap-2">
                        <ZoomIn className="w-4 h-4" />
                        点击放大
                      </div>
                    </div>
                  </div>
                  
                  {/* 视角名称标签 - Requirements: 7.3 */}
                  <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-2">
                    <p className="text-white text-xs font-medium truncate">
                      {image.perspectiveName}
                    </p>
                  </div>
                  
                  {/* 单张下载按钮 - Requirements: 7.5 */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDownloadSingle(image);
                    }}
                    className="absolute top-2 right-2 w-8 h-8 rounded-full bg-white/90 hover:bg-white 
                      shadow-md flex items-center justify-center opacity-0 group-hover:opacity-100 
                      transition-opacity"
                    title="下载此图片"
                  >
                    <Download className="w-4 h-4 text-gray-700" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* 操作按钮组 */}
          <div className="flex gap-3">
            {/* 批量下载按钮 - Requirements: 7.6 */}
            <button
              onClick={handleDownloadAll}
              disabled={isDownloading}
              className="flex-1 h-10 rounded-lg bg-blue-600 hover:bg-blue-700 text-white 
                font-medium text-sm flex items-center justify-center gap-2 transition-colors
                disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isDownloading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  打包中...
                </>
              ) : (
                <>
                  <Package className="w-4 h-4" />
                  下载全部 (ZIP)
                </>
              )}
            </button>
            <button
              onClick={onRegenerate}
              className="flex-1 h-10 rounded-lg bg-white hover:bg-gray-50 text-blue-600 
                border border-blue-600 font-medium text-sm flex items-center justify-center gap-2 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              重新生成
            </button>
            <button
              onClick={onFavorite}
              className="flex-1 h-10 rounded-lg bg-white hover:bg-gray-50 text-gray-700 
                border border-gray-300 font-medium text-sm flex items-center justify-center gap-2 transition-colors"
            >
              <Heart className="w-4 h-4" />
              收藏
            </button>
          </div>

          {/* 生成信息卡片 */}
          <div className="bg-blue-50 rounded-lg p-4 space-y-1">
            <div className="flex items-center gap-2 text-sm text-gray-700">
              <span>⏱️</span>
              <span>生成时间：{result.totalTime.toFixed(1)} 秒</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-700">
              <span>🖼️</span>
              <span>生成数量：{result.generatedImages.length} 张</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-700">
              <span>🎯</span>
              <span>使用步数：{result.params.steps} 步</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-700">
              <span>🌱</span>
              <span>随机种子：{result.params.seed || '随机'}</span>
            </div>
          </div>
        </>
      )}

      {/* 图片预览模态框 - Requirements: 7.4 */}
      <Dialog open={preview.isOpen} onOpenChange={(open) => !open && closePreview()}>
        <DialogContent className="max-w-4xl max-h-[90vh] p-0 overflow-hidden bg-black/95">
          <DialogHeader className="absolute top-0 left-0 right-0 z-10 p-4 bg-gradient-to-b from-black/70 to-transparent">
            <DialogTitle className="text-white">
              {preview.isOriginal ? '原图' : preview.image?.perspectiveName || '图片预览'}
            </DialogTitle>
          </DialogHeader>
          
          {/* 预览图片 */}
          <div className="flex items-center justify-center min-h-[400px] p-8 pt-16">
            {preview.isOriginal && result ? (
              <img 
                src={toDataUrl(result.originalImage)}
                alt="原图"
                className="max-w-full max-h-[70vh] object-contain"
              />
            ) : preview.image ? (
              <img 
                src={toDataUrl(preview.image.image)}
                alt={preview.image.perspectiveName}
                className="max-w-full max-h-[70vh] object-contain"
              />
            ) : null}
          </div>
          
          {/* 预览模态框底部操作栏 */}
          <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/70 to-transparent flex justify-center gap-4">
            <button
              onClick={() => {
                if (preview.isOriginal && result) {
                  handleDownloadOriginal();
                } else if (preview.image) {
                  handleDownloadSingle(preview.image);
                }
              }}
              className="px-4 py-2 rounded-lg bg-white/20 hover:bg-white/30 text-white 
                font-medium text-sm flex items-center gap-2 transition-colors"
            >
              <Download className="w-4 h-4" />
              下载图片
            </button>
            <button
              onClick={closePreview}
              className="px-4 py-2 rounded-lg bg-white/20 hover:bg-white/30 text-white 
                font-medium text-sm flex items-center gap-2 transition-colors"
            >
              <X className="w-4 h-4" />
              关闭
            </button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
