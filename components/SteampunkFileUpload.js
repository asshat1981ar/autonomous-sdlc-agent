import React, { useState, useCallback, useRef } from 'react';
import '../styles/steampunk.css';
export const SteampunkFileUpload = ({ onFileUpload, acceptedTypes = ['*'], maxFiles = 10, maxSize = 50 }) => {
    const [isDragOver, setIsDragOver] = useState(false);
    const [uploadedFiles, setUploadedFiles] = useState([]);
    const [isUploading, setIsUploading] = useState(false);
    const fileInputRef = useRef(null);
    const handleDragOver = useCallback((e) => {
        e.preventDefault();
        setIsDragOver(true);
    }, []);
    const handleDragLeave = useCallback((e) => {
        e.preventDefault();
        setIsDragOver(false);
    }, []);
    const validateFile = (file) => {
        // Check file size
        if (file.size > maxSize * 1024 * 1024) {
            alert(`File ${file.name} is too large. Maximum size is ${maxSize}MB.`);
            return false;
        }
        // Check file type if specified
        if (acceptedTypes.length > 0 && !acceptedTypes.includes('*')) {
            const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
            if (!acceptedTypes.some(type => file.type.includes(type) || type === fileExtension)) {
                alert(`File ${file.name} is not a supported type.`);
                return false;
            }
        }
        return true;
    };
    const processFiles = useCallback(async (files) => {
        setIsUploading(true);
        const validFiles = [];
        for (let i = 0; i < Math.min(files.length, maxFiles); i++) {
            const file = files[i];
            if (validateFile(file)) {
                validFiles.push(file);
            }
        }
        if (validFiles.length > 0) {
            setUploadedFiles(prev => [...prev, ...validFiles]);
            onFileUpload(validFiles);
        }
        setIsUploading(false);
        setIsDragOver(false);
    }, [onFileUpload, maxFiles, maxSize, acceptedTypes]);
    const handleDrop = useCallback((e) => {
        e.preventDefault();
        const files = e.dataTransfer.files;
        processFiles(files);
    }, [processFiles]);
    const handleFileSelect = useCallback((e) => {
        if (e.target.files) {
            processFiles(e.target.files);
        }
    }, [processFiles]);
    const removeFile = (index) => {
        setUploadedFiles(prev => prev.filter((_, i) => i !== index));
    };
    const formatFileSize = (bytes) => {
        if (bytes === 0)
            return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };
    return (React.createElement("div", { className: "steampunk-panel p-6" },
        React.createElement("div", { className: "flex items-center gap-3 mb-6" },
            React.createElement("div", { className: "steampunk-gear" }),
            React.createElement("h3", { className: "text-xl font-bold text-white", style: { fontFamily: 'var(--heading-font)' } }, "Manuscript & Blueprint Repository"),
            React.createElement("div", { className: "steampunk-gear", style: { animationDirection: 'reverse' } })),
        React.createElement("div", { className: `steampunk-upload steampunk-scroll ${isDragOver ? 'drag-over' : ''}`, onDragOver: handleDragOver, onDragLeave: handleDragLeave, onDrop: handleDrop, onClick: () => fileInputRef.current?.click(), style: { cursor: 'pointer' } },
            React.createElement("input", { ref: fileInputRef, type: "file", multiple: true, onChange: handleFileSelect, style: { display: 'none' }, accept: acceptedTypes.join(',') }),
            React.createElement("div", { className: "flex flex-col items-center gap-4" },
                React.createElement("div", { className: "text-6xl text-brass-primary" }, isUploading ? (React.createElement("div", { className: "steampunk-loading" })) : ('📁')),
                React.createElement("div", { className: "text-center" },
                    React.createElement("p", { className: "text-lg font-semibold text-antique-white mb-2" }, isUploading ? 'Processing Documents...' : 'Drop your manuscripts here'),
                    React.createElement("p", { className: "text-sm text-gray-300" }, "or click to browse your mechanical archives")),
                React.createElement("div", { className: "text-xs text-gray-400 text-center" },
                    React.createElement("p", null,
                        "Accepted: ",
                        acceptedTypes.join(', '),
                        " | Max: ",
                        maxFiles,
                        " files | Size limit: ",
                        maxSize,
                        "MB each")))),
        uploadedFiles.length > 0 && (React.createElement("div", { className: "mt-6" },
            React.createElement("h4", { className: "text-lg font-semibold text-brass-primary mb-4 flex items-center gap-2" },
                React.createElement("span", null, "\u2699\uFE0F"),
                "Archived Documents (",
                uploadedFiles.length,
                ")"),
            React.createElement("div", { className: "space-y-3 max-h-64 overflow-y-auto steampunk-scroll" }, uploadedFiles.map((file, index) => (React.createElement("div", { key: index, className: "steampunk-message bg-steel-gradient flex items-center justify-between p-3 rounded-lg" },
                React.createElement("div", { className: "flex items-center gap-3" },
                    React.createElement("span", { className: "text-xl" }, "\uD83D\uDCC4"),
                    React.createElement("div", null,
                        React.createElement("p", { className: "font-medium text-antique-white" }, file.name),
                        React.createElement("p", { className: "text-sm text-gray-300" }, formatFileSize(file.size)))),
                React.createElement("button", { onClick: (e) => {
                        e.stopPropagation();
                        removeFile(index);
                    }, className: "text-rust-red hover:text-red-400 transition-colors p-2", title: "Remove document" }, "\uD83D\uDDD1\uFE0F"))))))),
        React.createElement("div", { className: "flex gap-3 mt-6" },
            React.createElement("button", { className: "steampunk-button flex-1", onClick: () => fileInputRef.current?.click(), disabled: isUploading },
                React.createElement("span", { className: "mr-2" }, "\uD83D\uDCC1"),
                "Browse Archives"),
            uploadedFiles.length > 0 && (React.createElement("button", { className: "steampunk-button bg-rust-red border-rust-red hover:bg-red-600", onClick: () => setUploadedFiles([]) },
                React.createElement("span", { className: "mr-2" }, "\uD83D\uDD25"),
                "Clear All")))));
};
export default SteampunkFileUpload;
