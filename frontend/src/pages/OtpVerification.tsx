import { useState } from 'react';
import OtpInput from 'react-otp-input';
import { Box } from '@mui/material';
import Logo from "../assets/Logo.svg";
import { useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { ErrorResponse } from '../types/types';
import { useNavigate } from 'react-router-dom';

interface LocationState {
  email : string
}

const OTP_STRING_LENGTH = 6;

export default function OtpVerification() {
  const [otp, setOtp] = useState('');
  const location = useLocation();
  const navigate = useNavigate();
  const { email } = location.state as LocationState
  const { error, verifyOtpCode, otpData } = useAuth();

  const isErrorResponse = (error: unknown): error is ErrorResponse => {
      return (
        typeof error === 'object' && 
        error !== null && 
        'message' in error && 
        typeof (error as ErrorResponse).message === 'string'
      );
  
  };

  const handleSubmit = async (event : React.FormEvent) => {
    event.preventDefault()
    if (otp.length == OTP_STRING_LENGTH) {
      try {
        await verifyOtpCode(email, otp)
        navigate("/upload")
      } catch (error) {
        if (isErrorResponse(error)) {
          alert(error.message);
      } else {
        alert('An unexpected error occurred');
      }
    }
    }
  }
  

  return (
    <div className='flex flex-col items-center justify-center font-urbanist min-h-screen'>
      <div className='flex flex-col justify-around items-center '>
          <img src={Logo} alt="kifiya_logo" className="w-16 h-16 md:w-24 h-24" />
          <h3 className='text-3xl font-semibold'>Enter Your Verification Code</h3>
          <p className=''>Please enter the 6-digit verification code sent to: <strong>{email}</strong></p>
      </div>
      <Box sx={{
        display: 'flex',
        justifyContent: 'center',
        padding: 3,
        '& .otp-container': {
          gap: '8px'
        },
        '& .otp-input': {
          width: '60px !important',
          height: '60px',
          fontSize: '24px',
          borderRadius: '8px',
          border: '1px solid #ccc',
          textAlign: 'center',
          '&:focus': {
            borderColor: '#1976d2',
            outline: 'none',
            boxShadow: '0 0 0 2px rgba(25, 118, 210, 0.2)'
          },
          '&:not([value=""])': {
            borderColor: '#1976d2'
          }
        },
        '& .separator': {
          alignSelf: 'center',
          fontSize: '24px',
          padding: '0 4px'
        }
      }}>
        <OtpInput
          value={otp}
          onChange={setOtp}
          numInputs={6}
          inputType="number"
          renderSeparator={<span className="separator">-</span>}
          renderInput={(props) => <input {...props} className="otp-input" />}
          containerStyle={{ display: 'flex' }}
          inputStyle={{}}
          shouldAutoFocus
        />
      </Box>
       <button className='px-12 py-2 bg-blue-700 text-white' onClick={handleSubmit}>
          Verify OTP
       </button>
    </div>
  );
}
