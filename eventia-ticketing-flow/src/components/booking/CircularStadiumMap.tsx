import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { cn } from '@/lib/utils';

interface StadiumSection {
  section_id: string;
  name: string;
  price: number;
  availability: number;
  color_code: string;
  is_vip: boolean;
  selected?: number;
}

interface CircularStadiumMapProps {
  stadiumName: string;
  sections: StadiumSection[];
  onSectionSelect: (sectionId: string, quantity: number) => void;
  totalAmount: number;
  totalTickets: number;
  timeRemaining?: number; // in seconds, for countdown timer
}

const CircularStadiumMap: React.FC<CircularStadiumMapProps> = ({
  stadiumName,
  sections,
  onSectionSelect,
  totalAmount,
  totalTickets,
  timeRemaining
}) => {
  const [zoom, setZoom] = useState(1);
  
  // Format time remaining in minutes:seconds
  const formatTimeRemaining = () => {
    if (!timeRemaining) return null;
    const minutes = Math.floor(timeRemaining / 60);
    const seconds = timeRemaining % 60;
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
  };

  return (
    <div className="flex flex-col space-y-4">
      {/* Timer bar if time remaining is provided */}
      {timeRemaining !== undefined && (
        <div className="bg-indigo-900 text-white py-3 px-4 rounded-md">
          <div className="text-center">
            <span className="font-medium">You have approximately {Math.floor(timeRemaining / 60)} minutes</span> to select your seats.
          </div>
        </div>
      )}

      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold">{stadiumName}</h3>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setZoom(Math.max(zoom - 0.1, 0.6))}
          >
            -
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setZoom(Math.min(zoom + 0.1, 1.5))}
          >
            +
          </Button>
        </div>
      </div>

      {/* Stadium visualization container */}
      <div className="relative h-[500px] border rounded-lg overflow-hidden bg-gray-50 flex items-center justify-center">
        <div
          className="absolute inset-0 flex items-center justify-center"
          style={{
            transform: `scale(${zoom})`,
            transformOrigin: 'center',
            transition: 'transform 0.3s ease'
          }}
        >
          {/* Stadium pitch (center) */}
          <div className="relative">
            <div className="w-40 h-16 bg-green-500 rounded-full absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-10 flex items-center justify-center">
              <div className="w-32 h-8 bg-green-300 rounded-full"></div>
            </div>
            
            {/* Circular stadium shape */}
            <div className="w-[500px] h-[320px] relative rounded-[50%] border-[30px] border-gray-200">
              {/* Place sections around the stadium */}
              {sections.map((section, index) => {
                // Calculate position around the oval
                const angle = (index * (360 / sections.length)) % 360;
                const radius = 135; // distance from center
                
                // Calculate position using trigonometry
                const x = Math.cos((angle * Math.PI) / 180) * radius;
                const y = Math.sin((angle * Math.PI) / 180) * radius;
                
                // Calculate rotation so text is readable
                const textRotation = angle > 90 && angle < 270 ? 180 : 0;
                
                return (
                  <div
                    key={section.section_id}
                    className={cn(
                      "absolute w-24 h-16 flex items-center justify-center cursor-pointer rounded-md",
                      "transform -translate-x-1/2 -translate-y-1/2 transition-all duration-200",
                      "border-2 font-medium text-white text-center text-sm",
                      section.selected && section.selected > 0 ? "ring-2 ring-primary" : ""
                    )}
                    style={{
                      left: `calc(50% + ${x}px)`,
                      top: `calc(50% + ${y}px)`,
                      backgroundColor: section.color_code || '#2563EB',
                      borderColor: section.is_vip ? 'gold' : section.color_code || '#2563EB',
                      transform: `translate(-50%, -50%) rotate(${angle}deg)`,
                    }}
                    onClick={() => {
                      const newQuantity = section.selected && section.selected < section.availability 
                        ? section.selected + 1 
                        : 0;
                      onSectionSelect(section.section_id, newQuantity);
                    }}
                  >
                    <div 
                      className="flex flex-col items-center"
                      style={{ transform: `rotate(${-angle + textRotation}deg)` }}
                    >
                      <span className="whitespace-nowrap overflow-hidden text-ellipsis max-w-[90px]">
                        {section.name}
                      </span>
                      {section.selected && section.selected > 0 && (
                        <Badge variant="outline" className="bg-white text-black mt-1">
                          {section.selected}
                        </Badge>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Section legend */}
      <div className="p-3 bg-gray-100 border rounded-lg">
        <div className="text-sm font-medium mb-2">Sections:</div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
          {sections.map(section => (
            <div 
              key={section.section_id}
              className="flex items-center gap-1"
            >
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: section.color_code }}
              ></div>
              <span className="text-xs truncate">
                {section.name} (₹{section.price})
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Selection summary */}
      {totalTickets > 0 && (
        <div className="border rounded-md p-4 bg-white">
          <div className="flex justify-between items-center">
            <div>
              <div className="text-sm text-gray-500">Selected seats: {totalTickets}</div>
              <div className="text-xl font-bold">Total: ₹{totalAmount.toLocaleString()}</div>
            </div>
            <Button>Continue to Checkout</Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CircularStadiumMap; 