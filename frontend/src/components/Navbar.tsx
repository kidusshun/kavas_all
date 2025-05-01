import React, { useState } from 'react';
import { Menu, MenuItem, IconButton } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import NephroAiLogo from '../assets/nephroai_logo.svg';


const Navbar: React.FC = () => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  return (
    <nav>
      <div className="container mx-auto flex justify-center items-center px-4">
        {/* Desktop Links (Left) */}
        <div className="hidden md:flex space-x-16 font-urbanist"> {/* Reduced spacing */}
          <a href="#" className="text-gray-700 hover:text-gray-900">HISTORY</a>
          <a href="#" className="text-gray-700 hover:text-gray-900">FAQs</a>
        </div>

        {/* Logo (Center) */}
        <div className="ml-12 mr-12"> {/* Centered */}
            <img src={NephroAiLogo} alt="NephroAI Logo" className="w-16 h-16" />
        </div>

        {/* Desktop Links (Right) */}
        <div className="hidden md:flex space-x-16 font-urbanist"> {/* Reduced spacing */}
          <a href="#" className="text-gray-700 hover:text-gray-900">ABOUT</a>
          <a href="#" className="text-gray-700 hover:text-gray-900">LOGOUT</a>
        </div>

        {/* Mobile Menu (Hamburger Icon) */}
        <div className="md:hidden">
          <IconButton onClick={handleMenuOpen}>
            <MenuIcon />
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem onClick={handleMenuClose}>Link 1</MenuItem>
            <MenuItem onClick={handleMenuClose}>Link 2</MenuItem>
            <MenuItem onClick={handleMenuClose}>Link 3</MenuItem>
            <MenuItem onClick={handleMenuClose}>Link 4</MenuItem>
          </Menu>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;