# Distributed File System

A robust, fault-tolerant distributed file system implementation with master-slave architecture, file replication, and concurrent access control.

## 🏗️ System Architecture

### Components

1. **Master Server** (`master_server.py`)
   - Central metadata management
   - Chunk server registration and coordination
   - Primary server selection and updates
   - Client request routing

2. **Chunk Servers** (3 instances)
   - `chunk_server1.py` - Port 6001, ID 1
   - `chunk_server2.py` - Port 6002, ID 2  
   - `chunk_server3.py` - Port 6003, ID 3
   - Local file storage and management
   - File operations (create, read, write, delete)
   - Concurrent access control with file locking

3. **Clients** (2 instances)
   - `client1.py` - Client application 1
   - `client2.py` - Client application 2
   - File operation requests to chunk servers

4. **Supporting Components**
   - `master_server_heartbeat.py` - Master server health monitoring
   - `file_server_heartbeat.py` - Chunk server health monitoring
   - `node_failure.py` - Failure detection and recovery
   - `metadata.json` - System metadata storage

## 🚀 Features

### Core Functionality
- **File Operations**: Create, read, write, and delete files
- **Concurrent Access**: Thread-safe file operations with locking
- **Fault Tolerance**: Replication and failure detection
- **Load Balancing**: Distributed file storage across multiple servers
- **Metadata Management**: Centralized file location tracking

### Advanced Features
- **File Locking**: Prevents concurrent write conflicts
- **Performance Monitoring**: Request timing and logging
- **Health Monitoring**: Heartbeat mechanisms for server health
- **Error Handling**: Comprehensive timeout and exception management
- **Backup System**: Local file copies for data protection

## 📋 Prerequisites

- Python 3.7+
- Socket programming support
- Threading support
- File system access

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Jay2704/distributed_file_system.git
cd distributed_file_system
```

### 2. Start the Master Server
```bash
python master_server.py
```
The master server will start on `127.0.0.1:5011`

### 3. Start Chunk Servers
Open separate terminal windows for each chunk server:

```bash
# Terminal 1 - Chunk Server 1
python chunk_server1.py

# Terminal 2 - Chunk Server 2  
python chunk_server2.py

# Terminal 3 - Chunk Server 3
python chunk_server3.py
```

### 4. Start Clients
```bash
# Terminal 4 - Client 1
python client1.py

# Terminal 5 - Client 2
python client2.py
```

## 📖 Usage

### File Operations

The system supports the following file operations:

#### Create File
```python
# Client sends: CREATE_FILE:filename
# Response: FILE_CREATED
```

#### Write File
```python
# Client sends: WRITE_FILE:filename:content
# Response: FILE_WRITTEN
```

#### Read File
```python
# Client sends: READ_FILE:filename
# Response: FILE_CONTENT:content or FILE_NOT_FOUND
```

#### Delete File
```python
# Client sends: DELETE_FILE:filename
# Response: FILE_DELETED or FILE_NOT_FOUND
```

### Example Client Usage
```python
# Connect to chunk server
# Send file operations
# Receive responses
```

## 🔧 Configuration

### Port Configuration
- **Master Server**: 5011
- **Chunk Server 1**: 6001
- **Chunk Server 2**: 6002
- **Chunk Server 3**: 6003

### Directory Structure
```
distributed_file_system/
├── chunk_server_1_directory/
├── chunk_server_2_directory/
├── chunk_server_3_directory/
├── master_server.py
├── chunk_server1.py
├── chunk_server2.py
├── chunk_server3.py
├── client1.py
├── client2.py
└── README.md
```

## 🏛️ System Design

### Master-Slave Architecture
- **Master Server**: Central coordinator managing metadata and chunk server registration
- **Chunk Servers**: Distributed storage nodes handling file operations
- **Clients**: Applications requesting file operations

### File Locking Mechanism
- Prevents concurrent write conflicts
- Ensures data consistency
- Supports multiple client connections

### Replication Strategy
- Primary server selection for redundancy
- Backup file creation during write operations
- Fault tolerance through multiple chunk servers

## 🔍 Monitoring & Debugging

### Health Monitoring
- Heartbeat mechanisms for server health checks
- Failure detection and recovery
- Performance metrics logging

### Logging
- Request timing and performance metrics
- Error handling and exception logging
- File operation status tracking

## 🚨 Error Handling

### Common Error Responses
- `FILE_LOCKED_ERROR`: File is currently locked by another client
- `FILE_NOT_FOUND`: Requested file doesn't exist
- `TIMEOUT_ERROR`: Operation exceeded timeout limit
- `COPY_ERROR`: Backup creation failed

### Recovery Mechanisms
- Automatic retry mechanisms
- Graceful degradation on server failures
- Data consistency checks

## 🔒 Security Features

- File access control through locking
- Concurrent access prevention
- Data integrity through backup mechanisms
- Error isolation and recovery

## 📊 Performance

### Space Complexity
- O(2*N) for file storage with replication
- Efficient metadata management
- Optimized file locking mechanisms

### Time Complexity
- O(1) for most file operations
- Thread-safe concurrent access
- Minimal latency for distributed operations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add comprehensive comments
5. Test thoroughly
6. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

**Jay2704** - Distributed Systems Implementation

## 🔗 Repository

GitHub: https://github.com/Jay2704/distributed_file_system

---

*This distributed file system demonstrates key concepts in distributed computing, fault tolerance, and concurrent programming.*
