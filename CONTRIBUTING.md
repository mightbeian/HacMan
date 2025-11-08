# Contributing to HacMan

Thank you for your interest in contributing to HacMan! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Creating Challenges](#creating-challenges)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code:

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Avoid offensive or inappropriate content

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Environment details (OS, browser, etc.)

### Suggesting Features

1. Check existing feature requests
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Possible implementation approach

### Contributing Code

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Ensure all tests pass
6. Submit a pull request

## Creating Challenges

We welcome new CTF challenges! Follow these guidelines:

### Challenge Requirements

1. **Educational Value**: Challenge should teach a real security concept
2. **Fair Difficulty**: Appropriate for the assigned difficulty level
3. **Clear Description**: Well-written description with necessary context
4. **Unique Flag**: Format should be `FLAG{descriptive_flag_content}`
5. **Quality Hints**: 3 progressive hints (vague → specific)

### Challenge Template

```python
{
    "title": "Challenge Title",
    "description": "Detailed challenge description...",
    "category": "web|crypto|stego|forensics|binary|misc",
    "difficulty": 1-5,  # 1=Beginner, 5=Expert
    "points": 50-500,   # Based on difficulty
    "flag": "FLAG{unique_flag_here}",
    "hints": [
        "Hint 1: General direction",
        "Hint 2: More specific guidance",
        "Hint 3: Almost giving it away"
    ],
    "files": ["optional_file1.txt", "optional_file2.png"],
    "url": "http://optional-challenge-url.com",
}
```

### Challenge Categories

#### Web Exploitation
- SQL Injection
- XSS (Cross-Site Scripting)
- CSRF
- Authentication bypass
- File upload vulnerabilities
- SSRF

#### Cryptography
- Classical ciphers (Caesar, Vigenère)
- Modern encryption (RSA, AES)
- Hash functions
- Encoding schemes
- Custom crypto implementations

#### Steganography
- Image steganography
- Audio steganography
- LSB analysis
- Metadata extraction

#### Forensics
- Memory analysis
- Disk forensics
- Network packet analysis
- File recovery
- Log analysis

#### Binary Exploitation
- Buffer overflows
- Format string vulnerabilities
- Reverse engineering
- ROP (Return-Oriented Programming)
- Shellcoding

### Testing Your Challenge

1. **Solve it yourself**: Complete the challenge from scratch
2. **Test hints**: Verify hints are helpful but not spoilers
3. **Check flag format**: Ensure flag follows the `FLAG{...}` format
4. **Validate files**: All referenced files work correctly
5. **Peer review**: Have someone else test the challenge

### Submitting a Challenge

1. Add challenge to `backend/fixtures/challenges.json`
2. Include any necessary files in `backend/media/challenges/`
3. Update documentation if needed
4. Submit a pull request with:
   - Challenge description
   - Intended solution/writeup
   - Any dependencies or setup required

## Development Setup

See the main [README.md](README.md) for detailed installation instructions.

### Quick Start

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata challenges.json

# Frontend
cd frontend
npm install
npm start
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Pull Request Process

1. **Update Documentation**: Reflect any changes in README or docs
2. **Follow Code Style**: Use consistent formatting (PEP 8 for Python)
3. **Write Tests**: Include tests for new features
4. **Update CHANGELOG**: Add entry for significant changes
5. **Request Review**: Tag relevant maintainers

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] No new warnings
- [ ] Dependent changes merged

## Code Style

### Python (Backend)

- Follow PEP 8
- Use meaningful variable names
- Add docstrings for functions/classes
- Keep functions focused and small

### JavaScript (Frontend)

- Use ES6+ features
- Follow Airbnb style guide
- Use meaningful component/variable names
- Add comments for complex logic

### Git Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Be descriptive but concise
- Reference issues when applicable

Example:
```
Add RSA challenge with factorization

- Implements basic RSA encryption challenge
- Adds hints for factorization approach
- Includes test case for flag validation

Closes #123
```

## Questions?

Feel free to:
- Open an issue for questions
- Join our community chat
- Email: cabrera.cpaul@gmail.com

Thank you for contributing to HacMan! 🎯