import React, { useState, useCallback, useRef } from 'react';
import '../styles/steampunk.css';

interface FileUploadProps {
  onFileUpload: (files: File[]) => void;
  acceptedTypes?: string[];
  maxFiles?: number;
  maxSize?: number; // in MB
}

export const SteampunkFileUpload: React.FC<FileUploadProps> = ({
  onFileUpload,
  acceptedTypes = ['*'],
  maxFiles = 10,
  maxSize = 50
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const validateFile = (file: File): boolean => {
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

  const processFiles = useCallback(async (files: FileList) => {
    setIsUploading(true);
    const validFiles: File[] = [];

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

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    processFiles(files);
  }, [processFiles]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      processFiles(e.target.files);
    }
  }, [processFiles]);

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="steampunk-panel p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="steampunk-gear"></div>
        <h3 className="text-xl font-bold text-white" style={{ fontFamily: 'var(--heading-font)' }}>
          Manuscript & Blueprint Repository
        </h3>
        <div className="steampunk-gear" style={{ animationDirection: 'reverse' }}></div>
      </div>

      {/* Upload Area */}
      <div
        className={`steampunk-upload steampunk-scroll ${isDragOver ? 'drag-over' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        style={{ cursor: 'pointer' }}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={handleFileSelect}
          style={{ display: 'none' }}
          accept={acceptedTypes.join(',')}
        />

        <div className="flex flex-col items-center gap-4">
          <div className="text-6xl text-brass-primary">
            {isUploading ? (
              <div className="steampunk-loading"></div>
            ) : (
              '📁'
            )}
          </div>

          <div className="text-center">
            <p className="text-lg font-semibold text-antique-white mb-2">
              {isUploading ? 'Processing Documents...' : 'Drop your manuscripts here'}
            </p>
            <p className="text-sm text-gray-300">
              or click to browse your mechanical archives
            </p>
          </div>

          <div className="text-xs text-gray-400 text-center">
            <p>Accepted: {acceptedTypes.join(', ')} | Max: {maxFiles} files | Size limit: {maxSize}MB each</p>
          </div>
        </div>
      </div>

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="mt-6">
          <h4 className="text-lg font-semibold text-brass-primary mb-4 flex items-center gap-2">
            <span>⚙️</span>
            Archived Documents ({uploadedFiles.length})
          </h4>
          
          <div className="space-y-3 max-h-64 overflow-y-auto steampunk-scroll">
            {uploadedFiles.map((file, index) => (
              <div
                key={index}
                className="steampunk-message bg-steel-gradient flex items-center justify-between p-3 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <span className="text-xl">📄</span>
                  <div>
                    <p className="font-medium text-antique-white">{file.name}</p>
                    <p className="text-sm text-gray-300">{formatFileSize(file.size)}</p>
                  </div>
                </div>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(index);
                  }}
                  className="text-rust-red hover:text-red-400 transition-colors p-2"
                  title="Remove document"
                >
                  🗑️
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="flex gap-3 mt-6">
        <button
          className="steampunk-button flex-1"
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
        >
          <span className="mr-2">📁</span>
          Browse Archives
        </button>
        
        {uploadedFiles.length > 0 && (
          <button
            className="steampunk-button bg-rust-red border-rust-red hover:bg-red-600"
            onClick={() => setUploadedFiles([])}
          >
            <span className="mr-2">🔥</span>
            Clear All
          </button>
        )}
      </div>
    </div>
  );
};

export default SteampunkFileUpload;