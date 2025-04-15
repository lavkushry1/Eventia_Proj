import React from 'react';
import { cn } from '@/lib/utils';

export interface TeamBadgeProps {
  team: string;
  className?: string;
  showName?: boolean;
  color?: string;
}

export const TeamBadge: React.FC<TeamBadgeProps> = ({ 
  team, 
  className, 
  showName = true,
  color
}) => {
  const teamCode = team?.toLowerCase();
  
  // Default styling
  let badgeClasses = "px-2 py-1 rounded text-white font-medium";
  
  // Use custom color if provided
  if (color) {
    return (
      <span 
        className={cn(badgeClasses, className)}
        style={{ backgroundColor: color }}
      >
        {showName ? team : ''}
      </span>
    );
  }
  
  // Team-specific styling
  switch(teamCode) {
    case 'mi':
      badgeClasses = cn(badgeClasses, "bg-mi");
      break;
    case 'csk':
      badgeClasses = cn(badgeClasses, "bg-csk text-black");
      break;
    case 'rcb':
      badgeClasses = cn(badgeClasses, "bg-rcb");
      break;
    case 'kkr':
      badgeClasses = cn(badgeClasses, "bg-kkr");
      break;
    case 'dc':
      badgeClasses = cn(badgeClasses, "bg-dc");
      break;
    case 'rr':
      badgeClasses = cn(badgeClasses, "bg-rr");
      break;
    case 'pbks':
      badgeClasses = cn(badgeClasses, "bg-pbks");
      break;
    case 'srh':
      badgeClasses = cn(badgeClasses, "bg-srh text-black");
      break;
    case 'gt':
      badgeClasses = cn(badgeClasses, "bg-gt");
      break;
    case 'lsg':
      badgeClasses = cn(badgeClasses, "bg-lsg");
      break;
    default:
      badgeClasses = cn(badgeClasses, "bg-gray-700");
  }
  
  return (
    <span className={cn(badgeClasses, className)}>
      {showName ? team : ''}
    </span>
  );
};

export default TeamBadge; 