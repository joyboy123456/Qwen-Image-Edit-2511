/**
 * AI 商品视角转换应用 - API 服务模块
 * 
 * 实现与 Modal 后端的通信，处理图像生成请求。
 * 
 * Requirements:
 * - 4.1: 发送生成请求到 API_Server
 * - 9.1: POST /api/generate 端点
 * - 9.2: 请求参数格式
 * - 9.3: 响应格式
 */

import type {
  Perspective,
  GenerationParams,
  GeneratedImage,
  GenerateRequest,
  GenerateResponse,
  ApiError,
} from '../types';

/**
 * API 配置
 */
const API_CONFIG = {
  // Modal 后端 URL - 在生产环境中应该从环境变量读取
  // 使用类型断言来访问 Vite 环境变量
  baseUrl: (typeof import.meta !== 'undefined' && (import.meta as any).env?.VITE_API_BASE_URL) 
    || 'https://your-modal-app.modal.run',
  // 请求超时时间（毫秒）- 支持多图生成需要较长时间
  timeout: 300000, // 5 分钟
};

/**
 * API 错误类
 * 用于封装 API 调用过程中的错误
 */
export class ApiServiceError extends Error {
  public readonly code: string;
  public readonly statusCode?: number;

  constructor(code: string, message: string, statusCode?: number) {
    super(message);
    this.name = 'ApiServiceError';
    this.code = code;
    this.statusCode = statusCode;
  }
}

/**
 * 格式化请求参数
 * 将前端的参数格式转换为后端 API 期望的格式
 * 
 * @param image - Base64 编码的图片
 * @param perspectives - 选中的视角列表
 * @param params - 生成参数
 * @returns 格式化后的请求对象
 */
export function formatRequest(
  image: string,
  perspectives: Perspective[],
  params: GenerationParams
): GenerateRequest {
  return {
    image,
    perspectives: perspectives.map(p => ({
      id: p.id,
      name: p.name,
      prompt: p.prompt,
      icon: p.icon,
    })),
    steps: params.steps,
    cfg_scale: params.cfgScale,
    seed: params.seed || undefined,
  };
}

/**
 * 解析响应数据
 * 将后端 API 响应转换为前端使用的格式
 * 
 * @param response - API 响应数据
 * @returns 解析后的生成图片列表和元数据
 */
export function parseResponse(response: GenerateResponse): {
  images: GeneratedImage[];
  totalTime: number;
  originalImage: string;
} {
  return {
    images: response.images.map(img => ({
      perspectiveId: img.perspective_id,
      perspectiveName: img.perspective_name,
      image: img.image,
      seedUsed: img.seed_used,
    })),
    totalTime: response.total_time,
    originalImage: response.original_image,
  };
}

/**
 * 解析错误响应
 * 将后端错误响应转换为 ApiServiceError
 * 
 * @param error - 错误响应数据
 * @param statusCode - HTTP 状态码
 * @returns ApiServiceError 实例
 */
export function parseErrorResponse(error: ApiError, statusCode: number): ApiServiceError {
  return new ApiServiceError(error.error, error.message, statusCode);
}

/**
 * 生成图片
 * 调用后端 API 生成多视角图片
 * 
 * Requirements:
 * - 4.1: 发送生成请求到 API_Server
 * - 9.1: POST /api/generate 端点
 * - 9.2: 请求参数格式
 * - 9.3: 响应格式
 * 
 * @param image - Base64 编码的输入图片
 * @param perspectives - 选中的视角列表
 * @param params - 生成参数
 * @returns 生成结果，包含图片列表和元数据
 * @throws ApiServiceError 当请求失败时抛出
 */
export async function generateImages(
  image: string,
  perspectives: Perspective[],
  params: GenerationParams
): Promise<{
  images: GeneratedImage[];
  totalTime: number;
  originalImage: string;
}> {
  // 格式化请求
  const request = formatRequest(image, perspectives, params);
  
  // 创建 AbortController 用于超时控制
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout);
  
  try {
    const response = await fetch(API_CONFIG.baseUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);
    
    // 解析响应
    const data = await response.json();
    
    // 处理错误响应
    if (!response.ok) {
      const apiError = data as ApiError;
      throw parseErrorResponse(apiError, response.status);
    }
    
    // 解析成功响应
    return parseResponse(data as GenerateResponse);
    
  } catch (error) {
    clearTimeout(timeoutId);
    
    // 处理已知的 ApiServiceError
    if (error instanceof ApiServiceError) {
      throw error;
    }
    
    // 处理超时错误
    if (error instanceof Error && error.name === 'AbortError') {
      throw new ApiServiceError(
        'timeout',
        '生成超时，请重试',
        504
      );
    }
    
    // 处理网络错误
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new ApiServiceError(
        'network_error',
        '网络连接失败，请检查网络后重试',
        0
      );
    }
    
    // 处理其他未知错误
    throw new ApiServiceError(
      'unknown_error',
      error instanceof Error ? error.message : '未知错误',
      500
    );
  }
}

/**
 * 设置 API 基础 URL
 * 用于在运行时动态配置 API 地址
 * 
 * @param url - API 基础 URL
 */
export function setApiBaseUrl(url: string): void {
  API_CONFIG.baseUrl = url;
}

/**
 * 获取当前 API 基础 URL
 * 
 * @returns 当前配置的 API 基础 URL
 */
export function getApiBaseUrl(): string {
  return API_CONFIG.baseUrl;
}

/**
 * 设置请求超时时间
 * 
 * @param timeout - 超时时间（毫秒）
 */
export function setApiTimeout(timeout: number): void {
  API_CONFIG.timeout = timeout;
}
