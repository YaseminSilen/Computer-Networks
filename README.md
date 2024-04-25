# Multi-User File Transfer System

This project implements a multi-user file transfer system consisting of server-side and client-side components. The system allows multiple users to securely exchange files over a network connection.

## Server Side

### Overview
The server side is implemented in the `server.py` file. It utilizes the `Server` class, which initializes the server and handles incoming client requests.

### Functionality
- **Authentication**: Users are required to log in with a username and password.
- **Blocking Mechanism**: If a user enters the incorrect password multiple times, they are temporarily blocked by the system for security purposes.
- **Concurrent Sessions**: The server supports multiple simultaneous sessions, each handled by a separate thread.
- **Request Handling**: Incoming requests from clients are processed and routed to the appropriate functions for execution.

## Client Side

### Overview
The client side is implemented in the `client.py` file. It contains the `Main` class, responsible for establishing connections to the server and facilitating file transfers.

### Functionality
- **Authentication**: Users authenticate with the server by providing their username and password.
- **Session Management**: Upon successful authentication, users can initiate and manage sessions for file transfer.
- **File Transfer**: Users can send files to other users using the "UPD" command, which initiates a file transfer protocol with the server.
- **Real-time Updates**: The client periodically checks for incoming files and updates, ensuring prompt delivery of messages and files.

## Getting Started

1. **Server Setup**: Run the `server.py` file to start the server.
   ```bash
   python server.py
   ```

2. **Client Setup**: Run the `client.py` file to start a client session.
   ```bash
   python client.py
   ```

3. **Authentication**: Upon launching the client, users will be prompted to authenticate with their username and password.

4. **File Transfer**: Users can initiate file transfers using the "UPD" command followed by the filename.


## Usage

- Ensure that both the server and client scripts are executed within the same network environment.
- Follow the prompts on the client side to authenticate and initiate file transfers.

