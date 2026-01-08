/**
 * AI 商品视角转换应用 - 类型定义
 * 
 * 本文件定义了应用中使用的所有核心类型接口
 */

/**
 * 视角定义接口
 * 用于描述一个可选择的视角选项
 */
export interface Perspective {
  /** 视角唯一标识符 */
  id: string;
  /** 显示名称，如 "左侧45°" */
  name: string;
  /** 实际提示词，如 "Next Scene：将镜头向左旋转45度" */
  prompt: string;
  /** 图标 emoji */
  icon: string;
}

/**
 * 图像生成参数接口
 * 用于配置 AI 生成的高级参数
 */
export interface GenerationParams {
  /** 生成步数 (4-8), 默认: 8 */
  steps: number;
  /** CFG 强度 (1.0-5.0), 默认: 3.0 */
  cfgScale: number;
  /** 随机种子，空字符串表示随机 */
  seed: string;
}

/**
 * 单张生成图片接口
 * 表示一个视角生成的结果图片
 */
export interface GeneratedImage {
  /** 视角标识符 */
  perspectiveId: string;
  /** 视角显示名称 */
  perspectiveName: string;
  /** Base64 编码的图片数据 */
  image: string;
  /** 实际使用的随机种子 */
  seedUsed: string;
}

/**
 * 生成结果接口
 * 表示一次完整的批量生成结果
 */
export interface GenerationResult {
  /** 结果唯一标识符 */
  id: string;
  /** 原始上传图片 (base64) */
  originalImage: string;
  /** 生成的图片列表 */
  generatedImages: GeneratedImage[];
  /** 选中的视角列表 */
  selectedPerspectives: Perspective[];
  /** 生成时间戳 */
  timestamp: Date;
  /** 使用的生成参数 */
  params: GenerationParams;
  /** 总生成耗时（秒） */
  totalTime: number;
}

/**
 * 应用状态接口
 * 用于管理整个应用的状态
 */
export interface AppState {
  /** 上传的图片 (base64 或 null) */
  uploadedImage: string | null;
  /** 选中的视角列表 */
  selectedPerspectives: Perspective[];
  /** 生成参数 */
  params: GenerationParams;
  /** 是否正在生成 */
  isGenerating: boolean;
  /** 生成进度 */
  generationProgress: { current: number; total: number } | null;
  /** 当前显示的结果 */
  currentResult: GenerationResult | null;
  /** 历史记录列表 */
  history: GenerationResult[];
}

/**
 * 预设视角列表
 * 包含所有可选的预设视角选项
 * Requirements: 2.2, 2.3
 */
export const PRESET_PERSPECTIVES: Perspective[] = [
  {
    id: 'front',
    name: '正面视角',
    prompt: 'Next Scene：正面视角',
    icon: '📷'
  },
  {
    id: 'left_45',
    name: '左侧45°',
    prompt: 'Next Scene：将镜头向左旋转45度',
    icon: '↖️'
  },
  {
    id: 'right_45',
    name: '右侧45°',
    prompt: 'Next Scene：将镜头向右旋转45度',
    icon: '↗️'
  },
  {
    id: 'top_down',
    name: '俯视视角',
    prompt: 'Next Scene：将镜头转为俯视',
    icon: '🔽'
  },
  {
    id: 'bottom_up',
    name: '仰视视角',
    prompt: 'Next Scene：将镜头转为微微仰视',
    icon: '🔼'
  },
  {
    id: 'close_up',
    name: '特写镜头',
    prompt: 'Next Scene：将镜头转为特写镜头',
    icon: '🔍'
  },
  {
    id: 'wide_angle',
    name: '广角镜头',
    prompt: 'Next Scene：将镜头转为广角镜头',
    icon: '🌐'
  },
  {
    id: 'move_forward',
    name: '向前移动',
    prompt: 'Next Scene：将镜头向前移动',
    icon: '⬆️'
  },
  {
    id: 'move_backward',
    name: '向后移动',
    prompt: 'Next Scene：将镜头向后移动',
    icon: '⬇️'
  }
];

/**
 * API 请求接口
 */
export interface GenerateRequest {
  /** Base64 编码的输入图片 */
  image: string;
  /** 选中的视角列表 */
  perspectives: Perspective[];
  /** 生成步数 (4-8) */
  steps: number;
  /** CFG 强度 (1.0-5.0) */
  cfg_scale: number;
  /** 随机种子 (可选) */
  seed?: string;
}

/**
 * API 响应中的生成图片接口（snake_case，与后端一致）
 */
export interface ApiGeneratedImage {
  /** 视角标识符 */
  perspective_id: string;
  /** 视角显示名称 */
  perspective_name: string;
  /** Base64 编码的图片数据 */
  image: string;
  /** 实际使用的随机种子 */
  seed_used: string;
}

/**
 * API 响应接口（snake_case，与后端一致）
 */
export interface GenerateResponse {
  /** 生成的图片列表 */
  images: ApiGeneratedImage[];
  /** 总生成耗时（秒） */
  total_time: number;
  /** 原图 base64 */
  original_image: string;
}

/**
 * API 错误响应接口
 */
export interface ApiError {
  /** 错误代码 */
  error: string;
  /** 错误描述信息 */
  message: string;
}

/**
 * 默认生成参数
 */
export const DEFAULT_GENERATION_PARAMS: GenerationParams = {
  steps: 8,
  cfgScale: 3.0,
  seed: ''
};

/**
 * 参数范围常量
 */
export const PARAM_RANGES = {
  steps: { min: 4, max: 8 },
  cfgScale: { min: 1.0, max: 5.0 }
} as const;

/**
 * 历史记录最大数量
 */
export const MAX_HISTORY_SIZE = 10;
