import React, { useState, useRef, useEffect, useCallback } from 'react';
import '../styles/steampunk.css';
export const SteampunkChatInterface = ({ messages, onSendMessage, isLoading = false, availableProviders = ['Claude', 'GPT-4', 'Gemini', 'Blackbox'], selectedProvider = 'Claude', onProviderChange }) => {
    const [inputValue, setInputValue] = useState('');
    const [attachedFiles, setAttachedFiles] = useState([]);
    const messagesEndRef = useRef(null);
    const fileInputRef = useRef(null);
    const textareaRef = useRef(null);
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
    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };
    const handleFileAttach = (e) => {
        if (e.target.files) {
            const newFiles = Array.from(e.target.files);
            setAttachedFiles(prev => [...prev, ...newFiles]);
        }
    };
    const removeAttachment = (index) => {
        setAttachedFiles(prev => prev.filter((_, i) => i !== index));
    };
    const adjustTextareaHeight = () => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
        }
    };
    const getProviderIcon = (provider) => {
        const icons = {
            'Claude': '🧠',
            'GPT-4': '🤖',
            'Gemini': '💎',
            'Blackbox': '⚫'
        };
        return icons[provider] || '🔧';
    };
    const formatTime = (date) => {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };
    return (React.createElement("div", { className: "steampunk-chat h-full flex flex-col" },
        React.createElement("div", { className: "steampunk-chat-header" },
            React.createElement("div", { className: "steampunk-gear" }),
            React.createElement("div", { className: "flex-1" },
                React.createElement("h3", { className: "text-lg font-bold" }, "Mechanical Intelligence Console"),
                React.createElement("p", { className: "text-sm opacity-80" }, "Conversing with Artificial Cogitators")),
            React.createElement("div", { className: "flex items-center gap-2" },
                React.createElement("span", { className: "text-sm" }, "Cogitator:"),
                React.createElement("select", { value: selectedProvider, onChange: (e) => onProviderChange?.(e.target.value), className: "steampunk-input py-1 px-2 text-sm bg-coal-black text-antique-white" }, availableProviders.map(provider => (React.createElement("option", { key: provider, value: provider },
                    getProviderIcon(provider),
                    " ",
                    provider))))),
            React.createElement("div", { className: "steampunk-gear", style: { animationDirection: 'reverse' } })),
        React.createElement("div", { className: "flex-1 overflow-y-auto steampunk-scroll p-4 space-y-4" },
            messages.length === 0 ? (React.createElement("div", { className: "text-center text-gray-400 mt-8" },
                React.createElement("div", { className: "text-4xl mb-4" }, "\u2699\uFE0F"),
                React.createElement("p", null, "Initiate discourse with the mechanical minds..."))) : (messages.map((message) => (React.createElement("div", { key: message.id, className: `steampunk-message ${message.sender} ${message.sender === 'user' ? 'ml-8' : message.sender === 'ai' ? 'mr-8' : 'mx-4'}` },
                React.createElement("div", { className: "flex items-start gap-3" },
                    React.createElement("div", { className: "flex-shrink-0" }, message.sender === 'user' ? (React.createElement("div", { className: "w-8 h-8 bg-copper-gradient rounded-full flex items-center justify-center" }, "\uD83D\uDC64")) : message.sender === 'ai' ? (React.createElement("div", { className: "w-8 h-8 bg-steel-gradient rounded-full flex items-center justify-center" }, getProviderIcon(message.aiProvider || selectedProvider))) : (React.createElement("div", { className: "w-8 h-8 bg-brass-gradient rounded-full flex items-center justify-center" }, "\u2699\uFE0F"))),
                    React.createElement("div", { className: "flex-1" },
                        React.createElement("div", { className: "flex items-center gap-2 mb-1" },
                            React.createElement("span", { className: "font-semibold text-sm" }, message.sender === 'user' ? 'Engineer' :
                                message.sender === 'ai' ? (message.aiProvider || selectedProvider) : 'System'),
                            React.createElement("span", { className: "text-xs text-gray-400" }, formatTime(message.timestamp))),
                        React.createElement("div", { className: "text-sm leading-relaxed whitespace-pre-wrap" }, message.content),
                        message.attachments && message.attachments.length > 0 && (React.createElement("div", { className: "mt-2 space-y-1" }, message.attachments.map((file, index) => (React.createElement("div", { key: index, className: "flex items-center gap-2 text-xs bg-black bg-opacity-20 rounded p-2" },
                            React.createElement("span", null, "\uD83D\uDCCE"),
                            React.createElement("span", null, file.name)))))))))))),
            isLoading && (React.createElement("div", { className: "steampunk-message ai mr-8" },
                React.createElement("div", { className: "flex items-center gap-3" },
                    React.createElement("div", { className: "w-8 h-8 bg-steel-gradient rounded-full flex items-center justify-center" },
                        React.createElement("div", { className: "steampunk-loading w-4 h-4" })),
                    React.createElement("div", { className: "flex items-center gap-2" },
                        React.createElement("span", { className: "text-sm" }, "Cogitator processing..."),
                        React.createElement("div", { className: "flex gap-1" },
                            React.createElement("div", { className: "w-2 h-2 bg-brass-primary rounded-full animate-pulse" }),
                            React.createElement("div", { className: "w-2 h-2 bg-brass-primary rounded-full animate-pulse", style: { animationDelay: '0.1s' } }),
                            React.createElement("div", { className: "w-2 h-2 bg-brass-primary rounded-full animate-pulse", style: { animationDelay: '0.2s' } })))))),
            React.createElement("div", { ref: messagesEndRef })),
        React.createElement("div", { className: "border-t border-copper p-4 bg-coal-black" },
            attachedFiles.length > 0 && (React.createElement("div", { className: "mb-3 flex flex-wrap gap-2" }, attachedFiles.map((file, index) => (React.createElement("div", { key: index, className: "flex items-center gap-2 bg-steel-blue bg-opacity-20 rounded px-3 py-1 text-sm" },
                React.createElement("span", null, "\uD83D\uDCCE"),
                React.createElement("span", null, file.name),
                React.createElement("button", { onClick: () => removeAttachment(index), className: "text-rust-red hover:text-red-400 ml-1" }, "\u00D7")))))),
            React.createElement("div", { className: "flex gap-3" },
                React.createElement("button", { onClick: () => fileInputRef.current?.click(), className: "steampunk-button px-3 py-2 text-sm", title: "Attach blueprints", disabled: isLoading }, "\uD83D\uDCCE"),
                React.createElement("input", { ref: fileInputRef, type: "file", multiple: true, onChange: handleFileAttach, style: { display: 'none' }, accept: ".txt,.md,.js,.ts,.tsx,.py,.json,.csv,.pdf,.png,.jpg,.jpeg" }),
                React.createElement("div", { className: "flex-1 relative" },
                    React.createElement("textarea", { ref: textareaRef, value: inputValue, onChange: (e) => {
                            setInputValue(e.target.value);
                            adjustTextareaHeight();
                        }, onKeyPress: handleKeyPress, placeholder: "Transmit your inquiry to the mechanical minds...", className: "steampunk-input w-full resize-none min-h-[44px] max-h-[120px] py-3 pr-12", disabled: isLoading, rows: 1 }),
                    React.createElement("div", { className: "absolute bottom-1 right-2 text-xs text-gray-500" }, inputValue.length)),
                React.createElement("button", { onClick: handleSend, disabled: isLoading || (!inputValue.trim() && attachedFiles.length === 0), className: "steampunk-button px-4 py-2 disabled:opacity-50 disabled:cursor-not-allowed" }, isLoading ? (React.createElement("div", { className: "steampunk-loading w-4 h-4" })) : (React.createElement("span", null, "\u26A1")))),
            React.createElement("div", { className: "flex gap-2 mt-3 text-xs" },
                React.createElement("button", { onClick: () => setInputValue('Analyze the uploaded code and suggest improvements'), className: "text-brass-primary hover:text-amber-glow transition-colors" }, "\uD83D\uDD0D Analyze Code"),
                React.createElement("button", { onClick: () => setInputValue('Generate documentation for this project'), className: "text-brass-primary hover:text-amber-glow transition-colors" }, "\uD83D\uDCDA Generate Docs"),
                React.createElement("button", { onClick: () => setInputValue('Review for security vulnerabilities'), className: "text-brass-primary hover:text-amber-glow transition-colors" }, "\uD83D\uDEE1\uFE0F Security Review")))));
};
export default SteampunkChatInterface;
