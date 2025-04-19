import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface StadiumFallbackViewProps {
  onRetry: () => void;
  stadiumName?: string;
  error?: string;
}

/**
 * A fallback component that displays when the stadium view fails to render
 * This provides users with a graceful error experience
 */
const StadiumFallbackView: React.FC<StadiumFallbackViewProps> = ({
  onRetry,
  stadiumName = 'Stadium',
  error = 'We encountered an issue loading the seat selection view.'
}) => {
  return (
    <Card className="w-full border-amber-200 bg-amber-50">
      <CardHeader>
        <CardTitle className="flex items-center text-amber-800">
          <AlertTriangle className="h-5 w-5 mr-2 text-amber-600" />
          {stadiumName} Seat View Issue
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <p className="text-amber-700">
            {error} This could be due to one of the following reasons:
          </p>
          
          <ul className="list-disc pl-5 text-amber-700 space-y-1">
            <li>The stadium data is temporarily unavailable</li>
            <li>There was a network issue loading the seat map</li>
            <li>Your device might not support all the required graphics features</li>
            <li>The browser might be having trouble displaying the interactive elements</li>
          </ul>
          
          <div className="bg-white p-3 rounded-md border border-amber-200 mt-4">
            <h4 className="font-medium mb-2 text-amber-800">You can try:</h4>
            <div className="space-y-3">
              <div className="flex">
                <Button 
                  variant="outline" 
                  className="w-full border-amber-300 text-amber-800 hover:bg-amber-100"
                  onClick={onRetry}
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Retry Loading Seat Map
                </Button>
              </div>
              
              <p className="text-amber-600 text-sm">
                If the problem persists, try using the List View mode instead, which provides
                a simpler interface for selecting seats.
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default StadiumFallbackView; 