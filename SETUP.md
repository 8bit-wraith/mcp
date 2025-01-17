# MCP Setup Guide

## Prerequisites
- Node.js >= 14
- npm >= 7
- TypeScript >= 4.5

## Installation

```bash
# Clone the repository
git clone https://github.com/8bit-wraith/mcp.git

# Install dependencies
npm install

# Build the project
npm run build

# Start the services
./scripts/manage.sh start
```

## Configuration

1. Copy `.env.example` to `.env`
2. Update environment variables
3. Configure authentication methods

## Testing

```bash
# Run tests
npm test

# Check coverage
npm run test-coverage
```

## Development Workflow

1. Create feature branch
2. Make changes
3. Run tests
4. Submit PR

## Troubleshooting

See `TROUBLESHOOTING.md` for common issues and solutions.