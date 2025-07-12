import React, { useState, useRef, useEffect, useCallback } from 'react';
import '../styles/steampunk.css';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai' | 'system';
  timestamp: Date;
  aiProvider?: string;
  attachments?: File[];
}

interface ChatProps {
  messages: Message[];
  onSendMessage: (content: string, attachments?: File[]) => void;
  isLoading?: boolean;
  availableProviders?: string[];
  selectedProvider?: string;
  onProviderChange?: (provider: string) => void;
}

export const SteampunkChatInterface: React.FC<ChatProps> = ({
  messages,
  onSendMessage,
  isLoading = false,
  availableProviders = ['Claude', 'GPT-4', 'Gemini', 'Blackbox'],
  selectedProvider = 'Claude',
  onProviderChange
}) => {
  const [inputValue, setInputValue] = useState('');
  const [attachedFiles, setAttachedFiles] = useState<File[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = useCallback(() => {
    if (inputValue.trim() || attachedFiles.length > 0) {
      onSendMessage(inputValue.trim(), attachedFiles);
      setInputValue('');
      setAttachedFiles([]);
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  }, [inputValue, attachedFiles, onSendMessage]);

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileAttach = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      setAttachedFiles(prev => [...prev, ...newFiles]);
    }
  };

  const removeAttachment = (index: number) => {
    setAttachedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const adjustTextareaHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  };

  const getProviderIcon = (provider: string) => {
    const icons: { [key: string]: string } = {
      'Claude': '🧠',
      'GPT-4': '🤖',
      'Gemini': '💎',
      'Blackbox': '⚫'
    };
    return icons[provider] || '🔧';
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="steampunk-chat h-full flex flex-col">
      {/* Chat Header */}
      <div className="steampunk-chat-header">
        <div className="steampunk-gear"></div>
        <div className="flex-1">
          <h3 className="text-lg font-bold">Mechanical Intelligence Console</h3>
          <p className="text-sm opacity-80">Conversing with Artificial Cogitators</p>
        </div>
        
        {/* AI Provider Selector */}
        <div className="flex items-center gap-2">
          <span className="text-sm">Cogitator:</span>
          <select
            value={selectedProvider}
            onChange={(e) => onProviderChange?.(e.target.value)}
            className="steampunk-input py-1 px-2 text-sm bg-coal-black text-antique-white"
          >
            {availableProviders.map(provider => (
              <option key={provider} value={provider}>
                {getProviderIcon(provider)} {provider}
              </option>
            ))}
          </select>
        </div>
        
        <div className="steampunk-gear" style={{ animationDirection: 'reverse' }}></div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto steampunk-scroll p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-400 mt-8">
            <div className="text-4xl mb-4">⚙️</div>
            <p>Initiate discourse with the mechanical minds...</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`steampunk-message ${message.sender} ${
                message.sender === 'user' ? 'ml-8' : message.sender === 'ai' ? 'mr-8' : 'mx-4'
              }`}
            >
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0">
                  {message.sender === 'user' ? (
                    <div className="w-8 h-8 bg-copper-gradient rounded-full flex items-center justify-center">
                      👤
                    </div>
                  ) : message.sender === 'ai' ? (
                    <div className="w-8 h-8 bg-steel-gradient rounded-full flex items-center justify-center">
                      {getProviderIcon(message.aiProvider || selectedProvider)}
                    </div>
                  ) : (
                    <div className="w-8 h-8 bg-brass-gradient rounded-full flex items-center justify-center">
                      ⚙️
                    </div>
                  )}
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold text-sm">
                      {message.sender === 'user' ? 'Engineer' : 
                       message.sender === 'ai' ? (message.aiProvider || selectedProvider) : 'System'}
                    </span>
                    <span className="text-xs text-gray-400">
                      {formatTime(message.timestamp)}
                    </span>
                  </div>
                  
                  <div className="text-sm leading-relaxed whitespace-pre-wrap">
                    {message.content}
                  </div>
                  
                  {/* Attachments */}
                  {message.attachments && message.attachments.length > 0 && (
                    <div className="mt-2 space-y-1">
                      {message.attachments.map((file, index) => (
                        <div key={index} className="flex items-center gap-2 text-xs bg-black bg-opacity-20 rounded p-2">
                          <span>📎</span>
                          <span>{file.name}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
        
        {isLoading && (
          <div className="steampunk-message ai mr-8">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-steel-gradient rounded-full flex items-center justify-center">
                <div className="steampunk-loading w-4 h-4"></div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm">Cogitator processing...</span>
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-brass-primary rounded-full animate-pulse"></div>
                  <div className="w-2 h-2 bg-brass-primary rounded-full animate-pulse" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-brass-primary rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-copper p-4 bg-coal-black">
        {/* Attachments Preview */}
        {attachedFiles.length > 0 && (
          <div className="mb-3 flex flex-wrap gap-2">
            {attachedFiles.map((file, index) => (
              <div key={index} className="flex items-center gap-2 bg-steel-blue bg-opacity-20 rounded px-3 py-1 text-sm">
                <span>📎</span>
                <span>{file.name}</span>
                <button
                  onClick={() => removeAttachment(index)}
                  className="text-rust-red hover:text-red-400 ml-1"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}
        
        <div className="flex gap-3">
          {/* File Attachment Button */}
          <button
            onClick={() => fileInputRef.current?.click()}
            className="steampunk-button px-3 py-2 text-sm"
            title="Attach blueprints"
            disabled={isLoading}
          >
            📎
          </button>
          
          <input
            ref={fileInputRef}
            type="file"
            multiple
            onChange={handleFileAttach}
            style={{ display: 'none' }}
            accept=".txt,.md,.js,.ts,.tsx,.py,.json,.csv,.pdf,.png,.jpg,.jpeg"
          />
          
          {/* Message Input */}
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={inputValue}
              onChange={(e) => {
                setInputValue(e.target.value);
                adjustTextareaHeight();
              }}
              onKeyPress={handleKeyPress}
              placeholder="Transmit your inquiry to the mechanical minds..."
              className="steampunk-input w-full resize-none min-h-[44px] max-h-[120px] py-3 pr-12"
              disabled={isLoading}
              rows={1}
            />
            
            {/* Character count */}
            <div className="absolute bottom-1 right-2 text-xs text-gray-500">
              {inputValue.length}
            </div>
          </div>
          
          {/* Send Button */}
          <button
            onClick={handleSend}
            disabled={isLoading || (!inputValue.trim() && attachedFiles.length === 0)}
            className="steampunk-button px-4 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <div className="steampunk-loading w-4 h-4"></div>
            ) : (
              <span>⚡</span>
            )}
          </button>
        </div>
        
        {/* Quick Actions */}
        <div className="flex gap-2 mt-3 text-xs">
          <button
            onClick={() => setInputValue('Analyze the uploaded code and suggest improvements')}
            className="text-brass-primary hover:text-amber-glow transition-colors"
          >
            🔍 Analyze Code
          </button>
          <button
            onClick={() => setInputValue('Generate documentation for this project')}
            className="text-brass-primary hover:text-amber-glow transition-colors"
          >
            📚 Generate Docs
          </button>
          <button
            onClick={() => setInputValue('Review for security vulnerabilities')}
            className="text-brass-primary hover:text-amber-glow transition-colors"
          >
            🛡️ Security Review
          </button>
        </div>
      </div>
    </div>
  );
};

export default SteampunkChatInterface;