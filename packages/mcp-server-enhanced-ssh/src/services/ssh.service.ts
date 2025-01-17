import { Server, createServer } from 'net';
import * as pty from 'node-pty';
import { ATCClient } from './atc.client';
import { Logger } from '../utils/logger';

export class SSHService {
    private server!: Server;
    private atc: ATCClient;
    private sessions: Map<string, pty.IPty> = new Map();
    
    constructor(private readonly port: number = 2222) {
        this.atc = new ATCClient('ws://localhost:8000/ws');
    }
    
    async start(): Promise<void> {
        try {
            // Start TCP server first
            this.server = createServer();
            
            this.server.on('connection', (socket) => {
                const sessionId = `session_${Date.now()}`;
                this.handleSession(sessionId, socket).catch((error) => {
                    Logger.error(`Session error: ${error}`);
                    socket.destroy();
                });
            });
            
            // Start listening on port
            await new Promise<void>((resolve, reject) => {
                this.server.on('error', reject);
                this.server.listen(this.port, () => {
                    Logger.info(`SSH service listening on port ${this.port}`);
                    resolve();
                });
            });
            
            // Try to connect to ATC server with retries
            try {
                await this.atc.connect(5, 2000);  // 5 retries, 2 seconds between attempts
                Logger.info('Successfully connected to ATC server');
            } catch (error) {
                Logger.warn(`Failed to connect to ATC server: ${error}. Will continue without ATC integration.`);
            }
            
            Logger.info('SSH service started successfully');
        } catch (error) {
            Logger.error(`Failed to start SSH service: ${error}`);
            // Clean up if server was created
            if (this.server) {
                this.server.close();
            }
            throw error;
        }
    }
    
    private async handleSession(sessionId: string, socket: any): Promise<void> {
        try {
            const shell = pty.spawn('bash', [], {
                name: 'xterm-color',
                cols: 80,
                rows: 24,
                cwd: process.env.HOME,
                env: process.env
            });
            
            this.sessions.set(sessionId, shell);
            
            shell.onData((data) => {
                this.atc.send({ type: 'terminal', sessionId, data });
                socket.write(data);
            });
            
            socket.on('data', (data: Buffer) => {
                shell.write(data.toString());
            });
            
            socket.on('close', () => {
                shell.kill();
                this.sessions.delete(sessionId);
                Logger.info(`Session ${sessionId} closed`);
            });
            
            this.atc.on(`data_${sessionId}`, (data: string) => {
                shell.write(data);
            });
            
        } catch (error) {
            Logger.error(`Session error: ${error}`);
            throw error;
        }
    }
    
    async stop(): Promise<void> {
        try {
            // Kill all active sessions
            for (const [sessionId, shell] of this.sessions) {
                shell.kill();
                this.sessions.delete(sessionId);
                Logger.info(`Session ${sessionId} terminated`);
            }
            
            // Disconnect from ATC
            await this.atc.disconnect();
            
            // Close server
            if (this.server) {
                this.server.close();
            }
            
            Logger.info('SSH service stopped');
        } catch (error) {
            Logger.error(`Failed to stop SSH service: ${error}`);
            throw error;
        }
    }
}