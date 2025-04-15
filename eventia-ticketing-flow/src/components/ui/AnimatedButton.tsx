
import React from 'react';
import { Button, ButtonProps } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface AnimatedButtonProps extends ButtonProps {
  animation?: 'pulse' | 'scale' | 'none';
}

const AnimatedButton = ({
  children,
  animation = 'scale',
  className,
  ...props
}: AnimatedButtonProps) => {
  const animationClasses = {
    pulse: 'animate-pulse-light',
    scale: 'hover:scale-105 transition-transform duration-200',
    none: ''
  };

  return (
    <Button
      className={cn(animationClasses[animation], className)}
      {...props}
    >
      {children}
    </Button>
  );
};

export default AnimatedButton;
export { AnimatedButton };
