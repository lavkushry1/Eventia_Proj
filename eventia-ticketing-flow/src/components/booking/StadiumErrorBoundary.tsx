import React, { Component, ErrorInfo, ReactNode } from 'react';
import StadiumFallbackView from './StadiumFallbackView';

interface Props {
  children: ReactNode;
  stadiumName: string;
  onSwitchView?: () => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * Error boundary component for Stadium views
 * Catches rendering errors in any of the stadium visualization components
 * and provides a fallback UI instead of crashing the entire app
 */
class StadiumErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null
    };
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log the error to an error reporting service
    console.error('Stadium view error:', error, errorInfo);
  }

  handleRetry = (): void => {
    this.setState({
      hasError: false,
      error: null
    });
  }

  render(): ReactNode {
    if (this.state.hasError) {
      // Render fallback UI
      return (
        <StadiumFallbackView
          onRetry={this.handleRetry}
          stadiumName={this.props.stadiumName}
          error={this.state.error?.message || 'There was an error rendering the stadium view.'}
        />
      );
    }

    // If no error, render children normally
    return this.props.children;
  }
}

export default StadiumErrorBoundary; 