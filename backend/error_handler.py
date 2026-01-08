"""
AI 商品视角转换 Web 应用 - 后端错误处理模块

提供统一的错误处理和错误响应格式。

Requirements:
- 10.1: 模型加载失败时记录错误并返回服务不可用响应
- 10.2: 图像生成失败时返回描述性错误消息
- 10.5: 生成超时后返回超时错误
"""

from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging
import traceback

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ErrorCode(str, Enum):
    """错误代码枚举"""
    # 验证错误 (400)
    VALIDATION_ERROR = "validation_error"
    INVALID_IMAGE = "invalid_image"
    INVALID_PARAMS = "invalid_params"
    
    # 服务器错误 (500)
    GENERATION_ERROR = "generation_error"
    MODEL_ERROR = "model_error"
    SERVER_ERROR = "server_error"
    
    # 超时错误 (504)
    TIMEOUT = "timeout"
    
    # 服务不可用 (503)
    SERVICE_UNAVAILABLE = "service_unavailable"


@dataclass
class AppError:
    """应用错误类"""
    code: ErrorCode
    message: str
    status_code: int
    details: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "error": self.code.value,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        return result


# 预定义错误消息
ERROR_MESSAGES = {
    # 验证错误
    ErrorCode.VALIDATION_ERROR: {
        "message": "请求参数验证失败",
        "status_code": 400,
    },
    ErrorCode.INVALID_IMAGE: {
        "message": "无效的图片数据",
        "status_code": 400,
    },
    ErrorCode.INVALID_PARAMS: {
        "message": "参数超出有效范围",
        "status_code": 400,
    },
    
    # 服务器错误
    ErrorCode.GENERATION_ERROR: {
        "message": "图像生成失败",
        "status_code": 500,
    },
    ErrorCode.MODEL_ERROR: {
        "message": "AI 模型加载失败",
        "status_code": 503,
    },
    ErrorCode.SERVER_ERROR: {
        "message": "服务器内部错误",
        "status_code": 500,
    },
    
    # 超时错误
    ErrorCode.TIMEOUT: {
        "message": "生成超时",
        "status_code": 504,
    },
    
    # 服务不可用
    ErrorCode.SERVICE_UNAVAILABLE: {
        "message": "服务暂时不可用",
        "status_code": 503,
    },
}


def create_error(
    code: ErrorCode,
    message: Optional[str] = None,
    details: Optional[str] = None
) -> AppError:
    """
    创建应用错误
    
    Args:
        code: 错误代码
        message: 自定义错误消息（可选）
        details: 错误详情（可选）
        
    Returns:
        AppError 实例
    """
    error_info = ERROR_MESSAGES.get(code, {
        "message": "未知错误",
        "status_code": 500,
    })
    
    return AppError(
        code=code,
        message=message or error_info["message"],
        status_code=error_info["status_code"],
        details=details,
    )


def create_validation_error(message: str, details: Optional[str] = None) -> AppError:
    """创建验证错误"""
    return create_error(ErrorCode.VALIDATION_ERROR, message, details)


def create_invalid_image_error(details: Optional[str] = None) -> AppError:
    """创建无效图片错误"""
    return create_error(
        ErrorCode.INVALID_IMAGE,
        "无效的 base64 图片数据",
        details
    )


def create_invalid_params_error(message: str) -> AppError:
    """创建无效参数错误"""
    return create_error(ErrorCode.INVALID_PARAMS, message)


def create_generation_error(
    perspective_name: Optional[str] = None,
    details: Optional[str] = None
) -> AppError:
    """
    创建生成错误 (Requirement 10.2)
    
    Args:
        perspective_name: 失败的视角名称
        details: 错误详情
        
    Returns:
        AppError 实例
    """
    if perspective_name:
        message = f"视角 '{perspective_name}' 的图像生成失败"
    else:
        message = "图像生成失败"
    
    return create_error(ErrorCode.GENERATION_ERROR, message, details)


def create_model_error(details: Optional[str] = None) -> AppError:
    """
    创建模型加载错误 (Requirement 10.1)
    
    Args:
        details: 错误详情
        
    Returns:
        AppError 实例
    """
    logger.error(f"Model loading failed: {details}")
    return create_error(
        ErrorCode.MODEL_ERROR,
        "AI 模型加载失败，服务暂时不可用",
        details
    )


def create_timeout_error(
    timeout_seconds: int = 120,
    perspective_name: Optional[str] = None
) -> AppError:
    """
    创建超时错误 (Requirement 10.5)
    
    Args:
        timeout_seconds: 超时时间（秒）
        perspective_name: 超时的视角名称
        
    Returns:
        AppError 实例
    """
    if perspective_name:
        message = f"视角 '{perspective_name}' 的生成超时（{timeout_seconds}秒）"
    else:
        message = f"生成超时（{timeout_seconds}秒）"
    
    return create_error(ErrorCode.TIMEOUT, message)


def create_server_error(details: Optional[str] = None) -> AppError:
    """创建服务器错误"""
    return create_error(ErrorCode.SERVER_ERROR, details=details)


def create_service_unavailable_error(reason: Optional[str] = None) -> AppError:
    """创建服务不可用错误"""
    message = "服务暂时不可用"
    if reason:
        message = f"{message}：{reason}"
    return create_error(ErrorCode.SERVICE_UNAVAILABLE, message)


def log_error(error: Exception, context: Optional[str] = None) -> None:
    """
    记录错误日志
    
    Args:
        error: 异常对象
        context: 错误上下文描述
    """
    error_message = str(error)
    stack_trace = traceback.format_exc()
    
    if context:
        logger.error(f"[{context}] {error_message}")
    else:
        logger.error(error_message)
    
    logger.debug(f"Stack trace:\n{stack_trace}")


def handle_exception(
    error: Exception,
    context: Optional[str] = None
) -> AppError:
    """
    统一异常处理
    
    将各种异常转换为 AppError
    
    Args:
        error: 异常对象
        context: 错误上下文描述
        
    Returns:
        AppError 实例
    """
    # 记录错误
    log_error(error, context)
    
    # 处理超时错误
    if isinstance(error, TimeoutError):
        return create_timeout_error()
    
    # 处理运行时错误
    if isinstance(error, RuntimeError):
        error_message = str(error).lower()
        
        # 检查是否是模型相关错误
        if "model" in error_message or "load" in error_message:
            return create_model_error(str(error))
        
        # 检查是否是 ComfyUI 服务器错误
        if "comfyui" in error_message or "server" in error_message:
            return create_service_unavailable_error("ComfyUI 服务器未响应")
        
        # 其他运行时错误视为生成错误
        return create_generation_error(details=str(error))
    
    # 处理值错误（通常是验证错误）
    if isinstance(error, ValueError):
        return create_validation_error(str(error))
    
    # 处理其他未知错误
    return create_server_error(str(error))


class ComfyUIHealthCheckError(Exception):
    """ComfyUI 健康检查失败异常"""
    pass


class ModelLoadingError(Exception):
    """模型加载失败异常"""
    pass


class WorkflowExecutionError(Exception):
    """工作流执行失败异常"""
    pass


class ImageGenerationError(Exception):
    """图像生成失败异常"""
    def __init__(self, message: str, perspective_name: Optional[str] = None):
        super().__init__(message)
        self.perspective_name = perspective_name
