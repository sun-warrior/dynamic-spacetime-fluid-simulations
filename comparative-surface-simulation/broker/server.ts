// Copyright 2026 Rohit Vasant Khakhrodiya
// SPDX-License-Identifier: Apache-2.0

import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import * as zmq from 'zeromq'; 

const app = express();
const httpServer = createServer(app);

const io = new Server(httpServer, {
  cors: {
    origin: "*", 
    methods: ["GET", "POST"]
  }
});

async function runBroker() {
  const tensorSocket = new zmq.Subscriber();
  const paramSocket = new zmq.Push();

  // Connect the sockets
  tensorSocket.connect('tcp://127.0.0.1:5555');
  paramSocket.connect('tcp://127.0.0.1:5556');
  tensorSocket.subscribe('');
  
  console.log('✅ ZMQ: Connected to Python Tensor Stream (Port 5555)');
  console.log('✅ ZMQ: Connected to Python Parameter Listener (Port 5556)');

  io.on('connection', (socket) => {
    console.log(`🔌 Frontend connected: ${socket.id}`);

    socket.on('update_params', async (uiParameters) => {
      try {
        await paramSocket.send(JSON.stringify(uiParameters));
      } catch (error) {
        console.error('Error sending parameters to Python:', error);
      }
    });

    socket.on('disconnect', () => {
      console.log(`❌ Frontend disconnected: ${socket.id}`);
    });
  });

  for await (const [msg] of tensorSocket) {
    try {
      // Parse and forward directly to the frontend
      const tensorData = JSON.parse(msg.toString());
      io.emit('tensor_stream', tensorData);
    } catch (error) {
      console.error('Failed to parse incoming ZMQ message.', error);
    }
  }
}

const PORT = process.env.PORT || 3000;
httpServer.listen(PORT, () => {
  console.log(`🚀 Node.js Broker running on http://localhost:${PORT}`);
});

runBroker().catch(err => {
  console.error('Broker encountered a fatal error:', err);
  process.exit(1);
});