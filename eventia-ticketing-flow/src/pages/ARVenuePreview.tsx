
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group';
import { Card, CardContent } from '@/components/ui/card';
import { ArrowLeft, View, Eye, Maximize2, Minimize2, RotateCw, ChevronUp, ChevronDown, Smartphone } from 'lucide-react';
import { toast } from '@/hooks/use-toast';

const ARVenuePreview = () => {
  const { id } = useParams();
  const [loading, setLoading] = useState(true);
  const [zoomLevel, setZoomLevel] = useState([50]);
  const [viewMode, setViewMode] = useState('3d');
  const [currentSection, setCurrentSection] = useState('premium');
  const [rotationAngle, setRotationAngle] = useState(0);
  const [showControls, setShowControls] = useState(true);

  useEffect(() => {
    // Simulate loading the 3D model
    const timer = setTimeout(() => {
      setLoading(false);
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  const handleRotate = (direction: 'left' | 'right') => {
    setRotationAngle(prev => {
      const newAngle = direction === 'left' ? prev - 45 : prev + 45;
      return newAngle % 360;
    });
  };

  const toggleAR = () => {
    // In a real app, this would initiate the AR experience
    toast({
      title: "AR Mode",
      description: "Point your camera at a flat surface to place the stadium model.",
    });
  };

  const stadiumSections = [
    { id: 'premium', name: 'Premium Stand', price: '₹4,500' },
    { id: 'vip', name: 'VIP Lounge', price: '₹8,000' },
    { id: 'general', name: 'General Stand', price: '₹2,500' },
    { id: 'east', name: 'East Wing', price: '₹3,200' },
    { id: 'west', name: 'West Wing', price: '₹3,500' },
  ];

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      
      <main className="flex-grow pt-16 pb-12 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="mb-6 flex items-center">
            <Button variant="ghost" onClick={() => window.history.back()} className="mr-4">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Stadium AR Preview</h1>
              <p className="text-sm text-gray-600">Experience the venue before booking your tickets</p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Card className="overflow-hidden">
                <div className="relative bg-black rounded-t-lg">
                  {loading ? (
                    <div className="aspect-video bg-gray-900 flex items-center justify-center">
                      <div className="text-center">
                        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-primary border-r-transparent motion-reduce:animate-[spin_1.5s_linear_infinite] mb-4"></div>
                        <p className="text-white">Loading 3D model...</p>
                      </div>
                    </div>
                  ) : (
                    <div 
                      className="aspect-video bg-gradient-to-b from-blue-900 to-blue-950 flex items-center justify-center overflow-hidden"
                      style={{ perspective: '1000px' }}
                    >
                      <div 
                        className="relative w-4/5 h-4/5 transition-transform duration-500"
                        style={{ 
                          transform: `rotateY(${rotationAngle}deg) scale(${zoomLevel[0] / 50})`,
                          transformStyle: 'preserve-3d'
                        }}
                      >
                        {/* 3D stadium mockup */}
                        <div className="absolute inset-0 bg-white/5 border border-white/10 rounded-lg flex items-center justify-center">
                          <div className="text-center p-6">
                            <div className="w-full h-32 border-2 border-primary/30 rounded-full mx-auto mb-4 flex items-center justify-center">
                              <div className="w-3/4 h-20 border-2 border-primary/40 rounded-full flex items-center justify-center">
                                <div className="w-1/2 h-10 bg-primary/20 border border-primary/50 rounded-md"></div>
                              </div>
                            </div>
                            <div className={`text-white text-xl font-bold transition-opacity duration-300 ${currentSection === 'premium' ? 'opacity-100' : 'opacity-30'}`}>
                              {stadiumSections.find(s => s.id === currentSection)?.name || 'Premium Stand'}
                            </div>
                          </div>
                        </div>
                        
                        {/* Highlighted section based on selection */}
                        {currentSection === 'premium' && (
                          <div className="absolute top-1/4 left-1/2 w-16 h-16 -ml-8 -mt-8 bg-primary/40 rounded-full animate-pulse"></div>
                        )}
                        {currentSection === 'vip' && (
                          <div className="absolute top-1/2 left-1/4 w-16 h-16 -ml-8 -mt-8 bg-yellow-500/40 rounded-full animate-pulse"></div>
                        )}
                        {currentSection === 'general' && (
                          <div className="absolute bottom-1/4 left-1/2 w-16 h-16 -ml-8 -mt-8 bg-blue-500/40 rounded-full animate-pulse"></div>
                        )}
                        {currentSection === 'east' && (
                          <div className="absolute top-1/2 right-1/4 w-16 h-16 -ml-8 -mt-8 bg-green-500/40 rounded-full animate-pulse"></div>
                        )}
                        {currentSection === 'west' && (
                          <div className="absolute top-1/2 left-3/4 w-16 h-16 -ml-8 -mt-8 bg-purple-500/40 rounded-full animate-pulse"></div>
                        )}
                      </div>
                    </div>
                  )}
                  
                  {/* Toggle controls visibility on mobile */}
                  <Button 
                    variant="secondary" 
                    size="sm"
                    className="absolute bottom-4 left-1/2 transform -translate-x-1/2 md:hidden"
                    onClick={() => setShowControls(prev => !prev)}
                  >
                    {showControls ? <ChevronDown className="h-4 w-4" /> : <ChevronUp className="h-4 w-4" />}
                    {showControls ? 'Hide Controls' : 'Show Controls'}
                  </Button>
                </div>
                
                <CardContent className={`bg-gray-900 text-white p-4 transition-all duration-300 ${showControls ? 'max-h-96' : 'max-h-0 overflow-hidden p-0 md:max-h-96 md:p-4'}`}>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div>
                        <label className="text-sm font-medium text-gray-300 mb-2 block">View Mode</label>
                        <ToggleGroup type="single" value={viewMode} onValueChange={(value) => value && setViewMode(value)} className="border border-gray-700 rounded-md">
                          <ToggleGroupItem value="3d" className="data-[state=on]:bg-primary/20 data-[state=on]:text-primary-foreground">
                            <View className="h-4 w-4 mr-2" />
                            3D View
                          </ToggleGroupItem>
                          <ToggleGroupItem value="seat" className="data-[state=on]:bg-primary/20 data-[state=on]:text-primary-foreground">
                            <Eye className="h-4 w-4 mr-2" />
                            Seat View
                          </ToggleGroupItem>
                        </ToggleGroup>
                      </div>
                      
                      <div>
                        <label className="text-sm font-medium text-gray-300 mb-2 block">Zoom Level</label>
                        <div className="flex items-center space-x-2">
                          <Minimize2 className="h-4 w-4 text-gray-400" />
                          <Slider
                            value={zoomLevel}
                            onValueChange={setZoomLevel}
                            max={100}
                            step={1}
                            className="flex-grow"
                          />
                          <Maximize2 className="h-4 w-4 text-gray-400" />
                        </div>
                      </div>
                      
                      <div>
                        <label className="text-sm font-medium text-gray-300 mb-2 block">Rotation</label>
                        <div className="flex items-center justify-between">
                          <Button variant="outline" size="sm" onClick={() => handleRotate('left')}>
                            <RotateCw className="h-4 w-4 mr-2" />
                            Rotate Left
                          </Button>
                          <span className="text-sm text-gray-400">{rotationAngle}°</span>
                          <Button variant="outline" size="sm" onClick={() => handleRotate('right')}>
                            <RotateCw className="h-4 w-4 mr-2" />
                            Rotate Right
                          </Button>
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <div>
                        <label className="text-sm font-medium text-gray-300 mb-2 block">Select Stadium Section</label>
                        <div className="grid grid-cols-1 gap-2">
                          {stadiumSections.map((section) => (
                            <Button
                              key={section.id}
                              variant="outline"
                              size="sm"
                              className={`justify-between ${currentSection === section.id ? 'border-primary text-primary' : 'border-gray-700 text-gray-300'}`}
                              onClick={() => setCurrentSection(section.id)}
                            >
                              <span>{section.name}</span>
                              <span className="text-xs font-normal">{section.price}</span>
                            </Button>
                          ))}
                        </div>
                      </div>
                      
                      <Button onClick={toggleAR} className="w-full mt-4">
                        <Smartphone className="h-4 w-4 mr-2" />
                        View in AR on Your Device
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
            
            <div>
              <Card>
                <CardContent className="p-6">
                  <div className="text-center mb-6">
                    <h3 className="text-xl font-bold mb-2">Ready to Book Tickets?</h3>
                    <p className="text-gray-600 text-sm">
                      Now that you've previewed the venue, secure your seats before they sell out!
                    </p>
                  </div>
                  
                  <div className="space-y-4">
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <div className="text-sm text-gray-600 mb-1">Selected Section</div>
                      <div className="font-bold">
                        {stadiumSections.find(s => s.id === currentSection)?.name || 'Premium Stand'}
                      </div>
                      <div className="text-primary font-medium">
                        {stadiumSections.find(s => s.id === currentSection)?.price || '₹4,500'}
                      </div>
                    </div>
                    
                    <Link to={`/event/${id}`}>
                      <Button className="w-full">
                        Book Tickets Now
                      </Button>
                    </Link>
                    
                    <Button variant="outline" className="w-full" onClick={() => setCurrentSection('premium')}>
                      Explore Other Sections
                    </Button>
                  </div>
                  
                  <div className="mt-8 border-t border-gray-200 pt-6">
                    <h4 className="font-medium mb-3">Section Information</h4>
                    <div className="space-y-2 text-sm">
                      <p className="flex items-start">
                        <span className="flex-shrink-0 h-5 w-5 bg-primary/10 rounded-full flex items-center justify-center text-primary mr-2 text-xs">✓</span>
                        Best visibility of the entire field
                      </p>
                      <p className="flex items-start">
                        <span className="flex-shrink-0 h-5 w-5 bg-primary/10 rounded-full flex items-center justify-center text-primary mr-2 text-xs">✓</span>
                        Comfortable seating with extra legroom
                      </p>
                      <p className="flex items-start">
                        <span className="flex-shrink-0 h-5 w-5 bg-primary/10 rounded-full flex items-center justify-center text-primary mr-2 text-xs">✓</span>
                        Access to exclusive refreshment area
                      </p>
                      <p className="flex items-start">
                        <span className="flex-shrink-0 h-5 w-5 bg-primary/10 rounded-full flex items-center justify-center text-primary mr-2 text-xs">✓</span>
                        Covered seating protected from weather
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default ARVenuePreview;
