# import asyncio
# import json
# import socket
# import threading
# from datetime import datetime
# from typing import Dict, Set

# import uvicorn
# from fastapi import FastAPI
# from motor.motor_asyncio import AsyncIOMotorClient
# from pydantic import BaseModel

# # MongoDB Models
# class Message(BaseModel):
#     sender: str
#     receiver: str = None  # None for group messages
#     content: str
#     timestamp: datetime = datetime.now()
#     is_group: bool = False

# class User(BaseModel):
#     username: str
#     is_online: bool = False

# # FastAPI App
# app = FastAPI()
# main_event_loop = None  # global to store the main event loop

# # MongoDB connection
# client = AsyncIOMotorClient("mongodb://localhost:27017")
# db = client.chatapp
# messages_collection = db.messages
# users_collection = db.users

# # TCP Server
# class TCPChatServer:
#     def __init__(self, host='localhost', port=12345):
#         self.host = host
#         self.port = port
#         self.clients: Dict[str, socket.socket] = {}
#         self.groups: Dict[str, Set[str]] = {'general': set()}
#         self.running = False

#     def start(self):
#         self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         self.server.bind((self.host, self.port))
#         self.server.listen(5)
#         self.running = True
#         print(f"TCP Server listening on {self.host}:{self.port}")

#         while self.running:
#             try:
#                 client_socket, addr = self.server.accept()
#                 threading.Thread(target=self.handle_client, args=(client_socket, addr), daemon=True).start()
#             except Exception as e:
#                 if self.running:
#                     print(f"Error accepting connection: {e}")

#     def handle_client(self, client_socket, addr):
#         username = None
#         try:
#             while True:
#                 data = self.receive_message(client_socket)
#                 if not data:
#                     break
#                 msg = json.loads(data)
#                 msg_type = msg.get('type')

#                 if msg_type == 'join':
#                     username = msg['username']
#                     self.clients[username] = client_socket
#                     self.groups['general'].add(username)
#                     self.run_async_task(self.update_user_status(username, True))
#                     join_resp = {"type": "join_response", "success": True, "message": f"Welcome {username}!"}
#                     self.send_message(client_socket, json.dumps(join_resp))
#                     self.broadcast_user_list()
#                     self.broadcast_group_list()
                    
#                 elif msg_type == 'private_message':
#                     # Save to DB - Fixed the field mapping
#                     message_data = {
#                         "sender": msg["sender"],
#                         "receiver": msg["recipient"],  # Use "recipient" from client message
#                         "content": msg["content"],
#                         "is_group": False
#                     }
#                     self.run_async_task(self.save_message(message_data))
#                     self.send_to_user(msg)

#                 elif msg_type == 'group_message':
#                     # Save to DB - Fixed the field mapping
#                     message_data = {
#                         "sender": msg["sender"],
#                         "receiver": msg["group"],  # Use "group" from client message
#                         "content": msg["content"],
#                         "is_group": True
#                     }
#                     self.run_async_task(self.save_message(message_data))
#                     self.broadcast_to_group(msg, sender=msg['sender'])

#                 elif msg_type == 'get_users':
#                     self.send_user_list(client_socket)

#                 elif msg_type == 'get_groups':
#                     self.send_group_list(client_socket)

#                 elif msg_type == 'create_group':
#                     group_name = msg.get('group_name')
#                     if group_name and group_name not in self.groups:
#                         self.groups[group_name] = set()
#                         self.groups[group_name].add(username)
#                         self.broadcast_group_list()
#                         resp = {"type": "create_group_response", "success": True, "message": f"Group '{group_name}' created."}
#                     else:
#                         resp = {"type": "create_group_response", "success": False, "message": "Group already exists."}
#                     self.send_message(client_socket, json.dumps(resp))

#                 elif msg_type == 'join_group':
#                     group_name = msg.get('group_name')
#                     if group_name in self.groups:
#                         self.groups[group_name].add(username)
#                         self.broadcast_group_list()
#                         resp = {"type": "join_group_response", "success": True, "message": f"Joined group '{group_name}'"}
#                     else:
#                         resp = {"type": "join_group_response", "success": False, "message": "Group not found"}
#                     self.send_message(client_socket, json.dumps(resp))

#         except Exception as e:
#             print(f"Error handling client {addr}: {e}")
#         finally:
#             if username:
#                 self.clients.pop(username, None)
#                 for group in self.groups.values():
#                     group.discard(username)
#                 self.run_async_task(self.update_user_status(username, False))
#                 self.broadcast_user_list()
#             client_socket.close()

#     def receive_message(self, client_socket):
#         try:
#             length_data = client_socket.recv(4)
#             if not length_data:
#                 return None
#             msg_length = int.from_bytes(length_data, byteorder='big')
#             data = b''
#             while len(data) < msg_length:
#                 chunk = client_socket.recv(min(msg_length - len(data), 4096))
#                 if not chunk:
#                     return None
#                 data += chunk
#             return data.decode('utf-8')
#         except:
#             return None

#     def send_message(self, client_socket, message):
#         try:
#             msg_bytes = message.encode('utf-8')
#             length = len(msg_bytes).to_bytes(4, byteorder='big')
#             client_socket.sendall(length + msg_bytes)
#         except:
#             pass

#     def send_to_user(self, msg):
#         receiver = msg.get('receiver') or msg.get('recipient')
#         if receiver in self.clients:
#             self.send_message(self.clients[receiver], json.dumps(msg))

#     def broadcast_to_group(self, msg, sender):
#         group_name = msg.get('group')
#         if group_name in self.groups:
#             for member in self.groups[group_name]:
#                 if member != sender and member in self.clients:
#                     self.send_message(self.clients[member], json.dumps(msg))

#     def send_user_list(self, client_socket):
#         users = [{"username": u, "is_online": True} for u in self.clients.keys()]
#         user_list_msg = {"type": "user_list", "users": [u['username'] for u in users]}
#         self.send_message(client_socket, json.dumps(user_list_msg))

#     def broadcast_user_list(self):
#         users = [{"username": u, "is_online": True} for u in self.clients.keys()]
#         msg = {"type": "user_list", "users": [u['username'] for u in users]}
#         for sock in self.clients.values():
#             self.send_message(sock, json.dumps(msg))

#     def send_group_list(self, client_socket):
#         msg = {"type": "group_list", "groups": list(self.groups.keys())}
#         self.send_message(client_socket, json.dumps(msg))

#     def broadcast_group_list(self):
#         msg = {"type": "group_list", "groups": list(self.groups.keys())}
#         for sock in self.clients.values():
#             self.send_message(sock, json.dumps(msg))

#     async def save_message(self, msg_data):
#         try:
#             message = {
#                 "sender": msg_data["sender"],
#                 "receiver": msg_data["receiver"],
#                 "content": msg_data["content"],
#                 "timestamp": datetime.now(),
#                 "is_group": msg_data.get("is_group", False)
#             }
#             result = await messages_collection.insert_one(message)
#             print(f"[MongoDB] Message saved with ID: {result.inserted_id}")
#         except Exception as e:
#             print(f"[MongoDB] Failed to save message: {e}")

#     async def update_user_status(self, username, is_online):
#         try:
#             await users_collection.update_one(
#                 {"username": username},
#                 {"$set": {"username": username, "is_online": is_online}},
#                 upsert=True
#             )
#             print(f"[MongoDB] User status updated: {username} - {is_online}")
#         except Exception as e:
#             print(f"[MongoDB] Failed to update user status: {e}")

#     def run_async_task(self, coro):
#         global main_event_loop
#         if main_event_loop:
#             future = asyncio.run_coroutine_threadsafe(coro, main_event_loop)
#             try:
#                 return future.result()
#             except Exception as e:
#                 print(f"Async task error: {e}")

# # Global server instance
# tcp_server = TCPChatServer()

# # FastAPI routes
# @app.get("/messages/{username}")
# async def get_messages(username: str):
#     cursor = messages_collection.find({
#         "$or": [
#             {"sender": username},
#             {"receiver": username},
#             {"is_group": True}
#         ]
#     }).sort("timestamp", -1).limit(50)
#     messages = []
#     async for doc in cursor:
#         doc['_id'] = str(doc['_id'])
#         messages.append(doc)
#     return messages

# @app.get("/users")
# async def get_users():
#     users_cursor = users_collection.find({})
#     users = []
#     async for doc in users_cursor:
#         doc['_id'] = str(doc['_id'])
#         users.append(doc)
#     return users

# @app.on_event("startup")
# async def startup_event():
#     global main_event_loop
#     main_event_loop = asyncio.get_running_loop()
#     threading.Thread(target=tcp_server.start, daemon=True).start()

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)






import asyncio
import json
import socket
import threading
from datetime import datetime
from typing import Dict, Set

import uvicorn
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

# MongoDB Models
class Message(BaseModel):
    sender: str
    receiver: str = None  # None for group messages
    content: str
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
main_event_loop = None  # global to store the main event loop

# MongoDB connection
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.chatapp
messages_collection = db.messages
users_collection = db.users
groups_collection = db.groups

# TCP Server
class TCPChatServer:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.clients: Dict[str, socket.socket] = {}
        self.groups: Dict[str, Dict] = {}  # Changed to store group info
        self.running = False

    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        self.running = True
        print(f"TCP Server listening on {self.host}:{self.port}")

        # Load existing groups from database
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
                        # Check if user is member of the group
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

                elif msg_type == 'get_users':
                    self.send_user_list(client_socket)

                elif msg_type == 'get_groups':
                    self.send_user_groups(username)

                elif msg_type == 'create_group':
                    group_name = msg.get('group_name')
                    selected_members = msg.get('members', [])
                    
                    if group_name and group_name not in self.groups:
                        # Create group with creator and selected members
                        members = set([username] + selected_members)
                        group_data = {
                            'name': group_name,
                            'creator': username,
                            'members': members,
                            'created_at': datetime.now()
                        }
                        self.groups[group_name] = group_data
                        
                        # Save to database
                        self.run_async_task(self.save_group_to_db(group_data))
                        
                        # Notify all members about the new group
                        self.notify_group_members(group_name, f"You have been added to group '{group_name}' by {username}")
                        
                        resp = {"type": "create_group_response", "success": True, "message": f"Group '{group_name}' created."}
                    else:
                        resp = {"type": "create_group_response", "success": False, "message": "Group already exists."}
                    self.send_message(client_socket, json.dumps(resp))

                elif msg_type == 'add_member':
                    group_name = msg.get('group_name')
                    new_member = msg.get('member')
                    
                    if group_name in self.groups and self.groups[group_name]['creator'] == username:
                        if new_member not in self.groups[group_name]['members']:
                            self.groups[group_name]['members'].add(new_member)
                            self.run_async_task(self.update_group_in_db(group_name, self.groups[group_name]))
                            
                            # Notify the new member
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
                            
                            # Notify the removed member
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
            # Send to all members of the group (including sender for confirmation)
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
        """Send only the groups that the user is a member of"""
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
        """Notify all members of a group about group changes"""
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