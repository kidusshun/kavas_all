import { AxiosError } from "axios";
import { updateApi } from "./api";
import { PdfUploadResponse, ErrorResponse } from "../types/types";

export const uploadPdf = async (file: File): Promise<PdfUploadResponse> => {
  // Validate file type
  if (!file.name.endsWith('.pdf')) {
    throw {
      status: 400,
      message: "Only PDF files are accepted"
    } as ErrorResponse;
  }

  try {
    // Create FormData for file upload
    const formData = new FormData();
    formData.append('file', file);

    // Make the request with proper headers for file upload
    const response = await updateApi.post('/corpus/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    return response.data as PdfUploadResponse;
    
  } catch (error) {
    const axiosError = error as AxiosError;
    
    // Handle different error scenarios
    let errorResponse: ErrorResponse = {
      status: 500,
      message: 'An unknown error occurred during PDF upload'
    };

    if (axiosError.response) {
      // Backend returned an error response
      errorResponse = {
        status: axiosError.response.status,
        message: (axiosError.response.data as { detail?: string })?.detail || 'PDF upload failed',
        details: axiosError.response.data
      };
    } else if (axiosError.request) {
      // Request was made but no response received
      errorResponse = {
        status: 503,
        message: 'No response from server. Please check your network connection.'
      };
    } else {
      errorResponse.message = axiosError.message;
    }

    console.error('PDF upload failed:', errorResponse);
    throw errorResponse;
  }
};
