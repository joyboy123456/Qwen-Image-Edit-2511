/**
 * Parameter utility functions for AdvancedOptions component
 * These functions handle value clamping and filtering for generation parameters
 * 
 * Requirements: 3.3, 3.4, 3.5
 */

import { PARAM_RANGES } from '../types';

/**
 * Clamp steps value to valid range [4, 8]
 * Requirements: 3.3 - Steps slider value synchronization
 * 
 * @param value - The input value to clamp
 * @returns The clamped value within [4, 8]
 */
export function clampSteps(value: number): number {
  return Math.max(
    PARAM_RANGES.steps.min,
    Math.min(PARAM_RANGES.steps.max, Math.round(value))
  );
}

/**
 * Clamp CFG scale value to valid range [1.0, 5.0]
 * Requirements: 3.4 - CFG scale slider value synchronization
 * 
 * @param value - The input value to clamp
 * @returns The clamped value within [1.0, 5.0]
 */
export function clampCfgScale(value: number): number {
  return Math.max(
    PARAM_RANGES.cfgScale.min,
    Math.min(PARAM_RANGES.cfgScale.max, value)
  );
}

/**
 * Filter seed input to only allow numeric characters
 * Requirements: 3.5 - Seed input numeric filtering
 * 
 * @param value - The input string to filter
 * @returns String containing only numeric characters (0-9)
 */
export function filterSeedInput(value: string): string {
  return value.replace(/\D/g, '');
}
