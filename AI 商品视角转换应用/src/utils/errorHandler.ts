/**
 * AI 商品视角转换应用 - 错误处理工具
 * 
 * 提供统一的错误处理和用户友好的错误消息。
 * 
 * Requirements:
 * - 10.3: 显示错误消息给用户
 * - 10.4: 显示网络连接错误消息
 */

import { ApiServiceError } from '../services/api';

/**
 * 错误类型枚举
 */
export enum ErrorType {
  NETWORK = 'network',
  TIMEOUT = 'timeout',
  VALIDATION = 'validation',
  GENERATION = 'generation',
  SERVER = 'server',
  UNKNOWN = 'unknown',
}

/**
 * 用户友好的错误信息接口
 */
export interface UserFriendlyError {
  type: ErrorType;
  title: string;
  message: string;
  suggestion?: string;
  retryable: boolean;
}

/**
 * 错误代码到用户友好消息的映射
 */
const ERROR_MESSAGES: Record<string, UserFriendlyError> = {
  // 网络错误 - Requirements: 10.4
  network_error: {
    type: ErrorType.NETWORK,
    title: '网络连接失败',
    message: '无法连接到服务器，请检查您的网络连接。',
    suggestion: '请确保您已连接到互联网，然后重试。',
    retryable: true,
  },
  
  // 超时错误 - Requirements: 10.4
  timeout: {
    type: ErrorType.TIMEOUT,
    title: '请求超时',
    message: '图片生成时间过长，请求已超时。',
    suggestion: '您可以尝试减少选择的视角数量，或稍后重试。',
    retryable: true,
  },
  
  // 验证错误
  validation_error: {
    type: ErrorType.VALIDATION,
    title: '参数错误',
    message: '请求参数不正确。',
    suggestion: '请检查您的输入并重试。',
    retryable: false,
  },
  
  // 无效图片
  invalid_image: {
    type: ErrorType.VALIDATION,
    title: '图片无效',
    message: '上传的图片格式不正确或已损坏。',
    suggestion: '请上传有效的 PNG 或 JPG 图片。',
    retryable: false,
  },
  
  // 无效参数
  invalid_params: {
    type: ErrorType.VALIDATION,
    title: '参数无效',
    message: '生成参数超出有效范围。',
    suggestion: '请确保 Steps 在 4-8 之间，CFG Scale 在 1.0-5.0 之间。',
    retryable: false,
  },
  
  // 生成错误 - Requirements: 10.3
  generation_error: {
    type: ErrorType.GENERATION,
    title: '生成失败',
    message: 'AI 图片生成过程中出现错误。',
    suggestion: '请稍后重试，如果问题持续存在，请联系支持。',
    retryable: true,
  },
  
  // 模型错误
  model_error: {
    type: ErrorType.SERVER,
    title: '服务暂时不可用',
    message: 'AI 模型加载失败，服务暂时不可用。',
    suggestion: '请稍后重试，我们正在处理此问题。',
    retryable: true,
  },
  
  // 服务器错误
  server_error: {
    type: ErrorType.SERVER,
    title: '服务器错误',
    message: '服务器内部错误，请稍后重试。',
    suggestion: '如果问题持续存在，请联系支持。',
    retryable: true,
  },
  
  // 未知错误
  unknown_error: {
    type: ErrorType.UNKNOWN,
    title: '未知错误',
    message: '发生了未知错误。',
    suggestion: '请刷新页面并重试。',
    retryable: true,
  },
};

/**
 * 将 API 错误转换为用户友好的错误信息
 * 
 * @param error - 捕获的错误
 * @returns 用户友好的错误信息
 */
export function toUserFriendlyError(error: unknown): UserFriendlyError {
  // 处理 ApiServiceError
  if (error instanceof ApiServiceError) {
    const knownError = ERROR_MESSAGES[error.code];
    if (knownError) {
      return {
        ...knownError,
        // 如果后端提供了更具体的消息，使用后端的消息
        message: error.message || knownError.message,
      };
    }
    
    // 根据 HTTP 状态码判断错误类型
    if (error.statusCode) {
      if (error.statusCode === 504) {
        return ERROR_MESSAGES.timeout;
      }
      if (error.statusCode === 503) {
        return ERROR_MESSAGES.model_error;
      }
      if (error.statusCode >= 500) {
        return {
          ...ERROR_MESSAGES.server_error,
          message: error.message || ERROR_MESSAGES.server_error.message,
        };
      }
      if (error.statusCode >= 400) {
        return {
          ...ERROR_MESSAGES.validation_error,
          message: error.message || ERROR_MESSAGES.validation_error.message,
        };
      }
    }
    
    return {
      ...ERROR_MESSAGES.unknown_error,
      message: error.message || ERROR_MESSAGES.unknown_error.message,
    };
  }
  
  // 处理网络错误
  if (error instanceof TypeError && error.message.includes('fetch')) {
    return ERROR_MESSAGES.network_error;
  }
  
  // 处理超时错误
  if (error instanceof Error && error.name === 'AbortError') {
    return ERROR_MESSAGES.timeout;
  }
  
  // 处理其他 Error 实例
  if (error instanceof Error) {
    return {
      ...ERROR_MESSAGES.unknown_error,
      message: error.message,
    };
  }
  
  // 处理未知类型的错误
  return ERROR_MESSAGES.unknown_error;
}

/**
 * 获取错误的简短消息（用于 toast 通知）
 * 
 * @param error - 捕获的错误
 * @returns 简短的错误消息
 */
export function getErrorMessage(error: unknown): string {
  const friendlyError = toUserFriendlyError(error);
  return friendlyError.message;
}

/**
 * 获取错误的完整消息（包含建议）
 * 
 * @param error - 捕获的错误
 * @returns 完整的错误消息
 */
export function getFullErrorMessage(error: unknown): string {
  const friendlyError = toUserFriendlyError(error);
  if (friendlyError.suggestion) {
    return `${friendlyError.message} ${friendlyError.suggestion}`;
  }
  return friendlyError.message;
}

/**
 * 判断错误是否可重试
 * 
 * @param error - 捕获的错误
 * @returns 是否可重试
 */
export function isRetryableError(error: unknown): boolean {
  const friendlyError = toUserFriendlyError(error);
  return friendlyError.retryable;
}

/**
 * 判断是否为网络错误
 * 
 * @param error - 捕获的错误
 * @returns 是否为网络错误
 */
export function isNetworkError(error: unknown): boolean {
  const friendlyError = toUserFriendlyError(error);
  return friendlyError.type === ErrorType.NETWORK;
}

/**
 * 判断是否为超时错误
 * 
 * @param error - 捕获的错误
 * @returns 是否为超时错误
 */
export function isTimeoutError(error: unknown): boolean {
  const friendlyError = toUserFriendlyError(error);
  return friendlyError.type === ErrorType.TIMEOUT;
}
