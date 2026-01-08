import React, { useState, useCallback } from 'react';
import { Header } from './components/Header';
import { UploadArea } from './components/UploadArea';
import { DescriptionInput } from './components/DescriptionInput';
import { PresetButtons } from './components/PresetButtons';
import { AdvancedOptions } from './components/AdvancedOptions';
import { ResultDisplay } from './components/ResultDisplay';
import { HistorySection } from './components/HistorySection';
import { ToastContainer, ToastMessage, createErrorToast, createSuccessToast } from './components/Toast';
import { 
  Perspective, 
  GenerationParams, 
  GenerationResult,
  MAX_HISTORY_SIZE 
} from './types';
import { generateImages } from './services/api';
import { 
  toUserFriendlyError, 
  isRetryableError,
  isNetworkError,
  isTimeoutError 
} from './utils/errorHandler';

/**
 * 生成进度状态接口
 * Requirements: 4.2, 4.3
 */
export interface GenerationProgress {
  current: number;
  total: number;
}

function App() {
  // 上传的图片状态
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  // 自定义描述输入
  const [description, setDescription] = useState('');
  // 选中的视角列表 - Requirements: 2.6
  const [selectedPerspectives, setSelectedPerspectives] = useState<Perspective[]>([]);
  // 生成参数
  const [params, setParams] = useState<GenerationParams>({
    steps: 8,
    cfgScale: 3.0,
    seed: ''
  });
  // 是否正在生成 - Requirements: 4.2
  const [isGenerating, setIsGenerating] = useState(false);
  // 生成进度状态 - Requirements: 4.2, 4.3
  const [generationProgress, setGenerationProgress] = useState<GenerationProgress | null>(null);
  // 当前结果（新格式）
  const [currentResult, setCurrentResult] = useState<GenerationResult | null>(null);
  // 历史记录
  const [history, setHistory] = useState<GenerationResult[]>([]);
  // 积分
  const [credits, setCredits] = useState(100);
  // 错误消息
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  // Toast 通知列表 - Requirements: 10.3, 10.4
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  /**
   * 添加 Toast 通知
   */
  const addToast = useCallback((toast: ToastMessage) => {
    setToasts((prev) => [...prev, toast]);
  }, []);

  /**
   * 移除 Toast 通知
   */
  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  /**
   * 处理生成请求
   * Requirements: 4.1, 4.2, 4.3
   */
  const handleGenerate = async () => {
    // 清除之前的错误
    setErrorMessage(null);
    
    // 验证：必须上传图片 - Requirements: 4.4
    if (!uploadedImage) {
      alert('请先上传图片');
      return;
    }
    
    // 验证：必须选择视角或输入描述 - Requirements: 4.5
    if (selectedPerspectives.length === 0 && !description) {
      alert('请选择视角或输入自定义描述');
      return;
    }

    // 验证积分
    if (credits <= 0) {
      alert('积分不足，请充值');
      return;
    }

    // 开始生成 - Requirements: 4.2
    setIsGenerating(true);
    
    // 构建要生成的视角列表
    // 如果选择了预设视角，使用预设视角；否则使用自定义描述创建一个视角
    const perspectivesToGenerate: Perspective[] = selectedPerspectives.length > 0 
      ? selectedPerspectives
      : [{
          id: 'custom',
          name: '自定义视角',
          prompt: description,
          icon: '✨'
        }];
    
    // 设置初始进度 - Requirements: 4.3
    setGenerationProgress({
      current: 0,
      total: perspectivesToGenerate.length
    });

    try {
      // 调用 API 服务 - Requirements: 4.1
      const response = await generateImages(
        uploadedImage,
        perspectivesToGenerate,
        params
      );
      
      // 更新进度为完成
      setGenerationProgress({
        current: perspectivesToGenerate.length,
        total: perspectivesToGenerate.length
      });
      
      // 创建生成结果
      const result: GenerationResult = {
        id: Date.now().toString(),
        originalImage: response.originalImage,
        generatedImages: response.images,
        selectedPerspectives: perspectivesToGenerate,
        timestamp: new Date(),
        params: { ...params },
        totalTime: response.totalTime
      };

      // 更新当前结果
      setCurrentResult(result);
      
      // 添加到历史记录，保留最近 MAX_HISTORY_SIZE 条 - Requirements: 8.1, 8.2
      setHistory((prev: GenerationResult[]) => [result, ...prev.slice(0, MAX_HISTORY_SIZE - 1)]);
      
      // 扣除积分
      setCredits((prev: number) => prev - 1);
      
      // 显示成功通知
      addToast(createSuccessToast(
        '生成完成',
        `成功生成 ${response.images.length} 张图片，耗时 ${response.totalTime.toFixed(1)} 秒`
      ));
      
    } catch (error) {
      // 错误处理 - Requirements: 10.3, 10.4
      console.error('Generation failed:', error);
      
      // 使用错误处理工具获取用户友好的错误信息
      const friendlyError = toUserFriendlyError(error);
      setErrorMessage(friendlyError.message);
      
      // 创建错误 Toast 通知
      const errorToast = createErrorToast(
        friendlyError.title,
        friendlyError.message,
        {
          suggestion: friendlyError.suggestion,
          retryable: friendlyError.retryable,
          onRetry: friendlyError.retryable ? handleGenerate : undefined,
        }
      );
      addToast(errorToast);
      
      // 针对不同错误类型的特殊处理
      if (isNetworkError(error)) {
        console.warn('Network error detected - user may be offline');
      } else if (isTimeoutError(error)) {
        console.warn('Timeout error - generation took too long');
      }
    } finally {
      // 重置生成状态
      setIsGenerating(false);
      setGenerationProgress(null);
    }
  };

  const handlePresetSelect = (preset: string) => {
    setDescription(preset);
  };

  const handlePerspectiveSelectionChange = (perspectives: Perspective[]) => {
    setSelectedPerspectives(perspectives);
  };

  /**
   * 处理历史记录项点击
   * Requirements: 8.3, 8.4
   */
  const handleHistoryItemClick = (item: GenerationResult) => {
    // 恢复结果到主显示区 - Requirements: 8.3
    setCurrentResult(item);
    // 恢复输入参数 - Requirements: 8.4
    setUploadedImage(item.originalImage);
    setSelectedPerspectives(item.selectedPerspectives);
    setParams(item.params);
    // 如果有自定义描述，也恢复
    const customPerspective = item.selectedPerspectives.find(p => p.id === 'custom');
    if (customPerspective) {
      setDescription(customPerspective.prompt);
    }
  };

  const handleDownload = () => {
    if (!currentResult) return;
    
    // 下载第一张生成的图片（后续 Task 11 会实现批量下载）
    const firstImage = currentResult.generatedImages[0];
    if (!firstImage) return;
    
    // 创建下载链接
    const link = document.createElement('a');
    link.href = firstImage.image.startsWith('data:') 
      ? firstImage.image 
      : `data:image/png;base64,${firstImage.image}`;
    link.download = `ai-generated-${currentResult.id}-${firstImage.perspectiveId}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleRegenerate = () => {
    handleGenerate();
  };

  const handleFavorite = () => {
    alert('收藏功能即将上线！');
  };

  /**
   * 处理历史记录删除
   * Requirements: 8.5
   */
  const handleHistoryDelete = (id: string) => {
    setHistory((prev: GenerationResult[]) => prev.filter((item: GenerationResult) => item.id !== id));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#f0f4ff] to-[#e8f0fe]">
      {/* Toast 通知容器 - Requirements: 10.3, 10.4 */}
      <ToastContainer toasts={toasts} onClose={removeToast} />
      
      <Header credits={credits} />
      
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* 主工作区 */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
          <div className="flex flex-col lg:flex-row gap-6">
            {/* 左侧输入区 */}
            <div className="w-full lg:w-[40%] space-y-6">
              <UploadArea 
                image={uploadedImage} 
                onImageChange={setUploadedImage}
              />
              
              <DescriptionInput 
                value={description}
                onChange={setDescription}
              />
              
              <PresetButtons 
                selectedPerspectives={selectedPerspectives}
                onSelectionChange={handlePerspectiveSelectionChange}
                onSelect={handlePresetSelect}
              />
              
              <AdvancedOptions 
                params={params}
                onChange={setParams}
              />
              
              <button
                onClick={handleGenerate}
                disabled={isGenerating || !uploadedImage || (selectedPerspectives.length === 0 && !description)}
                className="w-full h-14 rounded-xl bg-gradient-to-r from-[#3b82f6] to-[#8b5cf6] text-white font-bold text-lg
                  hover:scale-[1.02] hover:shadow-[0_8px_16px_rgba(59,130,246,0.3)] 
                  disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100
                  transition-all duration-200 active:scale-[0.98]"
              >
                {isGenerating ? (
                  <div className="flex items-center justify-center gap-2">
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>AI 正在生成中...</span>
                  </div>
                ) : (
                  <span>🚀 生成新视角</span>
                )}
              </button>
              
              {/* 生成进度条 - Requirements: 4.2, 4.3 */}
              {isGenerating && generationProgress && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm text-gray-600">
                    <span>生成进度</span>
                    <span>{generationProgress.current} / {generationProgress.total}</span>
                  </div>
                  <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-300"
                      style={{ 
                        width: `${(generationProgress.current / generationProgress.total) * 100}%` 
                      }} 
                    />
                  </div>
                </div>
              )}
              
              {/* 简单进度动画（当没有具体进度时显示） */}
              {isGenerating && !generationProgress && (
                <div className="w-full h-1 bg-gray-200 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500 animate-[progress_3s_ease-in-out]" 
                       style={{ animation: 'progress 3.2s ease-in-out' }} />
                </div>
              )}
              
              {/* 错误消息显示 */}
              {errorMessage && !isGenerating && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                  {errorMessage}
                </div>
              )}
            </div>
            
            {/* 右侧结果展示区 */}
            <div className="w-full lg:w-[60%]">
              <ResultDisplay 
                result={currentResult}
                onDownload={handleDownload}
                onRegenerate={handleRegenerate}
                onFavorite={handleFavorite}
              />
            </div>
          </div>
        </div>
        
        {/* 底部历史记录区 */}
        {history.length > 0 && (
          <HistorySection 
            history={history}
            onItemClick={handleHistoryItemClick}
            onDelete={handleHistoryDelete}
          />
        )}
      </main>
    </div>
  );
}

export default App;
