import StartIcon from '@mui/icons-material/Start';
import Logo from "../assets/Logo.svg"
import { Link } from 'react-router-dom';

function Hero() {
  return (
    <>
    <div className="text-center mb-16 p-8">
          <div className="flex items- animate-fade-in justify-center md:justify-center">   
              <img src={Logo} alt="NephroAI Logo" className="w-16 h-16 md:w-24 h-24" />
          </div>
        </div>

        <div className="flex flex-col md:flex-col items-center justify-between space-y-8 md:space-y-0 p-4">
          <div className="md:w-1/2 space-y-8 animate-slide-in-left text-center">
            <h1 className="text-5xl md:text-6xl font-urbanist font-bold text-gray-800 leading-tight">
             
              <span className="text-brand">
                {' KAVAS : '}
              </span>
              RAG Knowledge update service
            </h1>
            <p className="text-xl text-gray-600 font-arsenal">
                Automated, real-time knowledge updates for your Retrieval-Augmented Generation (RAG) models—ensuring accuracy and relevance at all times. </p>
            <div className="flex gap-4 justify-center md:justify-center">
              <Link to="/auth">
                <button className="bg-blue-600 text-white px-16 py-2 font-semibold flex items-center gap-2 hover:bg-blue-700 transition-colors duration-300">
                  Login
                  <StartIcon className="w-5 h-5" />
                </button>
              </Link>
            </div>
          </div>
        </div>
    </>
  )
}

export default Hero