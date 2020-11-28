import asyncio
import websockets
import time
import shlex
import logging


class Client:

    def __init__(self, server, websocket, path):

        self.client = websocket
        self.server = server
        self.name = None

    async def send(self, msg):

        await self.client.send(msg)

    async def receive(self):

        msg = await self.client.recv()
        return msg

    async def handler(self):

        try:
            await self.send("Seja bem vindo ao chat! Identifique-se com /nome SeuNome.")
            await self.send("Escreva /help para mostrar todos os comandos.")
            while True:
                msg = await self.receive()
                if msg:
                    print(f"{self.name} < {msg}")
                    await self.process_command(msg)
                else:
                    continue
        except Exception:
            print("Erro:")
            raise
        finally: 
            await self.server.disconnect(self)
    
    async def process_command(self, msg):

        if msg.strip().startswith("/"):
            commands = shlex.split(msg.strip()[1:])
            if len(commands)==0:
                await self.send("Comando inválido!")
                return
            #print(commands)
            command = commands[0].lower()            
            if command == "horas":
                await self.send("Horas: " + time.strftime("%H:%M:%S"))
            elif command == "nome":
                await self.change_nickname(commands)
            elif command == "direct":
                await self.direct(commands)
            elif command == "help":
                await self.send("/nome SeuNome para mudar seu nickname.")
                await self.send("/horas para mostrar as horas.")
                await self.send("/direct Destinatário para enviar uma mensagem privada.")
            else:
                await self.send("Comando inválido!")
        else:
            if self.name:
                await self.server.send_all(self, msg)
            else:
                await self.send("Defina um nickname primeiro. Use /nome SeuNome")

    async def change_nickname(self, commands):

        if len(commands)>1 and self.server.verify_nickname(commands[1]):
            self.name = commands[1]
            await self.send(f"Nickname modificado para {self.name}.")
            await self.server.send_all(self,f"{self.name} entrou no chat.")
        else:
            await self.send("Nickname em uso. Por favor, escolha outro.")

    async def direct(self, command):

        if len(command)<3:
            await self.send("Comando inválido. Use /direct nickname seguido da mensagem.")
            return
        destination = command[1]
        msg = " ".join(command[2:])
        sent = await self.server.send_to_destination(self, msg, destination)
        if not sent:
            await self.send(f"Destino {destination} não encontrado. Mensagem cancelada")


    @property
    def connected(self):
        return self.client.open

class Server:
    def __init__(self):
        
        self.connections = []
        self.name = "SERVER"

    def verify_nickname(self, name):

        for client in self.connections:
            if client.name and client.name == name:
                return False
        return True

    async def connect(self, websocket, path):
       
        client = Client(self, websocket, path)
        if client not in self.connections:
            self.connections.append(client)
            print(f"Novo client conectado. Total: {self.nconnections}")
        await client.handler()
    
    async def disconnect(self, client):
        
        if client in self.connections:
            self.connections.remove(client)
            await self.send_all(self, f'{client.name} desconectou...')
            print(f"{client.name} foi desconectado. {self.nconnections} conexões ativas.")
            await client.client.close()
        
    async def send_all(self, origin, msg):

        print("Enviando para todos")
        for client in self.connections:
            if origin != client and client.connected:
                print(f"[Enviando] {origin.name} >> {client.name}: {msg}")
                await client.send(f"(Todos) {origin.name}: {msg}")
            
    async def send_to_destination(self, origin, msg, destination):

        for client in self.connections:
            if origin != client and client.connected and client.name == destination:
                print(f"[Enviando] {origin.name} >> {client.name}: {msg}")
                await client.send(f"(Privado) {origin.name}: {msg}")
                return True
        return False

        
    @property
    def nconnections(self):
       
        return(len(self.connections))

server = Server() 
loop = asyncio.get_event_loop()
start_server = websockets.serve(server.connect, 'localhost', 8765) 

loop.run_until_complete(start_server)
loop.run_forever()