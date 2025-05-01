import axios, { AxiosError } from "axios";
import {authApi} from "./api";
import { ErrorResponse, OtpRequestResponse } from "../types/types";

export const requestOtp = async (recipient: string): Promise<OtpRequestResponse> => {
  try {
    const response = await authApi.post('/request-otp', { 
      email: recipient // Changed from 'recipient' to match your backend's expected field name
    });
    
    return {
      message: response.data.message || 'OTP sent successfully',
      expires_at: response.data.expires_at,
      retry_after: response.data.retry_after
    };
    
  } catch (error) {
    const axiosError = error as AxiosError;
    
    // Handle different error scenarios
    let errorResponse: ErrorResponse = {
      status: 500,
      message: 'An unknown error occurred'
    };

    if (axiosError.response) {
      // Backend returned an error response
      errorResponse = {
        status: axiosError.response.status,
        message: (axiosError.response.data as { detail?: string })?.detail || 'Failed to send OTP',
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

    console.error('OTP request failed:', errorResponse);
    throw errorResponse;
  }
};

export const verifyOtp = async (email: string, otp: string) => {
  try {
    const response = await authApi.post('/verify-otp', {
      email: email,
      otp: otp
    });
    
    // Successful verification
    return {
      success: true,
      data: response.data, // Contains access_token and token_type
      error: null
    };
    
  } catch (error) {
    // Handle different error responses
    if (axios.isAxiosError(error)) {
      if (error.response) {
        // Backend returned an error response
        return {
          success: false,
          data: null,
          error: {
            status: error.response.status,
            message: error.response.data?.detail || 'OTP verification failed'
          }
        };
      } else {
        // Network or other errors
        return {
          success: false,
          data: null,
          error: {
            status: 500,
            message: 'Network error occurred'
          }
        };
      }
    }
    
    // Unknown error type
    return {
      success: false,
      data: null,
      error: {
        status: 500,
        message: 'Unknown error occurred'
      }
    };
  }
};
