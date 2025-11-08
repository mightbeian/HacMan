import React from 'react';
import { AppBar, Toolbar, Typography, Button, Container, Box, IconButton } from '@mui/material';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import SecurityIcon from '@mui/icons-material/Security';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import DashboardIcon from '@mui/icons-material/Dashboard';
import FlagIcon from '@mui/icons-material/Flag';
import PersonIcon from '@mui/icons-material/Person';
import LogoutIcon from '@mui/icons-material/Logout';

const Layout = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const NavButton = ({ to, icon, label }) => {
    const isActive = location.pathname === to;
    return (
      <Button
        component={Link}
        to={to}
        startIcon={icon}
        sx={{
          color: isActive ? 'primary.main' : 'white',
          mx: 1,
          fontWeight: isActive ? 700 : 400,
          borderBottom: isActive ? '2px solid' : 'none',
          borderRadius: 0,
          '&:hover': {
            backgroundColor: 'rgba(0, 255, 136, 0.1)',
          },
        }}
      >
        {label}
      </Button>
    );
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static" sx={{ background: 'linear-gradient(90deg, #0a0e27 0%, #1a1f3a 100%)' }}>
        <Toolbar>
          <SecurityIcon sx={{ mr: 2, fontSize: 32, color: 'primary.main' }} />
          <Typography
            variant="h5"
            component={Link}
            to="/"
            sx={{
              flexGrow: 0,
              fontWeight: 700,
              textDecoration: 'none',
              color: 'white',
              mr: 4,
              background: 'linear-gradient(45deg, #00ff88 30%, #00ccff 90%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            HacMan
          </Typography>

          <Box sx={{ flexGrow: 1, display: 'flex' }}>
            {user && (
              <>
                <NavButton to="/dashboard" icon={<DashboardIcon />} label="Dashboard" />
                <NavButton to="/challenges" icon={<FlagIcon />} label="Challenges" />
                <NavButton to="/leaderboard" icon={<EmojiEventsIcon />} label="Leaderboard" />
              </>
            )}
            {!user && (
              <NavButton to="/leaderboard" icon={<EmojiEventsIcon />} label="Leaderboard" />
            )}
          </Box>

          {user ? (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography variant="body2" sx={{ color: 'primary.main', fontWeight: 600 }}>
                {user.total_points} pts
              </Typography>
              <Button
                component={Link}
                to="/profile"
                startIcon={<PersonIcon />}
                sx={{ color: 'white' }}
              >
                {user.username}
              </Button>
              <IconButton onClick={handleLogout} sx={{ color: 'white' }}>
                <LogoutIcon />
              </IconButton>
            </Box>
          ) : (
            <Box>
              <Button component={Link} to="/login" sx={{ color: 'white', mr: 1 }}>
                Login
              </Button>
              <Button
                component={Link}
                to="/register"
                variant="contained"
                color="primary"
              >
                Register
              </Button>
            </Box>
          )}
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ flexGrow: 1, py: 4 }}>
        {children}
      </Container>

      <Box
        component="footer"
        sx={{
          py: 3,
          px: 2,
          mt: 'auto',
          backgroundColor: '#1a1f3a',
          textAlign: 'center',
        }}
      >
        <Typography variant="body2" color="text.secondary">
          © {new Date().getFullYear()} HacMan CTF Platform. Built with ❤️ for ethical hackers.
        </Typography>
      </Box>
    </Box>
  );
};

export default Layout;