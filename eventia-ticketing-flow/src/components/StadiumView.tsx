import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useStadium, useSeatViewImages } from '../hooks/use-stadiums';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle, Calendar, Map, MapPin, Users } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

const StadiumView = () => {
  const { stadiumId } = useParams<{ stadiumId: string }>();
  const { data: stadium, isLoading, error } = useStadium(stadiumId || '');
  
  // Default to the first section for seat view
  const [selectedSection, setSelectedSection] = React.useState<string>('');
  
  // Fetch seat view images for selected section
  const {
    data: seatViewData,
    isLoading: isLoadingSeatViews,
    error: seatViewError
  } = useSeatViewImages(
    stadiumId || '',
    selectedSection || ''
  );
  
  // When stadium data loads, select the first section by default
  React.useEffect(() => {
    if (stadium?.sections && stadium.sections.length > 0 && !selectedSection) {
      setSelectedSection(stadium.sections[0].section_id);
    }
  }, [stadium, selectedSection]);

  if (isLoading) {
    return <StadiumSkeleton />;
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>
          Failed to load stadium information. Please try again later.
        </AlertDescription>
      </Alert>
    );
  }

  if (!stadium) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Stadium Not Found</AlertTitle>
        <AlertDescription>
          The stadium you're looking for could not be found.
          <Link to="/stadiums" className="ml-2 underline">
            View all stadiums
          </Link>
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex flex-col md:flex-row gap-8">
        {/* Stadium Info */}
        <div className="w-full md:w-1/2">
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl font-bold">{stadium.name}</CardTitle>
              <CardDescription className="flex items-center">
                <MapPin className="h-4 w-4 mr-1" />
                {stadium.city}, {stadium.country}
              </CardDescription>
            </CardHeader>
            
            <CardContent>
              <div className="relative w-full h-64 mb-4 overflow-hidden rounded-lg">
                <img 
                  src={stadium.image_url} 
                  alt={stadium.name}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    target.src = '/assets/placeholder-stadium.jpg';
                  }}
                />
              </div>
              
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-semibold mb-2">About the Stadium</h3>
                  <p>{stadium.description || 'No description available.'}</p>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold mb-2">Capacity</h3>
                  <div className="flex items-center">
                    <Users className="h-5 w-5 mr-2" />
                    <span>{stadium.capacity.toLocaleString()} seats</span>
                  </div>
                </div>
                
                {stadium.facilities && stadium.facilities.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Facilities</h3>
                    <div className="flex flex-wrap gap-2">
                      {stadium.facilities.map((facility, index) => (
                        <Badge key={index} variant="outline" className="flex items-center gap-1">
                          {facility.icon && <img src={`/assets/icons/${facility.icon}`} alt="" className="w-4 h-4" />}
                          {facility.name}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Stadium Sections and Seat Views */}
        <div className="w-full md:w-1/2">
          <Card>
            <CardHeader>
              <CardTitle className="text-xl font-bold">Stadium Sections</CardTitle>
              <CardDescription>
                Select a section to view details and seat views
              </CardDescription>
            </CardHeader>
            
            <CardContent>
              {stadium.sections && stadium.sections.length > 0 ? (
                <Tabs defaultValue={selectedSection} onValueChange={setSelectedSection}>
                  <TabsList className="w-full mb-4">
                    {stadium.sections.map((section) => (
                      <TabsTrigger 
                        key={section.section_id} 
                        value={section.section_id}
                        className="flex-1"
                        style={{ 
                          borderBottom: `3px solid ${section.color_code || '#e2e8f0'}`
                        }}
                      >
                        {section.name}
                      </TabsTrigger>
                    ))}
                  </TabsList>
                  
                  {stadium.sections.map((section) => (
                    <TabsContent key={section.section_id} value={section.section_id}>
                      <div className="space-y-4">
                        <div className="flex flex-wrap justify-between items-center gap-2">
                          <div>
                            <span className="text-sm text-gray-500">Capacity</span>
                            <p className="font-medium">{section.capacity.toLocaleString()} seats</p>
                          </div>
                          <div>
                            <span className="text-sm text-gray-500">Price</span>
                            <p className="font-medium">₹{section.price.toLocaleString()}</p>
                          </div>
                          <div>
                            <span className="text-sm text-gray-500">Available</span>
                            <p className="font-medium">{section.availability.toLocaleString()} seats</p>
                          </div>
                          {section.is_vip && (
                            <Badge variant="secondary">VIP</Badge>
                          )}
                        </div>
                        
                        <div>
                          <p className="text-sm">{section.description || 'No description available for this section.'}</p>
                        </div>
                        
                        {/* Seat Views for this section */}
                        <div>
                          <h3 className="text-lg font-semibold mb-2">Seat Views</h3>
                          {isLoadingSeatViews ? (
                            <div className="space-y-2">
                              <Skeleton className="h-40 w-full rounded-lg" />
                              <Skeleton className="h-4 w-3/4" />
                            </div>
                          ) : seatViewError ? (
                            <Alert>
                              <AlertCircle className="h-4 w-4" />
                              <AlertDescription>
                                Failed to load seat views. Please try again.
                              </AlertDescription>
                            </Alert>
                          ) : seatViewData?.views && seatViewData.views.length > 0 ? (
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                              {seatViewData.views.map((view) => (
                                <div key={view.view_id} className="overflow-hidden rounded-lg">
                                  <img 
                                    src={view.image_url} 
                                    alt={view.description || 'Seat view'} 
                                    className="w-full h-40 object-cover hover:scale-105 transition-transform"
                                    onClick={() => window.open(view.image_url, '_blank')}
                                    onError={(e) => {
                                      const target = e.target as HTMLImageElement;
                                      target.src = '/assets/placeholder-seat-view.jpg';
                                    }}
                                  />
                                  <p className="text-sm mt-1 text-center">{view.description || 'View from this section'}</p>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <div className="text-center py-6 border rounded-lg">
                              <p className="text-gray-500">No seat views available for this section</p>
                            </div>
                          )}
                        </div>
                      </div>
                    </TabsContent>
                  ))}
                </Tabs>
              ) : (
                <div className="text-center py-6 border rounded-lg">
                  <p className="text-gray-500">No sections available for this stadium</p>
                </div>
              )}
            </CardContent>
            
            <CardFooter>
              <Button asChild variant="outline" className="w-full">
                <Link to="/stadiums">View All Stadiums</Link>
              </Button>
            </CardFooter>
          </Card>
        </div>
      </div>
    </div>
  );
};

// Skeleton loader for the stadium view
const StadiumSkeleton = () => (
  <div className="container mx-auto px-4 py-8">
    <div className="flex flex-col md:flex-row gap-8">
      <div className="w-full md:w-1/2">
        <Card>
          <CardHeader>
            <Skeleton className="h-8 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
          </CardHeader>
          
          <CardContent>
            <Skeleton className="h-64 w-full mb-4 rounded-lg" />
            <div className="space-y-4">
              <div>
                <Skeleton className="h-6 w-1/3 mb-2" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-2/3" />
              </div>
              
              <div>
                <Skeleton className="h-6 w-1/4 mb-2" />
                <Skeleton className="h-4 w-1/3" />
              </div>
              
              <div>
                <Skeleton className="h-6 w-1/4 mb-2" />
                <div className="flex flex-wrap gap-2">
                  <Skeleton className="h-8 w-24 rounded-full" />
                  <Skeleton className="h-8 w-24 rounded-full" />
                  <Skeleton className="h-8 w-24 rounded-full" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      
      <div className="w-full md:w-1/2">
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-2/3" />
            <Skeleton className="h-4 w-1/2" />
          </CardHeader>
          
          <CardContent>
            <div className="mb-4">
              <Skeleton className="h-10 w-full" />
            </div>
            
            <div className="space-y-4">
              <div className="flex flex-wrap justify-between items-center gap-2">
                <Skeleton className="h-12 w-24" />
                <Skeleton className="h-12 w-24" />
                <Skeleton className="h-12 w-24" />
              </div>
              
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-5/6" />
              
              <div>
                <Skeleton className="h-6 w-1/3 mb-2" />
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <Skeleton className="h-40 w-full rounded-lg" />
                  <Skeleton className="h-40 w-full rounded-lg" />
                </div>
              </div>
            </div>
          </CardContent>
          
          <CardFooter>
            <Skeleton className="h-10 w-full" />
          </CardFooter>
        </Card>
      </div>
    </div>
  </div>
);

export default StadiumView;