import asyncio
import json
import socket
import threading
import base64
from datetime import datetime
from typing import Dict, Set

import uvicorn
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

# MongoDB Models
class Message(BaseModel):
    sender: str
    receiver: str = None
    content: str
    timestamp: datetime = datetime.now()
    is_group: bool = False

class FileDocument(BaseModel):
    filename: str
    sender: str
    receiver: str = None  # None for group files
    file_content: str  # Base64 encoded
    file_size: int
    timestamp: datetime = datetime.now()
    is_group: bool = False

class User(BaseModel):
    username: str
    is_online: bool = False

class Group(BaseModel):
    name: str
    creator: str
    members: Set[str]
    created_at: datetime = datetime.now()

# FastAPI App
app = FastAPI()
main_event_loop = None

# MongoDB connection
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.chatapp
messages_collection = db.messages
users_collection = db.users
groups_collection = db.groups
files_collection = db.files  # New collection for files

# TCP Server
class TCPChatServer:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.clients: Dict[str, socket.socket] = {}
        self.groups: Dict[str, Dict] = {}
        self.running = False

    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        self.running = True
        print(f"TCP Server listening on {self.host}:{self.port}")

        self.run_async_task(self.load_groups_from_db())

        while self.running:
            try:
                client_socket, addr = self.server.accept()
                threading.Thread(target=self.handle_client, args=(client_socket, addr), daemon=True).start()
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {e}")

    def handle_client(self, client_socket, addr):
        username = None
        try:
            while True:
                data = self.receive_message(client_socket)
                if not data:
                    break
                msg = json.loads(data)
                msg_type = msg.get('type')

                if msg_type == 'join':
                    username = msg['username']
                    self.clients[username] = client_socket
                    self.run_async_task(self.update_user_status(username, True))
                    join_resp = {"type": "join_response", "success": True, "message": f"Welcome {username}!"}
                    self.send_message(client_socket, json.dumps(join_resp))
                    self.broadcast_user_list()
                    self.send_user_groups(username)
                    
                elif msg_type == 'private_message':
                    message_data = {
                        "sender": msg["sender"],
                        "receiver": msg["recipient"],
                        "content": msg["content"],
                        "is_group": False
                    }
                    self.run_async_task(self.save_message(message_data))
                    self.send_to_user(msg)

                elif msg_type == 'group_message':
                    group_name = msg.get("group")
                    if group_name in self.groups:
                        if username in self.groups[group_name]['members']:
                            message_data = {
                                "sender": msg["sender"],
                                "receiver": group_name,
                                "content": msg["content"],
                                "is_group": True
                            }
                            self.run_async_task(self.save_message(message_data))
                            self.broadcast_to_group(msg, sender=msg['sender'])
                        else:
                            error_resp = {"type": "error", "message": "You are not a member of this group"}
                            self.send_message(client_socket, json.dumps(error_resp))

                    # SERVER SIDE FIXES - Replace your file transfer handlers in the server

                elif msg_type == 'file_transfer':
                    recipient = msg.get('recipient')
                    filename = msg.get('filename')
                    file_content = msg.get('file_content')
                    file_size = msg.get('file_size')
                    
                    if not all([recipient, filename, file_content, file_size]):
                        error_resp = {"type": "error", "message": "Missing file transfer data"}
                        self.send_message(client_socket, json.dumps(error_resp))
                        continue
                    
                    # Save file to MongoDB
                    file_data = {
                        "filename": filename,
                        "sender": username,
                        "receiver": recipient,
                        "file_content": file_content,
                        "file_size": file_size,
                        "is_group": False
                    }
                    self.run_async_task(self.save_file_to_db(file_data))
                    
                    # Send file to recipient
                    if recipient in self.clients:
                        file_msg = {
                            "type": "file_received",
                            "sender": username,
                            "filename": filename,
                            "file_content": file_content,
                            "file_size": file_size,
                            "timestamp": datetime.now().strftime('%H:%M'),
                            "is_group": False
                        }
                        self.send_message(self.clients[recipient], json.dumps(file_msg))
                    
                    # Send confirmation to sender
                    confirm_msg = {
                        "type": "file_sent_confirmation",
                        "success": True,
                        "message": f"File '{filename}' sent to {recipient}"
                    }
                    self.send_message(client_socket, json.dumps(confirm_msg))

                elif msg_type == 'group_file_transfer':
                    group_name = msg.get('group')
                    filename = msg.get('filename')
                    file_content = msg.get('file_content')
                    file_size = msg.get('file_size')
                    
                    if not all([group_name, filename, file_content, file_size]):
                        error_resp = {"type": "error", "message": "Missing group file transfer data"}
                        self.send_message(client_socket, json.dumps(error_resp))
                        continue
                    
                    if group_name in self.groups and username in self.groups[group_name]['members']:
                        # Save file to MongoDB
                        file_data = {
                            "filename": filename,
                            "sender": username,
                            "receiver": group_name,
                            "file_content": file_content,
                            "file_size": file_size,
                            "is_group": True
                        }
                        self.run_async_task(self.save_file_to_db(file_data))
                        
                        # Send file to all group members except sender
                        for member in self.groups[group_name]['members']:
                            if member != username and member in self.clients:
                                file_msg = {
                                    "type": "group_file_received",
                                    "sender": username,
                                    "group_name": group_name,
                                    "filename": filename,
                                    "file_content": file_content,
                                    "file_size": file_size,
                                    "timestamp": datetime.now().strftime('%H:%M'),
                                    "is_group": True
                                }
                                self.send_message(self.clients[member], json.dumps(file_msg))
                        
                        # Send confirmation to sender
                        confirm_msg = {
                            "type": "file_sent_confirmation",
                            "success": True,
                            "message": f"File '{filename}' sent to group {group_name}"
                        }
                        self.send_message(client_socket, json.dumps(confirm_msg))
                    else:
                        error_resp = {"type": "error", "message": "You are not a member of this group"}
                        self.send_message(client_socket, json.dumps(error_resp))

                elif msg_type == 'add_member':
                    group_name = msg.get('group_name')
                    new_member = msg.get('member')
                    
                    if group_name in self.groups and self.groups[group_name]['creator'] == username:
                        if new_member not in self.groups[group_name]['members']:
                            self.groups[group_name]['members'].add(new_member)
                            self.run_async_task(self.update_group_in_db(group_name, self.groups[group_name]))
                            
                            if new_member in self.clients:
                                notification = {
                                    "type": "group_notification",
                                    "message": f"You have been added to group '{group_name}' by {username}",
                                    "group": group_name
                                }
                                self.send_message(self.clients[new_member], json.dumps(notification))
                                self.send_user_groups(new_member)
                            
                            resp = {"type": "add_member_response", "success": True, "message": f"Added {new_member} to group"}
                        else:
                            resp = {"type": "add_member_response", "success": False, "message": "User already in group"}
                    else:
                        resp = {"type": "add_member_response", "success": False, "message": "Only group creator can add members"}
                    self.send_message(client_socket, json.dumps(resp))

                elif msg_type == 'remove_member':
                    group_name = msg.get('group_name')
                    member_to_remove = msg.get('member')
                    
                    if group_name in self.groups and self.groups[group_name]['creator'] == username:
                        if member_to_remove in self.groups[group_name]['members'] and member_to_remove != username:
                            self.groups[group_name]['members'].remove(member_to_remove)
                            self.run_async_task(self.update_group_in_db(group_name, self.groups[group_name]))
                            
                            if member_to_remove in self.clients:
                                notification = {
                                    "type": "group_notification",
                                    "message": f"You have been removed from group '{group_name}' by {username}",
                                    "group": group_name
                                }
                                self.send_message(self.clients[member_to_remove], json.dumps(notification))
                                self.send_user_groups(member_to_remove)
                            
                            resp = {"type": "remove_member_response", "success": True, "message": f"Removed {member_to_remove} from group"}
                        else:
                            resp = {"type": "remove_member_response", "success": False, "message": "Cannot remove creator or non-member"}
                    else:
                        resp = {"type": "remove_member_response", "success": False, "message": "Only group creator can remove members"}
                    self.send_message(client_socket, json.dumps(resp))

        except Exception as e:
            print(f"Error handling client {addr}: {e}")
        finally:
            if username:
                self.clients.pop(username, None)
                self.run_async_task(self.update_user_status(username, False))
                self.broadcast_user_list()
            client_socket.close()

    def receive_message(self, client_socket):
        try:
            length_data = client_socket.recv(4)
            if not length_data:
                return None
            msg_length = int.from_bytes(length_data, byteorder='big')
            data = b''
            while len(data) < msg_length:
                chunk = client_socket.recv(min(msg_length - len(data), 4096))
                if not chunk:
                    return None
                data += chunk
            return data.decode('utf-8')
        except:
            return None

    def send_message(self, client_socket, message):
        try:
            msg_bytes = message.encode('utf-8')
            length = len(msg_bytes).to_bytes(4, byteorder='big')
            client_socket.sendall(length + msg_bytes)
        except:
            pass

    def send_to_user(self, msg):
        receiver = msg.get('receiver') or msg.get('recipient')
        if receiver in self.clients:
            self.send_message(self.clients[receiver], json.dumps(msg))

    def broadcast_to_group(self, msg, sender):
        group_name = msg.get('group')
        if group_name in self.groups:
            for member in self.groups[group_name]['members']:
                if member in self.clients:
                    self.send_message(self.clients[member], json.dumps(msg))

    def send_user_list(self, client_socket):
        users = [{"username": u, "is_online": True} for u in self.clients.keys()]
        user_list_msg = {"type": "user_list", "users": [u['username'] for u in users]}
        self.send_message(client_socket, json.dumps(user_list_msg))

    def broadcast_user_list(self):
        users = [{"username": u, "is_online": True} for u in self.clients.keys()]
        msg = {"type": "user_list", "users": [u['username'] for u in users]}
        for sock in self.clients.values():
            self.send_message(sock, json.dumps(msg))

    def send_user_groups(self, username):
        user_groups = []
        for group_name, group_data in self.groups.items():
            if username in group_data['members']:
                user_groups.append({
                    'name': group_name,
                    'creator': group_data['creator'],
                    'members': list(group_data['members']),
                    'is_creator': group_data['creator'] == username
                })
        
        msg = {"type": "group_list", "groups": user_groups}
        if username in self.clients:
            self.send_message(self.clients[username], json.dumps(msg))

    def notify_group_members(self, group_name, message):
        if group_name in self.groups:
            for member in self.groups[group_name]['members']:
                if member in self.clients:
                    notification = {
                        "type": "group_notification",
                        "message": message,
                        "group": group_name
                    }
                    self.send_message(self.clients[member], json.dumps(notification))
                    self.send_user_groups(member)

    async def save_message(self, msg_data):
        try:
            message = {
                "sender": msg_data["sender"],
                "receiver": msg_data["receiver"],
                "content": msg_data["content"],
                "timestamp": datetime.now(),
                "is_group": msg_data.get("is_group", False)
            }
            result = await messages_collection.insert_one(message)
            print(f"[MongoDB] Message saved with ID: {result.inserted_id}")
        except Exception as e:
            print(f"[MongoDB] Failed to save message: {e}")

    async def save_file_to_db(self, file_data):
        try:
            file_doc = {
                "filename": file_data["filename"],
                "sender": file_data["sender"],
                "receiver": file_data["receiver"],
                "file_content": file_data["file_content"],
                "file_size": file_data["file_size"],
                "timestamp": datetime.now(),
                "is_group": file_data.get("is_group", False)
            }
            result = await files_collection.insert_one(file_doc)
            print(f"[MongoDB] File saved with ID: {result.inserted_id}")
        except Exception as e:
            print(f"[MongoDB] Failed to save file: {e}")

    async def update_user_status(self, username, is_online):
        try:
            await users_collection.update_one(
                {"username": username},
                {"$set": {"username": username, "is_online": is_online}},
                upsert=True
            )
            print(f"[MongoDB] User status updated: {username} - {is_online}")
        except Exception as e:
            print(f"[MongoDB] Failed to update user status: {e}")

    async def save_group_to_db(self, group_data):
        try:
            group_doc = {
                "name": group_data["name"],
                "creator": group_data["creator"],
                "members": list(group_data["members"]),
                "created_at": group_data["created_at"]
            }
            result = await groups_collection.insert_one(group_doc)
            print(f"[MongoDB] Group saved with ID: {result.inserted_id}")
        except Exception as e:
            print(f"[MongoDB] Failed to save group: {e}")

    async def update_group_in_db(self, group_name, group_data):
        try:
            await groups_collection.update_one(
                {"name": group_name},
                {"$set": {"members": list(group_data["members"])}},
                upsert=True
            )
            print(f"[MongoDB] Group updated: {group_name}")
        except Exception as e:
            print(f"[MongoDB] Failed to update group: {e}")

    async def load_groups_from_db(self):
        try:
            cursor = groups_collection.find({})
            async for doc in cursor:
                group_data = {
                    'name': doc['name'],
                    'creator': doc['creator'],
                    'members': set(doc['members']),
                    'created_at': doc['created_at']
                }
                self.groups[doc['name']] = group_data
            print(f"[MongoDB] Loaded {len(self.groups)} groups from database")
        except Exception as e:
            print(f"[MongoDB] Failed to load groups: {e}")

    def run_async_task(self, coro):
        global main_event_loop
        if main_event_loop:
            future = asyncio.run_coroutine_threadsafe(coro, main_event_loop)
            try:
                return future.result()
            except Exception as e:
                print(f"Async task error: {e}")

# Global server instance
tcp_server = TCPChatServer()

# FastAPI routes
@app.get("/messages/{username}")
async def get_messages(username: str):
    cursor = messages_collection.find({
        "$or": [
            {"sender": username},
            {"receiver": username},
            {"is_group": True}
        ]
    }).sort("timestamp", -1).limit(100)
    messages = []
    async for doc in cursor:
        doc['_id'] = str(doc['_id'])
        messages.append(doc)
    return messages

@app.get("/files/{username}")
async def get_user_files(username: str):
    cursor = files_collection.find({
        "$or": [
            {"sender": username},
            {"receiver": username},
            {"is_group": True}
        ]
    }).sort("timestamp", -1).limit(50)
    files = []
    async for doc in cursor:
        doc['_id'] = str(doc['_id'])
        # Remove file_content from response for performance
        doc.pop('file_content', None)
        files.append(doc)
    return files

@app.get("/file/{file_id}")
async def get_file_content(file_id: str):
    from bson import ObjectId
    try:
        file_doc = await files_collection.find_one({"_id": ObjectId(file_id)})
        if file_doc:
            return {
                "filename": file_doc["filename"],
                "file_content": file_doc["file_content"],
                "file_size": file_doc["file_size"]
            }
        return {"error": "File not found"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/users")
async def get_users():
    users_cursor = users_collection.find({})
    users = []
    async for doc in users_cursor:
        doc['_id'] = str(doc['_id'])
        users.append(doc)
    return users

@app.get("/groups/{username}")
async def get_user_groups(username: str):
    cursor = groups_collection.find({"members": username})
    groups = []
    async for doc in cursor:
        doc['_id'] = str(doc['_id'])
        groups.append(doc)
    return groups

@app.on_event("startup")
async def startup_event():
    global main_event_loop
    main_event_loop = asyncio.get_running_loop()
    threading.Thread(target=tcp_server.start, daemon=True).start()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)