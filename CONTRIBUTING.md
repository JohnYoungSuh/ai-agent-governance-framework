# Contributing to AI Agent Governance Framework - Internal

Thank you for your interest in contributing! This document provides guidelines for contributing to the internal repository.

## How to Contribute

### 1. Report Issues
- Use internal issue tracker for bug reports and feature requests
- Provide clear descriptions and examples
- Include relevant context (agent tier, use case, etc.)

### 2. Suggest Enhancements
- Open a discussion in internal communications channels first
- Describe the problem and proposed solution
- Consider impact on existing deployments

### 3. Submit Changes

**Process (No forking required for internal repo):**
1. Create a feature branch (`git checkout -b feature/your-feature`)
2. Make your changes
4. Add tests/examples if applicable
5. Update documentation
3. Commit with clear messages (`git commit -m 'Add feature: X'`)
4. Push to feature branch (`git push origin feature/your-feature`)
5. Open a Pull Request to master

**PR Guidelines:**
- One feature/fix per PR
- Include rationale and context
- Update relevant documentation
- Ensure examples work
- Pass all checks

### 4. Improve Documentation
- Fix typos and clarify language
- Add examples and use cases
- Improve templates and forms
- Translate to other languages

## Code Standards

### For Templates
- Use YAML for structured data
- Include inline comments
- Provide examples
- Validate syntax

### For Scripts
- Use bash with `set -e`
- Include help text (`--help`)
- Add error handling
- Log actions clearly

### For Documentation
- Use Markdown
- Follow existing structure
- Include code examples
- Keep it concise

## Review Process

1. **Automated Checks**: CI runs validation
2. **Peer Review**: Maintainer reviews content
3. **Testing**: Examples must work
4. **Documentation**: Updates required for features
5. **Approval**: Maintainer approves and merges

## Community Guidelines

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn
- Share knowledge and experiences

## Questions?

- Use internal communications channels
- Tag issues with `question`
- Reach out to internal governance team at youngs@suhlabs.com

## Upstream Contributions

To contribute improvements back to the public repository:
- Submit PRs to: https://github.com/JohnYoungSuh/ai-agent-governance-framework
- Follow standard fork-based contribution workflow

Thank you for contributing! 🎉
