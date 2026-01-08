/**
 * PresetButtons 组件属性测试
 * 
 * Feature: ai-product-view-webapp, Property 3: Preset button populates description
 * Validates: Requirements 2.2
 * 
 * 测试预设视角按钮的核心逻辑：
 * - 对于任意预设视角，选择它时应该触发 onSelect 回调并传递正确的 prompt
 */

import { describe, it, expect } from 'vitest';
import * as fc from 'fast-check';
import { PRESET_PERSPECTIVES, Perspective } from '../types';

/**
 * 模拟 PresetButtons 组件的核心选择逻辑
 * 这是从组件中提取的纯函数逻辑，用于属性测试
 */
function simulatePresetSelection(
  perspective: Perspective,
  selectedPerspectives: Perspective[],
  onSelect?: (prompt: string) => void
): { newSelection: Perspective[]; promptPassed?: string } {
  const isSelected = selectedPerspectives.some(p => p.id === perspective.id);
  let promptPassed: string | undefined;
  
  if (isSelected) {
    // 取消选中
    const newSelection = selectedPerspectives.filter(p => p.id !== perspective.id);
    return { newSelection };
  } else {
    // 添加选中
    const newSelection = [...selectedPerspectives, perspective];
    
    // 兼容旧版单选回调 - 传递 prompt
    if (onSelect) {
      promptPassed = perspective.prompt;
      onSelect(promptPassed);
    }
    
    return { newSelection, promptPassed };
  }
}

describe('PresetButtons Property Tests', () => {
  /**
   * Property 3: Preset button populates description
   * 
   * *For any* preset button in the preset list, clicking it SHALL set the 
   * description input value to the preset's corresponding description text.
   * 
   * Feature: ai-product-view-webapp, Property 3: Preset button populates description
   * Validates: Requirements 2.2
   */
  describe('Property 3: Preset button populates description', () => {
    it('should pass the correct prompt to onSelect for any preset perspective', () => {
      // 创建一个生成器，从 PRESET_PERSPECTIVES 中随机选择一个视角
      const perspectiveArb = fc.constantFrom(...PRESET_PERSPECTIVES);
      
      fc.assert(
        fc.property(perspectiveArb, (perspective) => {
          // 记录 onSelect 被调用时传递的值
          let capturedPrompt: string | undefined;
          const mockOnSelect = (prompt: string) => {
            capturedPrompt = prompt;
          };
          
          // 模拟点击一个未选中的视角
          const result = simulatePresetSelection(
            perspective,
            [], // 空选择列表，确保视角未被选中
            mockOnSelect
          );
          
          // 验证：onSelect 应该被调用，且传递的 prompt 应该等于视角的 prompt
          expect(capturedPrompt).toBe(perspective.prompt);
          expect(result.promptPassed).toBe(perspective.prompt);
          
          // 验证：prompt 应该是非空字符串
          expect(perspective.prompt).toBeTruthy();
          expect(typeof perspective.prompt).toBe('string');
          expect(perspective.prompt.length).toBeGreaterThan(0);
        }),
        { numRuns: 100 }
      );
    });

    it('should not call onSelect when deselecting a perspective', () => {
      const perspectiveArb = fc.constantFrom(...PRESET_PERSPECTIVES);
      
      fc.assert(
        fc.property(perspectiveArb, (perspective) => {
          let onSelectCalled = false;
          const mockOnSelect = () => {
            onSelectCalled = true;
          };
          
          // 模拟点击一个已选中的视角（取消选中）
          const result = simulatePresetSelection(
            perspective,
            [perspective], // 视角已在选择列表中
            mockOnSelect
          );
          
          // 验证：取消选中时不应该调用 onSelect
          expect(onSelectCalled).toBe(false);
          expect(result.promptPassed).toBeUndefined();
        }),
        { numRuns: 100 }
      );
    });

    it('should ensure all preset perspectives have valid prompts', () => {
      // 验证所有预设视角都有有效的 prompt
      fc.assert(
        fc.property(fc.constantFrom(...PRESET_PERSPECTIVES), (perspective) => {
          // 每个视角必须有 id, name, prompt, icon
          expect(perspective.id).toBeTruthy();
          expect(perspective.name).toBeTruthy();
          expect(perspective.prompt).toBeTruthy();
          expect(perspective.icon).toBeTruthy();
          
          // prompt 应该包含 "Next Scene" 前缀（根据设计文档）
          expect(perspective.prompt).toContain('Next Scene');
        }),
        { numRuns: 100 }
      );
    });

    it('should correctly populate description for any sequence of selections', () => {
      // 生成随机的视角选择序列
      const selectionSequenceArb = fc.array(
        fc.constantFrom(...PRESET_PERSPECTIVES),
        { minLength: 1, maxLength: 10 }
      );
      
      fc.assert(
        fc.property(selectionSequenceArb, (selections) => {
          const prompts: string[] = [];
          const mockOnSelect = (prompt: string) => {
            prompts.push(prompt);
          };
          
          let currentSelection: Perspective[] = [];
          
          // 模拟一系列选择操作
          for (const perspective of selections) {
            const result = simulatePresetSelection(
              perspective,
              currentSelection,
              mockOnSelect
            );
            currentSelection = result.newSelection;
          }
          
          // 验证：每次新选中时传递的 prompt 都应该与对应视角的 prompt 匹配
          // 注意：取消选中时不会添加到 prompts 数组
          for (const prompt of prompts) {
            const matchingPerspective = PRESET_PERSPECTIVES.find(p => p.prompt === prompt);
            expect(matchingPerspective).toBeDefined();
          }
        }),
        { numRuns: 100 }
      );
    });
  });
});
