# Generated by https://smithery.ai. See: https://smithery.ai/docs/config#dockerfile
# Use an official Node.js runtime as a parent image
FROM node:18-alpine AS builder

# Set the working directory
WORKDIR /app

# Install pnpm globally
RUN npm install -g pnpm

# Copy the package and lock files
COPY packages/mcp-server-enhanced-ssh/package.json packages/mcp-server-enhanced-ssh/pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install

# Copy the rest of the application's source code
COPY packages/mcp-server-enhanced-ssh .

# Build the application
RUN pnpm run build

# Final stage: production environment
FROM node:18-alpine

# Set the working directory
WORKDIR /app

# Copy built files from the builder
COPY --from=builder /app/dist ./dist

# Copy node_modules
COPY --from=builder /app/node_modules ./node_modules

# Specify the default command to run the application
CMD ["node", "dist/index.js"]