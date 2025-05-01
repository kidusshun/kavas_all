import { useState } from 'react';
import { requestOtp, verifyOtp,  } from '../services/authService';
import {OtpRequestResponse, ErrorResponse, VerfiedOtpResponse } from '../types/types';

export const useAuth = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ErrorResponse | null>(null);
  const [otpData, setOtpData] = useState<OtpRequestResponse | null>(null);
  const [verificationResult, setVerificationResult] = useState<any>(null);

  const sendOtp = async (email: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await requestOtp(email);
      setOtpData(response);
      return;
    } catch (err) {
      const error = err as ErrorResponse;
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const verifyOtpCode = async (email: string, otp: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await verifyOtp(email, otp);
      const { access_token } = result.data as VerfiedOtpResponse
      localStorage.setItem("token", access_token)
      setVerificationResult(result);
      return;
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
    otpData,
    verificationResult,
    sendOtp,
    verifyOtpCode,
    reset: () => {
      setError(null);
      setOtpData(null);
      setVerificationResult(null);
    }
  };
};