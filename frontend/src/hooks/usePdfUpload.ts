import { useState } from 'react';
import { uploadPdf } from '../services/uploadService';
import { PdfUploadResponse, ErrorResponse } from '../types/types';

export const usePdfUpload = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ErrorResponse | null>(null);
  const [uploadResult, setUploadResult] = useState<PdfUploadResponse | null>(null);
  const [progress, setProgress] = useState(0);

  const upload = async (file: File) => {
    setLoading(true);
    setError(null);
    setProgress(0);
    
    try {
      const result = await uploadPdf(file);
      setUploadResult(result);
      return result;
    } catch (err) {
      const error = err as ErrorResponse;
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    uploadResult,
    progress,
    upload,
    reset: () => {
      setError(null);
      setUploadResult(null);
      setProgress(0);
    }
  };
};