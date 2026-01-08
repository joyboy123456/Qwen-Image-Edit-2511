/**
 * AI 商品视角转换应用 - Toast 通知组件
 * 
 * 提供用户友好的错误和成功消息通知。
 * 
 * Requirements:
 * - 10.3: 显示错误消息给用户
 * - 10.4: 显示网络连接错误消息
 */

import React, { useEffect, useState } from 'react';

/**
 * Toast 类型
 */
export type ToastType = 'success' | 'error' | 'warning' | 'info';

/**
 * Toast 消息接口
 */
export interface ToastMessage {
  id: string;
  type: ToastType;
  title: string;
  message: string;
  suggestion?: string;
  duration?: number;
  retryable?: boolean;
  onRetry?: () => void;
}

/**
 * Toast 组件属性
 */
interface ToastProps {
  toast: ToastMessage;
  onClose: (id: string) => void;
}

/**
 * 单个 Toast 组件
 */
export function Toast({ toast, onClose }: ToastProps) {
  const [isVisible, setIsVisible] = useState(true);
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    if (toast.duration && toast.duration > 0) {
      const timer = setTimeout(() => {
        handleClose();
      }, toast.duration);
      return () => clearTimeout(timer);
    }
  }, [toast.duration]);

  const handleClose = () => {
    setIsExiting(true);
    setTimeout(() => {
      setIsVisible(false);
      onClose(toast.id);
    }, 300);
  };

  if (!isVisible) return null;

  // 根据类型获取样式
  const getTypeStyles = () => {
    switch (toast.type) {
      case 'success':
        return {
          bg: 'bg-green-50',
          border: 'border-green-200',
          icon: '✅',
          titleColor: 'text-green-800',
          textColor: 'text-green-700',
        };
      case 'error':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          icon: '❌',
          titleColor: 'text-red-800',
          textColor: 'text-red-700',
        };
      case 'warning':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          icon: '⚠️',
          titleColor: 'text-yellow-800',
          textColor: 'text-yellow-700',
        };
      case 'info':
      default:
        return {
          bg: 'bg-blue-50',
          border: 'border-blue-200',
          icon: 'ℹ️',
          titleColor: 'text-blue-800',
          textColor: 'text-blue-700',
        };
    }
  };

  const styles = getTypeStyles();

  return (
    <div
      className={`
        ${styles.bg} ${styles.border} border rounded-lg shadow-lg p-4 max-w-md
        transform transition-all duration-300 ease-in-out
        ${isExiting ? 'opacity-0 translate-x-full' : 'opacity-100 translate-x-0'}
      `}
    >
      <div className="flex items-start gap-3">
        <span className="text-xl flex-shrink-0">{styles.icon}</span>
        <div className="flex-1 min-w-0">
          <h4 className={`font-semibold ${styles.titleColor}`}>{toast.title}</h4>
          <p className={`text-sm mt-1 ${styles.textColor}`}>{toast.message}</p>
          {toast.suggestion && (
            <p className={`text-xs mt-2 ${styles.textColor} opacity-80`}>
              💡 {toast.suggestion}
            </p>
          )}
          {toast.retryable && toast.onRetry && (
            <button
              onClick={toast.onRetry}
              className={`
                mt-3 px-3 py-1.5 text-sm font-medium rounded-md
                ${toast.type === 'error' ? 'bg-red-100 text-red-700 hover:bg-red-200' : 'bg-blue-100 text-blue-700 hover:bg-blue-200'}
                transition-colors duration-200
              `}
            >
              🔄 重试
            </button>
          )}
        </div>
        <button
          onClick={handleClose}
          className={`
            flex-shrink-0 p-1 rounded-full hover:bg-black/5
            ${styles.textColor} opacity-60 hover:opacity-100
            transition-opacity duration-200
          `}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
}

/**
 * Toast 容器组件属性
 */
interface ToastContainerProps {
  toasts: ToastMessage[];
  onClose: (id: string) => void;
}

/**
 * Toast 容器组件
 * 
 * 在屏幕右上角显示所有 Toast 通知
 */
export function ToastContainer({ toasts, onClose }: ToastContainerProps) {
  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-3">
      {toasts.map((toast) => (
        <Toast key={toast.id} toast={toast} onClose={onClose} />
      ))}
    </div>
  );
}

/**
 * 创建 Toast 消息的工厂函数
 */
export function createToast(
  type: ToastType,
  title: string,
  message: string,
  options?: {
    suggestion?: string;
    duration?: number;
    retryable?: boolean;
    onRetry?: () => void;
  }
): ToastMessage {
  return {
    id: `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    type,
    title,
    message,
    suggestion: options?.suggestion,
    duration: options?.duration ?? (type === 'error' ? 8000 : 5000),
    retryable: options?.retryable,
    onRetry: options?.onRetry,
  };
}

/**
 * 创建错误 Toast
 */
export function createErrorToast(
  title: string,
  message: string,
  options?: {
    suggestion?: string;
    retryable?: boolean;
    onRetry?: () => void;
  }
): ToastMessage {
  return createToast('error', title, message, {
    ...options,
    duration: 8000, // 错误消息显示更长时间
  });
}

/**
 * 创建成功 Toast
 */
export function createSuccessToast(title: string, message: string): ToastMessage {
  return createToast('success', title, message, { duration: 3000 });
}
