/**
 * API 服务单元测试
 * 
 * 测试请求格式化、响应解析和错误处理
 * Requirements: 9.3, 9.4
 */

import { describe, it, expect } from 'vitest';
import {
  formatRequest,
  parseResponse,
  parseErrorResponse,
  ApiServiceError,
} from './api';
import type { Perspective, GenerationParams, GenerateResponse, ApiError } from '../types';

describe('API Service', () => {
  // 测试数据
  const mockPerspectives: Perspective[] = [
    { id: 'front', name: '正面视角', prompt: 'Next Scene：正面视角', icon: '📷' },
    { id: 'left_45', name: '左侧45°', prompt: 'Next Scene：将镜头向左旋转45度', icon: '↖️' },
  ];

  const mockParams: GenerationParams = {
    steps: 8,
    cfgScale: 3.0,
    seed: '12345',
  };

  const mockImage = 'base64encodedimage';

  describe('formatRequest - 请求格式化', () => {
    it('should format request with all parameters correctly', () => {
      const result = formatRequest(mockImage, mockPerspectives, mockParams);

      expect(result.image).toBe(mockImage);
      expect(result.steps).toBe(8);
      expect(result.cfg_scale).toBe(3.0);
      expect(result.seed).toBe('12345');
      expect(result.perspectives).toHaveLength(2);
    });

    it('should map perspectives correctly', () => {
      const result = formatRequest(mockImage, mockPerspectives, mockParams);

      expect(result.perspectives[0]).toEqual({
        id: 'front',
        name: '正面视角',
        prompt: 'Next Scene：正面视角',
        icon: '📷',
      });
      expect(result.perspectives[1]).toEqual({
        id: 'left_45',
        name: '左侧45°',
        prompt: 'Next Scene：将镜头向左旋转45度',
        icon: '↖️',
      });
    });

    it('should handle empty seed as undefined', () => {
      const paramsWithEmptySeed: GenerationParams = {
        steps: 8,
        cfgScale: 3.0,
        seed: '',
      };

      const result = formatRequest(mockImage, mockPerspectives, paramsWithEmptySeed);

      expect(result.seed).toBeUndefined();
    });

    it('should handle single perspective', () => {
      const singlePerspective = [mockPerspectives[0]];
      const result = formatRequest(mockImage, singlePerspective, mockParams);

      expect(result.perspectives).toHaveLength(1);
      expect(result.perspectives[0].id).toBe('front');
    });

    it('should handle empty perspectives array', () => {
      const result = formatRequest(mockImage, [], mockParams);

      expect(result.perspectives).toHaveLength(0);
    });
  });

  describe('parseResponse - 响应解析', () => {
    const mockApiResponse: GenerateResponse = {
      images: [
        {
          perspective_id: 'front',
          perspective_name: '正面视角',
          image: 'generated_image_base64_1',
          seed_used: '12345',
        },
        {
          perspective_id: 'left_45',
          perspective_name: '左侧45°',
          image: 'generated_image_base64_2',
          seed_used: '12346',
        },
      ],
      total_time: 15.5,
      original_image: 'original_base64',
    };

    it('should parse response with multiple images correctly', () => {
      const result = parseResponse(mockApiResponse);

      expect(result.images).toHaveLength(2);
      expect(result.totalTime).toBe(15.5);
      expect(result.originalImage).toBe('original_base64');
    });

    it('should convert snake_case to camelCase for images', () => {
      const result = parseResponse(mockApiResponse);

      expect(result.images[0]).toEqual({
        perspectiveId: 'front',
        perspectiveName: '正面视角',
        image: 'generated_image_base64_1',
        seedUsed: '12345',
      });
    });

    it('should handle single image response', () => {
      const singleImageResponse: GenerateResponse = {
        images: [mockApiResponse.images[0]],
        total_time: 8.2,
        original_image: 'original_base64',
      };

      const result = parseResponse(singleImageResponse);

      expect(result.images).toHaveLength(1);
      expect(result.totalTime).toBe(8.2);
    });

    it('should handle empty images array', () => {
      const emptyResponse: GenerateResponse = {
        images: [],
        total_time: 0,
        original_image: 'original_base64',
      };

      const result = parseResponse(emptyResponse);

      expect(result.images).toHaveLength(0);
      expect(result.totalTime).toBe(0);
    });
  });

  describe('parseErrorResponse - 错误响应解析', () => {
    it('should create ApiServiceError with correct properties', () => {
      const apiError: ApiError = {
        error: 'validation_error',
        message: 'image is required',
      };

      const result = parseErrorResponse(apiError, 400);

      expect(result).toBeInstanceOf(ApiServiceError);
      expect(result.code).toBe('validation_error');
      expect(result.message).toBe('image is required');
      expect(result.statusCode).toBe(400);
    });

    it('should handle different error codes', () => {
      const serverError: ApiError = {
        error: 'generation_error',
        message: 'Image generation failed',
      };

      const result = parseErrorResponse(serverError, 500);

      expect(result.code).toBe('generation_error');
      expect(result.statusCode).toBe(500);
    });

    it('should handle timeout error', () => {
      const timeoutError: ApiError = {
        error: 'timeout',
        message: 'Generation timed out after 120 seconds',
      };

      const result = parseErrorResponse(timeoutError, 504);

      expect(result.code).toBe('timeout');
      expect(result.statusCode).toBe(504);
    });
  });

  describe('ApiServiceError', () => {
    it('should be an instance of Error', () => {
      const error = new ApiServiceError('test_error', 'Test message', 400);

      expect(error).toBeInstanceOf(Error);
      expect(error.name).toBe('ApiServiceError');
    });

    it('should have correct properties', () => {
      const error = new ApiServiceError('network_error', 'Network failed', 0);

      expect(error.code).toBe('network_error');
      expect(error.message).toBe('Network failed');
      expect(error.statusCode).toBe(0);
    });

    it('should work without statusCode', () => {
      const error = new ApiServiceError('unknown', 'Unknown error');

      expect(error.code).toBe('unknown');
      expect(error.statusCode).toBeUndefined();
    });
  });
});
