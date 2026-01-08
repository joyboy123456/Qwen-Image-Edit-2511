import React from 'react';
import { Gem, Settings, User } from 'lucide-react';

interface HeaderProps {
  credits: number;
}

export function Header({ credits }: HeaderProps) {
  return (
    <header className="h-16 bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-6 h-full flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <span className="text-white font-bold text-xl">AI</span>
          </div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            AI 视角转换
          </h1>
        </div>
        
        {/* 右侧操作区 */}
        <div className="flex items-center gap-4">
          {/* 积分余额 */}
          <div className="flex items-center gap-2 px-4 py-2 bg-blue-50 rounded-lg">
            <Gem className="w-5 h-5 text-blue-600" />
            <span className="text-sm font-medium text-gray-700">
              剩余 {credits} 次
            </span>
          </div>
          
          {/* 设置按钮 */}
          <button className="w-10 h-10 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors">
            <Settings className="w-5 h-5 text-gray-600" />
          </button>
          
          {/* 用户头像 */}
          <button className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center hover:shadow-lg transition-shadow">
            <User className="w-5 h-5 text-white" />
          </button>
        </div>
      </div>
    </header>
  );
}
