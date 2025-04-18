import React from 'react';

export interface TeamLogoProps {
  teamCode: string;
  size?: number | string;
  className?: string;
  alt?: string;
  useBackendPath?: boolean;
}

/**
 * TeamLogo component displays IPL team logos
 * It can use either the backend API path or the local public assets path
 */
const TeamLogo: React.FC<TeamLogoProps> = ({
  teamCode,
  size = 50,
  className = '',
  alt = '',
  useBackendPath = false,
}) => {
  // Ensure team code is lowercase
  const code = teamCode?.toLowerCase() || '';
  
  // Determine the logo URL based on the source preference
  const logoUrl = useBackendPath
    ? `${import.meta.env.VITE_API_BASE_URL || ''}/static/teams/${code}.png`
    : `/assets/teams/${code}.png`;
  
  // Default to placeholder if team code is empty
  const fallbackUrl = '/placeholder.svg';
  
  return (
    <img
      src={code ? logoUrl : fallbackUrl}
      alt={alt || `${code.toUpperCase()} logo`}
      className={className}
      style={{ width: size, height: size, objectFit: 'contain' }}
      onError={(e) => {
        // Fallback to local path if backend path fails
        if (useBackendPath) {
          (e.target as HTMLImageElement).src = `/assets/teams/${code}.png`;
        } else {
          (e.target as HTMLImageElement).src = fallbackUrl;
        }
      }}
    />
  );
};

export default TeamLogo; 