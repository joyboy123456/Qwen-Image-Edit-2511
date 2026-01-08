"""
AI 商品视角转换 Web 应用 - 类型定义

定义后端 API 的请求和响应数据模型。
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class Perspective(BaseModel):
    """视角定义"""
    id: str = Field(..., description="Perspective identifier")
    name: str = Field(..., description="Display name")
    prompt: str = Field(..., description="Prompt text for generation")


class GenerateRequest(BaseModel):
    """图像生成请求"""
    image: str = Field(..., description="Base64 encoded input image")
    perspectives: List[Perspective] = Field(..., description="List of perspectives to generate")
    steps: int = Field(default=8, ge=4, le=8, description="Generation steps (4-8)")
    cfg_scale: float = Field(default=3.0, ge=1.0, le=5.0, description="CFG scale (1.0-5.0)")
    seed: Optional[str] = Field(default=None, description="Random seed (optional)")


class GeneratedImage(BaseModel):
    """生成的图像"""
    perspective_id: str = Field(..., description="Perspective identifier")
    perspective_name: str = Field(..., description="Perspective display name")
    image: str = Field(..., description="Base64 encoded result image")
    seed_used: str = Field(..., description="Seed used for generation")


class GenerateResponse(BaseModel):
    """图像生成响应"""
    images: List[GeneratedImage] = Field(..., description="List of generated images")
    total_time: float = Field(..., description="Total generation time in seconds")
    original_image: str = Field(..., description="Original input image base64")


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human readable error message")
