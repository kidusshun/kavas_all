export type OtpRequestResponse = {
  message: string;
  expires_at?: number;
  retry_after?: number;
};

export type ErrorResponse = {
  status: number;
  message: string;
  details?: unknown;
};

// services/types.ts
export interface PdfUploadResponse {
  status: string;
  chunks_uploaded: number;
  filename: string;
}

export type VerfiedOtpResponse = {
  access_token : string;
  token_type : string
}