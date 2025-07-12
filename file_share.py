import os
import asyncio
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from motor.motor_asyncio import AsyncIOMotorClient
import json

class FileTransferStatus(Enum):
    PENDING = "pending"
    TRANSFERRING = "transferring"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING = "waiting"

@dataclass
class FileChunk:
    chunk_id: int
    data: bytes
    checksum: str
    size: int

@dataclass
class FileTransferInfo:
    transfer_id: str
    sender: str
    receiver: str = None  # None for group transfers
    group_name: str = None
    filename: str = ""
    file_size: int = 0
    chunks_total: int = 0
    chunks_sent: int = 0
    chunks_received: int = 0
    status: FileTransferStatus = FileTransferStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    file_path: str = ""
    checksum: str = ""
    priority: int = 0  # Higher priority gets preference

class FlowControlManager:
    def __init__(self, max_concurrent_transfers: int = 3, max_bandwidth_per_user: int = 1024 * 1024):  # 1MB/s per user
        self.max_concurrent_transfers = max_concurrent_transfers
        self.max_bandwidth_per_user = max_bandwidth_per_user
        self.active_transfers: Dict[str, List[str]] = {}  # user -> list of transfer_ids
        self.bandwidth_usage: Dict[str, int] = {}  # user -> bytes per second
        self.last_bandwidth_reset = time.time()
        
    def can_start_transfer(self, user: str) -> bool:
        current_transfers = len(self.active_transfers.get(user, []))
        return current_transfers < self.max_concurrent_transfers
    
    def add_transfer(self, user: str, transfer_id: str):
        if user not in self.active_transfers:
            self.active_transfers[user] = []
        self.active_transfers[user].append(transfer_id)
    
    def remove_transfer(self, user: str, transfer_id: str):
        if user in self.active_transfers:
            if transfer_id in self.active_transfers[user]:
                self.active_transfers[user].remove(transfer_id)
    
    def update_bandwidth_usage(self, user: str, bytes_transferred: int):
        current_time = time.time()
        if current_time - self.last_bandwidth_reset > 1.0:  # Reset every second
            self.bandwidth_usage.clear()
            self.last_bandwidth_reset = current_time
        
        if user not in self.bandwidth_usage:
            self.bandwidth_usage[user] = 0
        self.bandwidth_usage[user] += bytes_transferred
    
    def get_transfer_delay(self, user: str) -> float:
        """Calculate delay based on current bandwidth usage"""
        current_usage = self.bandwidth_usage.get(user, 0)
        if current_usage > self.max_bandwidth_per_user:
            # Calculate delay to throttle the transfer
            excess = current_usage - self.max_bandwidth_per_user
            return min(excess / self.max_bandwidth_per_user, 2.0)  # Max 2 second delay
        return 0.0

class CongestionControlManager:
    def __init__(self, max_system_bandwidth: int = 5 * 1024 * 1024):  # 5MB/s system-wide
        self.max_system_bandwidth = max_system_bandwidth
        self.current_system_load = 0
        self.transfer_queue: List[str] = []  # Queue for waiting transfers
        self.active_system_transfers: Set[str] = set()
        
    def can_start_system_transfer(self) -> bool:
        return self.current_system_load < self.max_system_bandwidth
    
    def add_to_queue(self, transfer_id: str):
        if transfer_id not in self.transfer_queue:
            self.transfer_queue.append(transfer_id)
    
    def remove_from_queue(self, transfer_id: str):
        if transfer_id in self.transfer_queue:
            self.transfer_queue.remove(transfer_id)
    
    def get_next_transfer(self) -> Optional[str]:
        if self.transfer_queue and self.can_start_system_transfer():
            return self.transfer_queue.pop(0)
        return None
    
    def update_system_load(self, load_change: int):
        self.current_system_load = max(0, self.current_system_load + load_change)

class FileTransferManager:
    def __init__(self, db_client: AsyncIOMotorClient, upload_dir: str = "uploads"):
        self.db = db_client.chatapp
        self.file_transfers_collection = self.db.file_transfers
        self.file_chunks_collection = self.db.file_chunks
        self.upload_dir = upload_dir
        self.chunk_size = 64 * 1024  # 64KB chunks
        
        # Control managers
        self.flow_control = FlowControlManager()
        self.congestion_control = CongestionControlManager()
        
        # Active transfers
        self.active_transfers: Dict[str, FileTransferInfo] = {}
        self.transfer_locks: Dict[str, asyncio.Lock] = {}
        
        # Ensure upload directory exists
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def generate_transfer_id(self, sender: str, receiver: str, filename: str) -> str:
        """Generate unique transfer ID"""
        timestamp = str(int(time.time()))
        data = f"{sender}_{receiver}_{filename}_{timestamp}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def calculate_file_checksum(self, file_path: str) -> str:
        """Calculate MD5 checksum of file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    async def initiate_file_transfer(self, sender: str, receiver: str, file_path: str, 
                                   group_name: str = None, priority: int = 0) -> str:
        """Initiate a file transfer"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        transfer_id = self.generate_transfer_id(sender, receiver, filename)
        
        # Calculate file checksum
        checksum = self.calculate_file_checksum(file_path)
        
        # Create transfer info
        transfer_info = FileTransferInfo(
            transfer_id=transfer_id,
            sender=sender,
            receiver=receiver,
            group_name=group_name,
            filename=filename,
            file_size=file_size,
            chunks_total=int((file_size + self.chunk_size - 1) / self.chunk_size),
            file_path=file_path,
            checksum=checksum,
            priority=priority
        )
        
        # Check flow control
        if not self.flow_control.can_start_transfer(sender):
            transfer_info.status = FileTransferStatus.WAITING
            await self.save_transfer_info(transfer_info)
            return transfer_id
        
        # Check congestion control
        if not self.congestion_control.can_start_system_transfer():
            transfer_info.status = FileTransferStatus.WAITING
            self.congestion_control.add_to_queue(transfer_id)
            await self.save_transfer_info(transfer_info)
            return transfer_id
        
        # Start transfer
        self.active_transfers[transfer_id] = transfer_info
        self.transfer_locks[transfer_id] = asyncio.Lock()
        self.flow_control.add_transfer(sender, transfer_id)
        
        # Save to database
        await self.save_transfer_info(transfer_info)
        
        # Start transfer process
        asyncio.create_task(self.process_file_transfer(transfer_id))
        
        return transfer_id
    
    async def process_file_transfer(self, transfer_id: str):
        """Process file transfer with flow and congestion control"""
        if transfer_id not in self.active_transfers:
            return
        
        transfer_info = self.active_transfers[transfer_id]
        
        try:
            transfer_info.status = FileTransferStatus.TRANSFERRING
            await self.save_transfer_info(transfer_info)
            
            # Split file into chunks
            chunks = await self.split_file_into_chunks(transfer_info.file_path)
            
            # Transfer chunks with flow control
            for chunk in chunks:
                # Check bandwidth throttling
                delay = self.flow_control.get_transfer_delay(transfer_info.sender)
                if delay > 0:
                    await asyncio.sleep(delay)
                
                # Save chunk to database
                await self.save_file_chunk(transfer_id, chunk)
                
                # Update progress
                transfer_info.chunks_sent += 1
                self.flow_control.update_bandwidth_usage(transfer_info.sender, chunk.size)
                
                # Update transfer info
                await self.save_transfer_info(transfer_info)
            
            # Mark as completed
            transfer_info.status = FileTransferStatus.COMPLETED
            transfer_info.completed_at = datetime.now()
            await self.save_transfer_info(transfer_info)
            
        except Exception as e:
            transfer_info.status = FileTransferStatus.FAILED
            await self.save_transfer_info(transfer_info)
            print(f"File transfer failed: {e}")
        
        finally:
            # Clean up
            self.flow_control.remove_transfer(transfer_info.sender, transfer_id)
            if transfer_id in self.active_transfers:
                del self.active_transfers[transfer_id]
            if transfer_id in self.transfer_locks:
                del self.transfer_locks[transfer_id]
            
            # Check if any waiting transfers can be started
            await self.process_waiting_transfers()
    
    async def split_file_into_chunks(self, file_path: str) -> List[FileChunk]:
        """Split file into chunks"""
        chunks = []
        chunk_id = 0
        
        with open(file_path, 'rb') as f:
            while True:
                chunk_data = f.read(self.chunk_size)
                if not chunk_data:
                    break
                
                checksum = hashlib.md5(chunk_data).hexdigest()
                chunk = FileChunk(
                    chunk_id=chunk_id,
                    data=chunk_data,
                    checksum=checksum,
                    size=len(chunk_data)
                )
                chunks.append(chunk)
                chunk_id += 1
        
        return chunks
    
    async def save_file_chunk(self, transfer_id: str, chunk: FileChunk):
        """Save file chunk to database"""
        chunk_doc = {
            "transfer_id": transfer_id,
            "chunk_id": chunk.chunk_id,
            "data": chunk.data,
            "checksum": chunk.checksum,
            "size": chunk.size,
            "created_at": datetime.now()
        }
        await self.file_chunks_collection.insert_one(chunk_doc)
    
    async def save_transfer_info(self, transfer_info: FileTransferInfo):
        """Save transfer info to database"""
        transfer_doc = {
            "transfer_id": transfer_info.transfer_id,
            "sender": transfer_info.sender,
            "receiver": transfer_info.receiver,
            "group_name": transfer_info.group_name,
            "filename": transfer_info.filename,
            "file_size": transfer_info.file_size,
            "chunks_total": transfer_info.chunks_total,
            "chunks_sent": transfer_info.chunks_sent,
            "chunks_received": transfer_info.chunks_received,
            "status": transfer_info.status.value,
            "created_at": transfer_info.created_at,
            "completed_at": transfer_info.completed_at,
            "file_path": transfer_info.file_path,
            "checksum": transfer_info.checksum,
            "priority": transfer_info.priority
        }
        
        await self.file_transfers_collection.update_one(
            {"transfer_id": transfer_info.transfer_id},
            {"$set": transfer_doc},
            upsert=True
        )
    
    async def get_transfer_info(self, transfer_id: str) -> Optional[FileTransferInfo]:
        """Get transfer info from database"""
        doc = await self.file_transfers_collection.find_one({"transfer_id": transfer_id})
        if not doc:
            return None
        
        return FileTransferInfo(
            transfer_id=doc["transfer_id"],
            sender=doc["sender"],
            receiver=doc.get("receiver"),
            group_name=doc.get("group_name"),
            filename=doc["filename"],
            file_size=doc["file_size"],
            chunks_total=doc["chunks_total"],
            chunks_sent=doc["chunks_sent"],
            chunks_received=doc["chunks_received"],
            status=FileTransferStatus(doc["status"]),
            created_at=doc["created_at"],
            completed_at=doc.get("completed_at"),
            file_path=doc["file_path"],
            checksum=doc["checksum"],
            priority=doc["priority"]
        )
    
    async def get_file_chunks(self, transfer_id: str) -> List[FileChunk]:
        """Get all chunks for a transfer"""
        cursor = self.file_chunks_collection.find({"transfer_id": transfer_id}).sort("chunk_id", 1)
        chunks = []
        
        async for doc in cursor:
            chunk = FileChunk(
                chunk_id=doc["chunk_id"],
                data=doc["data"],
                checksum=doc["checksum"],
                size=doc["size"]
            )
            chunks.append(chunk)
        
        return chunks
    
    async def reconstruct_file(self, transfer_id: str, output_path: str) -> bool:
        """Reconstruct file from chunks"""
        chunks = await self.get_file_chunks(transfer_id)
        if not chunks:
            return False
        
        # Sort chunks by chunk_id
        chunks.sort(key=lambda x: x.chunk_id)
        
        # Write chunks to file
        with open(output_path, 'wb') as f:
            for chunk in chunks:
                f.write(chunk.data)
        
        # Verify checksum
        transfer_info = await self.get_transfer_info(transfer_id)
        if transfer_info:
            actual_checksum = self.calculate_file_checksum(output_path)
            return actual_checksum == transfer_info.checksum
        
        return True
    
    async def process_waiting_transfers(self):
        """Process transfers in waiting queue"""
        # Check congestion control queue
        next_transfer_id = self.congestion_control.get_next_transfer()
        if next_transfer_id:
            transfer_info = await self.get_transfer_info(next_transfer_id)
            if transfer_info and transfer_info.status == FileTransferStatus.WAITING:
                if self.flow_control.can_start_transfer(transfer_info.sender):
                    self.active_transfers[next_transfer_id] = transfer_info
                    self.transfer_locks[next_transfer_id] = asyncio.Lock()
                    self.flow_control.add_transfer(transfer_info.sender, next_transfer_id)
                    asyncio.create_task(self.process_file_transfer(next_transfer_id))
    
    async def get_user_transfers(self, username: str) -> List[Dict]:
        """Get all transfers for a user"""
        cursor = self.file_transfers_collection.find({
            "$or": [
                {"sender": username},
                {"receiver": username}
            ]
        }).sort("created_at", -1)
        
        transfers = []
        async for doc in cursor:
            doc['_id'] = str(doc['_id'])
            transfers.append(doc)
        
        return transfers
    
    async def get_transfer_progress(self, transfer_id: str) -> Dict:
        """Get transfer progress"""
        transfer_info = await self.get_transfer_info(transfer_id)
        if not transfer_info:
            return {}
        
        progress = 0
        if transfer_info.chunks_total > 0:
            progress = (transfer_info.chunks_sent / transfer_info.chunks_total) * 100
        
        return {
            "transfer_id": transfer_id,
            "filename": transfer_info.filename,
            "status": transfer_info.status.value,
            "progress": progress,
            "chunks_sent": transfer_info.chunks_sent,
            "chunks_total": transfer_info.chunks_total,
            "file_size": transfer_info.file_size,
            "created_at": transfer_info.created_at.isoformat(),
            "queue_position": self.get_queue_position(transfer_id) if transfer_info.status == FileTransferStatus.WAITING else None
        }
    
    def get_queue_position(self, transfer_id: str) -> int:
        """Get position in waiting queue"""
        try:
            return self.congestion_control.transfer_queue.index(transfer_id) + 1
        except ValueError:
            return 0
    
    async def cancel_transfer(self, transfer_id: str) -> bool:
        """Cancel a file transfer"""
        if transfer_id in self.active_transfers:
            transfer_info = self.active_transfers[transfer_id]
            transfer_info.status = FileTransferStatus.FAILED
            await self.save_transfer_info(transfer_info)
            
            # Clean up
            self.flow_control.remove_transfer(transfer_info.sender, transfer_id)
            del self.active_transfers[transfer_id]
            if transfer_id in self.transfer_locks:
                del self.transfer_locks[transfer_id]
            
            return True
        
        # Remove from queue if waiting
        self.congestion_control.remove_from_queue(transfer_id)
        return False
    
    async def get_system_status(self) -> Dict:
        """Get system transfer status"""
        return {
            "active_transfers": len(self.active_transfers),
            "waiting_transfers": len(self.congestion_control.transfer_queue),
            "system_bandwidth_usage": self.congestion_control.current_system_load,
            "max_system_bandwidth": self.congestion_control.max_system_bandwidth,
            "user_bandwidth_usage": dict(self.flow_control.bandwidth_usage)
        }