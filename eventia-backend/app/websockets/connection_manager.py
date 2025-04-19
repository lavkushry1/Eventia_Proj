"""
WebSocket Connection Manager
--------------------------
Manages WebSocket connections for real-time updates
"""

from typing import Dict, List, Any
from fastapi import WebSocket
from ..utils.logger import logger


class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates
    
    This class handles:
    - Connecting and disconnecting WebSocket clients
    - Grouping connections by stadium ID
    - Broadcasting messages to all clients or specific groups
    """
    
    def __init__(self):
        # Dictionary to store active connections grouped by stadium ID
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Dictionary to track connection count for logging/monitoring
        self.connection_count: Dict[str, int] = {}
    
    async def connect(self, websocket: WebSocket, stadium_id: str):
        """
        Connect a new WebSocket client
        
        Args:
            websocket: The WebSocket connection
            stadium_id: The stadium ID to associate with this connection
        """
        # Accept the connection
        await websocket.accept()
        
        # Add to active connections for this stadium
        if stadium_id not in self.active_connections:
            self.active_connections[stadium_id] = []
            self.connection_count[stadium_id] = 0
        
        self.active_connections[stadium_id].append(websocket)
        self.connection_count[stadium_id] += 1
        
        # Log connection
        logger.info(f"New WebSocket connection for stadium {stadium_id}. Total connections: {self.connection_count[stadium_id]}")
        
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection_established",
            "stadium_id": stadium_id,
            "message": "Connected to seat updates"
        })
    
    def disconnect(self, websocket: WebSocket, stadium_id: str):
        """
        Disconnect a WebSocket client
        
        Args:
            websocket: The WebSocket connection to disconnect
            stadium_id: The stadium ID associated with this connection
        """
        # Remove from active connections
        if stadium_id in self.active_connections:
            if websocket in self.active_connections[stadium_id]:
                self.active_connections[stadium_id].remove(websocket)
                self.connection_count[stadium_id] -= 1
                
                # Log disconnection
                logger.info(f"WebSocket disconnected from stadium {stadium_id}. Remaining connections: {self.connection_count[stadium_id]}")
                
                # Clean up if no more connections for this stadium
                if not self.active_connections[stadium_id]:
                    del self.active_connections[stadium_id]
                    del self.connection_count[stadium_id]
    
    async def broadcast_to_stadium(self, stadium_id: str, message: Dict[str, Any]):
        """
        Broadcast a message to all connections for a specific stadium
        
        Args:
            stadium_id: The stadium ID to broadcast to
            message: The message to broadcast
        """
        if stadium_id in self.active_connections:
            # Create a list to track failed connections for cleanup
            failed_connections = []
            
            # Send message to all connections for this stadium
            for connection in self.active_connections[stadium_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    # If sending fails, mark connection for removal
                    logger.error(f"Error sending message to WebSocket: {str(e)}")
                    failed_connections.append(connection)
            
            # Clean up failed connections
            for failed in failed_connections:
                self.disconnect(failed, stadium_id)
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """
        Broadcast a message to all connections
        
        Args:
            message: The message to broadcast
        """
        # Broadcast to all stadiums
        for stadium_id in list(self.active_connections.keys()):
            await self.broadcast_to_stadium(stadium_id, message)
    
    def get_connection_count(self, stadium_id: str = None) -> int:
        """
        Get the number of active connections
        
        Args:
            stadium_id: Optional stadium ID to get count for
            
        Returns:
            Number of active connections
        """
        if stadium_id:
            return self.connection_count.get(stadium_id, 0)
        else:
            return sum(self.connection_count.values())