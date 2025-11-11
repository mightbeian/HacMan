const express = require('express');
const router = express.Router();
const { authenticateToken } = require('../middleware/auth');

// Mock user data
let users = [];

// Get user profile
router.get('/profile', authenticateToken, (req, res) => {
  const user = users.find(u => u.id === req.user.id) || {
    id: req.user.id,
    username: req.user.username,
    email: 'user@example.com',
    rank: 'Newbie',
    points: 0,
    badges: [],
    solvedChallenges: [],
    createdAt: new Date()
  };
  
  res.json({ user });
});

// Get user stats
router.get('/stats', authenticateToken, (req, res) => {
  const stats = {
    totalPoints: 850,
    challengesSolved: 12,
    rank: 'Script Kiddie',
    globalRank: 42,
    categoryStats: {
      web: { solved: 5, total: 15, accuracy: 0.85 },
      crypto: { solved: 3, total: 10, accuracy: 0.90 },
      forensics: { solved: 2, total: 8, accuracy: 0.75 },
      stego: { solved: 1, total: 6, accuracy: 0.80 },
      binary: { solved: 1, total: 5, accuracy: 0.60 }
    },
    recentActivity: [
      { date: '2025-11-10', challenge: 'SQL Injection 101', points: 100, time: '15m' },
      { date: '2025-11-09', challenge: 'XSS Playground', points: 150, time: '28m' },
      { date: '2025-11-08', challenge: 'Caesar Cipher', points: 50, time: '5m' }
    ],
    strengthAreas: ['Web Exploitation', 'Cryptography'],
    weaknessAreas: ['Binary Exploitation', 'Forensics'],
    avgSolveTime: 22,
    streak: 5
  };
  
  res.json(stats);
});

// Get ML recommendations
router.get('/recommendations', authenticateToken, (req, res) => {
  const recommendations = [
    {
      challengeId: 7,
      title: 'Command Injection',
      category: 'web',
      difficulty: 'medium',
      points: 200,
      reason: 'Based on your web exploitation skills',
      confidence: 0.92,
      estimatedTime: '25-35 minutes'
    },
    {
      challengeId: 8,
      title: 'RSA Basics',
      category: 'crypto',
      difficulty: 'medium',
      points: 180,
      reason: 'Strengthen your cryptography knowledge',
      confidence: 0.88,
      estimatedTime: '20-30 minutes'
    },
    {
      challengeId: 9,
      title: 'Network Traffic Analysis',
      category: 'forensics',
      difficulty: 'easy',
      points: 120,
      reason: 'Build forensics fundamentals',
      confidence: 0.75,
      estimatedTime: '15-20 minutes'
    }
  ];
  
  res.json({ recommendations });
});

// Update profile
router.patch('/profile', authenticateToken, (req, res) => {
  const { bio, avatar, preferences } = req.body;
  
  res.json({
    message: 'Profile updated successfully',
    user: {
      id: req.user.id,
      username: req.user.username,
      bio: bio || '',
      avatar: avatar || null,
      preferences: preferences || {}
    }
  });
});

module.exports = router;