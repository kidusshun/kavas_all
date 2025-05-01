import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Auth from './pages/Auth';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import Uploader from './pages/FileUpload'
import Home from './pages/Home';
import OtpVerification from './pages/OtpVerification';

const theme = createTheme({
  typography: {
    fontFamily: '"Arsenal", "Arial", sans-serif',  // Use Urbanist as the default font
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
    <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/auth" element={<Auth />} />
          <Route path="/upload" element={<Uploader />} />
          <Route path='/auth/verify-otp' element={<OtpVerification />} />
        </Routes>
    </Router>
    </ThemeProvider>
  );
}

export default App;