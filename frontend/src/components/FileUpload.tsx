import React, { useState, useCallback } from "react";
import styled from "styled-components";

interface FileUploadProps {
  onUploadStart: (filename: string) => void;
  onUploadComplete: (message: string) => void;
  onUploadError: (error: string) => void;
}

const UploadContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  border: 2px dashed #007bff;
  border-radius: 8px;
  background-color: #f8f9fa;
  text-align: center;
  transition: all 0.3s ease;

  &:hover {
    border-color: #0056b3;
    background-color: #e7f3ff;
  }

  &.dragover {
    border-color: #28a745;
    background-color: #d4edda;
  }
`;

const UploadText = styled.p`
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
`;

const FileInput = styled.input`
  display: none;
`;

const UploadButton = styled.button`
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0, 123, 255, 0.3);
  }

  &:disabled {
    background: #6c757d;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
`;

const StatusMessage = styled.div<{ type: 'info' | 'success' | 'error' }>`
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
  
  ${props => {
    switch (props.type) {
      case 'info':
        return 'background-color: #d1ecf1; color: #0c5460; border-left: 4px solid #bee5eb;';
      case 'success':
        return 'background-color: #d4edda; color: #155724; border-left: 4px solid #c3e6cb;';
      case 'error':
        return 'background-color: #f8d7da; color: #721c24; border-left: 4px solid #f5c6cb;';
      default:
        return '';
    }
  }}
`;

const SupportedFormats = styled.div`
  font-size: 0.75rem;
  color: #6c757d;
  margin-top: 4px;
`;

const FileUpload: React.FC<FileUploadProps> = ({
  onUploadStart,
  onUploadComplete,
  onUploadError,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<{
    type: 'info' | 'success' | 'error';
    message: string;
  } | null>(null);
  const [processingFileId, setProcessingFileId] = useState<string | null>(null);

  const supportedFormats = "PDF, DOCX, DOC, TXT, PNG, JPG, JPEG, TIFF, BMP, GIF";

  const handleFile = useCallback(async (file: File) => {
    if (isUploading) return;

    setIsUploading(true);
    setUploadStatus({ type: 'info', message: 'Uploading file...' });
    onUploadStart(file.name);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const result = await response.json();
      setProcessingFileId(result.file_id);
      setUploadStatus({ type: 'info', message: 'File uploaded! Extracting text...' });

      // Poll for processing status
      const pollStatus = async () => {
        try {
          const statusResponse = await fetch(`http://localhost:8000/upload/status/${result.file_id}`);
          if (statusResponse.ok) {
            const status = await statusResponse.json();
            
            if (status.status === 'processing') {
              setUploadStatus({ type: 'info', message: status.message });
              setTimeout(pollStatus, 2000); // Poll every 2 seconds
            } else if (status.status === 'completed') {
              setUploadStatus({ type: 'success', message: status.message });
              onUploadComplete(status.message);
              setIsUploading(false);
              setProcessingFileId(null);
            } else if (status.status === 'error') {
              setUploadStatus({ type: 'error', message: status.message });
              onUploadError(status.message);
              setIsUploading(false);
              setProcessingFileId(null);
            }
          }
        } catch (error) {
          console.error('Error polling status:', error);
          setTimeout(pollStatus, 3000); // Retry after 3 seconds
        }
      };

      // Start polling
      setTimeout(pollStatus, 1000);

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Upload failed';
      setUploadStatus({ type: 'error', message: errorMessage });
      onUploadError(errorMessage);
      setIsUploading(false);
    }
  }, [isUploading, onUploadStart, onUploadComplete, onUploadError]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFile(files[0]);
    }
  }, [handleFile]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  }, [handleFile]);

  return (
    <div>
      <UploadContainer
        className={isDragOver ? 'dragover' : ''}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <UploadText>
          {isUploading ? 'Processing...' : 'Drag and drop a file here, or click to select'}
        </UploadText>
        
        <UploadButton
          disabled={isUploading}
          onClick={() => document.getElementById('file-input')?.click()}
        >
          {isUploading ? 'Processing...' : 'Choose File'}
        </UploadButton>
        
        <SupportedFormats>
          Supported formats: {supportedFormats}
        </SupportedFormats>
        
        <FileInput
          id="file-input"
          type="file"
          accept=".pdf,.docx,.doc,.txt,.png,.jpg,.jpeg,.tiff,.tif,.bmp,.gif"
          onChange={handleFileSelect}
          disabled={isUploading}
        />
      </UploadContainer>

      {uploadStatus && (
        <StatusMessage type={uploadStatus.type}>
          {uploadStatus.message}
        </StatusMessage>
      )}
    </div>
  );
};

export default FileUpload;
