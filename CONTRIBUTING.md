# Contributing to Jenna Voice Assistant

Thank you for your interest in contributing to Jenna Voice Assistant. This document provides guidelines and instructions for contributing to this proprietary software project.

## Important License Notice

Jenna Voice Assistant is **proprietary software**. Before contributing, please read and understand the [LICENSE](./LICENSE) file. Key points to remember:

- All contributions you make will be subject to the same proprietary license
- You must credit the original work by linking to: `https://github.com/Mainali1/Jenna-VA`
- Any derivative works must be substantially different (at least 50% changed/added code)

## Code of Conduct

All contributors are expected to adhere to professional standards of conduct:

- Use inclusive language and be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what is best for the project and community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

Bug reports help improve the project. When reporting bugs:

1. Check if the bug has already been reported
2. Use the bug report template if available
3. Include detailed steps to reproduce the bug
4. Describe the expected behavior and what actually happened
5. Include screenshots if applicable
6. Provide system information (OS, Python version, etc.)

### Suggesting Enhancements

We welcome suggestions for enhancements:

1. Clearly describe the enhancement and its benefits
2. Provide examples of how the enhancement would work
3. Consider how the enhancement fits with existing features

### Pull Requests

Follow these steps for submitting pull requests:

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Make your changes following the coding standards
4. Add or update tests as necessary
5. Ensure all tests pass
6. Update documentation to reflect your changes
7. Submit a pull request with a clear description of the changes

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Node.js 16 or higher
- Microsoft Visual C++ Redistributable (latest version)

### Setup Steps

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/YOUR-USERNAME/Jenna-VA.git
   cd Jenna-VA
   ```

2. Set up Python environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. Configure environment:
   ```bash
   copy .env.template .env  # On Windows
   cp .env.template .env  # On macOS/Linux
   # Edit .env with your API keys and preferences
   ```

5. Run the application:
   ```bash
   python main.py
   ```

## Coding Standards

### Python Code

- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for all functions, classes, and modules
- Keep functions focused on a single responsibility
- Use meaningful variable and function names
- Add comments for complex logic

### TypeScript/JavaScript Code

- Follow the ESLint configuration in the project
- Use TypeScript types/interfaces for all components and functions
- Follow React best practices for component structure
- Use functional components with hooks instead of class components
- Keep components small and focused on a single responsibility

### Testing

- Write unit tests for new functionality
- Ensure existing tests pass before submitting a pull request
- Aim for good test coverage of critical functionality

## Documentation

- Update documentation for any changes to features or APIs
- Document complex algorithms or design decisions
- Keep the README and other documentation up to date

## Review Process

All submissions require review before being merged:

1. Automated checks must pass (linting, tests)
2. At least one maintainer must approve the changes
3. Changes may require revisions before being accepted
4. Large changes may require discussion before implementation

## Attribution

All contributions will be attributed to their authors. By contributing, you agree to be listed as a contributor to the project.

---

Thank you for contributing to Jenna Voice Assistant!

© 2023 Jenna Development Team. All rights reserved.