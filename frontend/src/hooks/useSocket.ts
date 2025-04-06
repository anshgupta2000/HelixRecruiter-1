import { useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';

// The base URL for the API
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const useSocket = (): Socket | null => {
  const [socket, setSocket] = useState<Socket | null>(null);

  useEffect(() => {
    // Create a socket connection
    const socketIo = io(API_URL, {
      transports: ['websocket'],
      autoConnect: true,
    });

    // Set the socket state
    setSocket(socketIo);

    // Clean up the socket connection on unmount
    return () => {
      socketIo.disconnect();
    };
  }, []);

  return socket;
};
