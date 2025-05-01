import React, { useState } from 'react';
import { TextField, Button, Paper, Tabs, Tab, Box, ThemeProvider } from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import Logo from '../assets/Logo.svg';
import { createTheme } from '@mui/material/styles';
import { useAuth } from '../hooks/useAuth';
import { ErrorResponse } from '../types/types';
import { useNavigate } from 'react-router-dom';

const theme = createTheme({
  palette: {
    primary: {
      main: '#ea7f1f',
    },
    secondary: {
      main: '#E0C2FF',
      light: '#F5EBFF',
      contrastText: '#47008F',
    },
  },
});

const AuthPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [emailError, setEmailError] = useState({ error: false, helperText: '' });
  // const { loading, error, sendOtp, otpData } = useAuth();
  
  const navigate = useNavigate();

  const validateEmail = (email: string) => {
    // const kifiyaRegex = /^[^\s@]+@kifiya\.et$/i;
    const kifiyaRegex = /\S+@\S+\.\S+/;
    return kifiyaRegex.test(email);
  };

  const handleEmailChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newEmail = event.target.value;
    setEmail(newEmail);
    
    if (newEmail && !validateEmail(newEmail)) {
      setEmailError({ error: true, helperText: 'Invalid email. Make sure it is a Kifiya email' });
    } else {
      setEmailError({ error: false, helperText: '' });
    }
  };

  const isErrorResponse = (error: unknown): error is ErrorResponse => {
    return (
      typeof error === 'object' && 
      error !== null && 
      'message' in error && 
      typeof (error as ErrorResponse).message === 'string'
    );
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!validateEmail(email)) {
      setEmailError({ error: true, helperText: 'Invalid email' });
      return;
    }
    setEmailError({ error: false, helperText: '' });

    try {
      const response = await fetch('http://localhost:8000/auth/request-otp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to send OTP');
      }

      // Navigate to OTP page with email state
      navigate('/auth/verify-otp', { state: { email: email } });
    } catch (error) {
      if (isErrorResponse(error)) {
        alert(error.message);
      } else {
        alert('An unexpected error occurred');
      }
    }
  };

  return (
    <div className="flex items-center animate-slide-in-right justify-center min-h-screen bg-gradient-to-b">
      <Paper className="p-8 w-full max-w-md">
        <div className="flex items-center animate-fade-in justify-center mb-8">   
          <img src={Logo} alt="Kifiya Logo" className="w-16 h-16 md:w-24 md:h-24" />
        </div>
        <ThemeProvider theme={theme}>
          <Tabs centered>
            <Tab label="Login" color="primary" />
          </Tabs>
        </ThemeProvider>

        <Box mt={4}>
          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Email"
              variant="outlined"
              value={email}
              onChange={handleEmailChange}
              margin="normal"
              helperText={emailError.helperText}
              error={emailError.error}
              InputProps={{
                startAdornment: <PersonIcon className="mr-2" />,
              }}
            />
            <ThemeProvider theme={theme}>
              <Button
                fullWidth
                type="submit"
                variant="contained"
                color="primary"
                className="mt-8 h-12 font-urbanist"
              >
                Send OTP
              </Button>
            </ThemeProvider>
          </form>
        </Box>
      </Paper>
    </div>
  );
};

export default AuthPage;