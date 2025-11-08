import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  CircularProgress,
} from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import api from '../utils/api';
import { useAuth } from '../contexts/AuthContext';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import FlagIcon from '@mui/icons-material/Flag';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';

const Dashboard = () => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/player/dashboard/');
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  const categoryData = dashboardData?.category_breakdown
    ? Object.entries(dashboardData.category_breakdown).map(([key, value]) => ({
        category: key.toUpperCase(),
        solved: value,
      }))
    : [];

  return (
    <Box>
      <Typography variant="h3" fontWeight={700} gutterBottom>
        Welcome back, {user?.username}!
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Here's your hacking progress overview
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <EmojiEventsIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                <Box>
                  <Typography variant="h4" fontWeight={700}>
                    {dashboardData?.profile.total_points || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Points
                  </Typography>
                </Box>
              </Box>
              <Chip
                label={dashboardData?.profile.rank || 'Newbie'}
                color="primary"
                size="small"
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <FlagIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                <Box>
                  <Typography variant="h4" fontWeight={700}>
                    {dashboardData?.profile.challenges_solved || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Challenges Solved
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingUpIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                <Box>
                  <Typography variant="h4" fontWeight={700}>
                    {dashboardData?.statistics.successful_attempts || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Successful Attempts
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Progress Chart */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Progress Over Time
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={dashboardData?.progress_chart || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="date" stroke="#888" />
                  <YAxis stroke="#888" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1a1f3a', border: '1px solid #00ff88' }}
                  />
                  <Line
                    type="monotone"
                    dataKey="points"
                    stroke="#00ff88"
                    strokeWidth={3}
                    dot={{ fill: '#00ff88' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Category Breakdown */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Category Breakdown
              </Typography>
              {categoryData.map((item) => (
                <Box key={item.category} sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">{item.category}</Typography>
                    <Typography variant="body2" color="primary">
                      {item.solved}
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={(item.solved / 10) * 100}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Solves */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Recent Solves
              </Typography>
              {dashboardData?.recent_solves?.length > 0 ? (
                dashboardData.recent_solves.map((solve, index) => (
                  <Box
                    key={index}
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      p: 2,
                      mb: 1,
                      backgroundColor: '#0a0e27',
                      borderRadius: 2,
                    }}
                  >
                    <Box>
                      <Typography variant="body1" fontWeight={600}>
                        {solve.challenge}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(solve.solved_at).toLocaleDateString()}
                      </Typography>
                    </Box>
                    <Chip
                      label={`${solve.points} pts`}
                      color="primary"
                      size="small"
                    />
                  </Box>
                ))
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No challenges solved yet. Start hacking!
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;