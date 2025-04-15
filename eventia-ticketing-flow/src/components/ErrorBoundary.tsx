import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
      errorInfo: null
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log the error to console
    console.error('🚨 React Error Boundary caught an error:', error, errorInfo);
    
    // You can also log to a monitoring service like Sentry
    if (window.location.hostname !== 'localhost') {
      // Only log in production to avoid noise in development
      // If using Sentry: Sentry.captureException(error);
      
      // Log with correlation ID from API if available
      const correlationId = sessionStorage.getItem('x-correlation-id');
      if (correlationId) {
        console.error('Error correlation ID:', correlationId);
      }
    }
    
    this.setState({
      error,
      errorInfo
    });
  }

  render(): ReactNode {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }
      
      // Default error UI
      return (
        <div className="error-boundary">
          <div className="error-container">
            <h1>Something went wrong.</h1>
            <div className="error-details">
              {this.state.error && (
                <div className="error-message">
                  <h2>Error:</h2>
                  <pre>{this.state.error.toString()}</pre>
                </div>
              )}
              {this.state.errorInfo && (
                <div className="stack-trace">
                  <h2>Component Stack:</h2>
                  <pre>{this.state.errorInfo.componentStack}</pre>
                </div>
              )}
            </div>
            <button
              onClick={() => window.location.reload()}
              className="reset-button"
            >
              Reload Page
            </button>
          </div>
          
          <style jsx>{`
            .error-boundary {
              display: flex;
              flex-direction: column;
              align-items: center;
              justify-content: center;
              height: 100vh;
              padding: 1rem;
              background-color: #f8f9fa;
              color: #212529;
              text-align: center;
            }
            
            .error-container {
              max-width: 800px;
              background-color: white;
              border-radius: 8px;
              padding: 2rem;
              box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            
            h1 {
              color: #dc3545;
              margin-bottom: 1.5rem;
            }
            
            .error-details {
              text-align: left;
              margin-bottom: 2rem;
              overflow: auto;
              max-height: 50vh;
              padding: 1rem;
              background-color: #f8f9fa;
              border-radius: 4px;
            }
            
            pre {
              white-space: pre-wrap;
              overflow-wrap: break-word;
              font-size: 0.875rem;
            }
            
            .reset-button {
              background-color: #0d6efd;
              border: none;
              color: white;
              padding: 0.5rem 1rem;
              border-radius: 4px;
              cursor: pointer;
              font-size: 1rem;
            }
            
            .reset-button:hover {
              background-color: #0b5ed7;
            }
          `}</style>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary; 