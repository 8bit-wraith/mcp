import { ContextType } from './types';

export class MCPError extends Error {
  constructor(
    message: string,
    public code: string,
    public context?: Record<string, any>
  ) {
    super(message);
    this.name = 'MCPError';
  }
}

export class ValidationError extends MCPError {
  constructor(message: string, context?: Record<string, any>) {
    super(message, 'VALIDATION_ERROR', context);
  }
}

export class OperationError extends MCPError {
  constructor(message: string, context?: Record<string, any>) {
    super(message, 'OPERATION_ERROR', context);
  }
}

export interface ErrorContext {
  type: ContextType;
  operation: string;
  data?: any;
}

export class ErrorHandler {
  // Track operation attempts for resilience
  private operationAttempts: Map<string, number> = new Map();
  
  constructor(private maxRetries: number = 3) {}

  async withRetry<T>(
    operation: () => Promise<T>,
    context: ErrorContext
  ): Promise<T> {
    const operationKey = `${context.type}-${context.operation}`;
    let attempts = this.operationAttempts.get(operationKey) || 0;

    try {
      const result = await operation();
      // Reset attempts on success
      this.operationAttempts.set(operationKey, 0);
      return result;
    } catch (error) {
      attempts++;
      this.operationAttempts.set(operationKey, attempts);

      if (attempts >= this.maxRetries) {
        throw new OperationError(
          `Operation failed after ${attempts} attempts`,
          { ...context, error }
        );
      }

      // Exponential backoff
      const delay = Math.min(1000 * Math.pow(2, attempts), 10000);
      await new Promise(resolve => setTimeout(resolve, delay));
      
      return this.withRetry(operation, context);
    }
  }

  validateContextOperation(
    context: any,
    requiredFields: string[],
    operation: string
  ): void {
    const missingFields = requiredFields.filter(field => !context[field]);
    
    if (missingFields.length > 0) {
      throw new ValidationError(
        `Invalid context for ${operation}`,
        {
          missingFields,
          providedContext: context
        }
      );
    }
  }

  async validateAndExecute<T>(
    operation: () => Promise<T>,
    context: any,
    requiredFields: string[],
    operationName: string
  ): Promise<T> {
    this.validateContextOperation(context, requiredFields, operationName);
    
    return this.withRetry(operation, {
      type: context.type,
      operation: operationName,
      data: context
    });
  }

  // Specific handler for API operations
  async handleAPIOperation<T>(
    operation: () => Promise<T>,
    endpoint: string,
    params: any
  ): Promise<T> {
    try {
      return await this.withRetry(operation, {
        type: ContextType.TOOL,
        operation: `API_${endpoint}`,
        data: params
      });
    } catch (error) {
      // Special handling for API-specific errors
      if (error.response) {
        throw new OperationError(
          `API Error: ${error.response.status}`,
          {
            endpoint,
            params,
            statusCode: error.response.status,
            statusText: error.response.statusText
          }
        );
      }
      throw error;
    }
  }

  // Voice system error handling
  async handleVoiceOperation<T>(
    operation: () => Promise<T>,
    voiceType: string,
    params: any
  ): Promise<T> {
    return this.withRetry(operation, {
      type: ContextType.SYSTEM,
      operation: `VOICE_${voiceType}`,
      data: params
    });
  }

  // Context store error handling
  async handleContextOperation<T>(
    operation: () => Promise<T>,
    contextType: ContextType,
    operationType: string,
    data: any
  ): Promise<T> {
    return this.withRetry(operation, {
      type: contextType,
      operation: `CONTEXT_${operationType}`,
      data
    });
  }

  // Terminal session error handling
  async handleTerminalOperation<T>(
    operation: () => Promise<T>,
    sessionId: string,
    command: string
  ): Promise<T> {
    return this.withRetry(operation, {
      type: ContextType.SYSTEM,
      operation: 'TERMINAL_COMMAND',
      data: { sessionId, command }
    });
  }
}