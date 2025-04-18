import React, { useState, useEffect } from 'react';
import { ZoomIn, ZoomOut, RotateCw, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';

interface SeatMapSection {
  section_id: string;
  name: string;
  price: number;
  availability: number;
  color_code: string;
  is_vip: boolean;
  selected: number;
}

interface StadiumSeatMapProps {
  stadiumName: string;
  sections: SeatMapSection[];
  onSectionSelect: (sectionId: string, quantity: number) => void;
}

const StadiumSeatMap: React.FC<StadiumSeatMapProps> = ({
  stadiumName,
  sections,
  onSectionSelect,
}) => {
  const [zoom, setZoom] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading of the stadium map
    const timer = setTimeout(() => {
      setLoading(false);
    }, 1000);
    return () => clearTimeout(timer);
  }, []);

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 0.2, 2));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 0.2, 0.5));
  };

  const handleRotate = () => {
    setRotation(prev => prev + 45);
  };

  if (loading) {
    return (
      <div className="h-[400px] w-full flex items-center justify-center bg-gray-50 rounded-lg">
        <div className="flex flex-col items-center gap-2">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p>Loading stadium map...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative border rounded-lg overflow-hidden">
      <div className="bg-gray-100 p-3 border-b flex justify-between items-center">
        <h3 className="font-medium">{stadiumName} - Seat Map</h3>
        <div className="flex gap-1">
          <Button
            variant="outline"
            size="icon"
            className="h-8 w-8"
            onClick={handleZoomOut}
          >
            <ZoomOut className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="h-8 w-8"
            onClick={handleZoomIn}
          >
            <ZoomIn className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="h-8 w-8"
            onClick={handleRotate}
          >
            <RotateCw className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="relative h-[400px] overflow-hidden bg-gray-50">
        <div
          className="absolute inset-0 flex items-center justify-center"
          style={{
            transform: `scale(${zoom}) rotate(${rotation}deg)`,
            transformOrigin: 'center',
            transition: 'transform 0.3s ease'
          }}
        >
          {/* Stadium visualization */}
          <div className="relative">
            {/* Cricket pitch */}
            <div className="w-32 h-12 bg-green-600 rounded-full border-4 border-green-700 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-10"></div>
            
            <div className="w-[500px] h-[300px] border-[30px] border-gray-200 rounded-[50%] relative">
              {/* Render sections around the oval */}
              {sections.map((section, index) => {
                // Calculate position around the oval
                const angle = (index * (360 / sections.length) + rotation) % 360;
                const radius = 150; // distance from center
                const x = Math.cos((angle * Math.PI) / 180) * radius;
                const y = Math.sin((angle * Math.PI) / 180) * radius;
                
                return (
                  <TooltipProvider key={section.section_id}>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <div
                          className={cn(
                            "absolute w-24 h-12 flex items-center justify-center cursor-pointer",
                            "transform -translate-x-1/2 -translate-y-1/2 transition-all",
                            "border-2 font-medium text-white text-center text-sm",
                            section.selected > 0 ? "ring-2 ring-primary" : ""
                          )}
                          style={{
                            left: `calc(50% + ${x}px)`,
                            top: `calc(50% + ${y}px)`,
                            backgroundColor: section.color_code,
                            borderColor: section.is_vip ? 'gold' : section.color_code,
                          }}
                          onClick={() => {
                            const newQuantity = section.selected < section.availability 
                              ? section.selected + 1 
                              : 0;
                            onSectionSelect(section.section_id, newQuantity);
                          }}
                        >
                          <div className="flex flex-col">
                            <span>{section.name}</span>
                            {section.selected > 0 && (
                              <Badge variant="outline" className="bg-white text-black">
                                {section.selected}
                              </Badge>
                            )}
                          </div>
                        </div>
                      </TooltipTrigger>
                      <TooltipContent>
                        <div className="text-sm">
                          <p className="font-bold">{section.name}</p>
                          <p>Price: ₹{section.price}</p>
                          <p>Available: {section.availability}</p>
                          {section.is_vip && <p className="text-amber-500">VIP Section</p>}
                          {section.selected > 0 && <p className="text-primary">Selected: {section.selected}</p>}
                        </div>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      <div className="p-3 bg-gray-100 border-t">
        <div className="flex flex-wrap gap-2">
          {sections.map(section => (
            <div 
              key={section.section_id}
              className="flex items-center gap-1"
            >
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: section.color_code }}
              ></div>
              <span className="text-xs">
                {section.name} (₹{section.price})
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default StadiumSeatMap; 