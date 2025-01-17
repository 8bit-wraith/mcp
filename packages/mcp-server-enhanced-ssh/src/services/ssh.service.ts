import { Server, createServer } from 'net';
import * as pty from 'node-pty';
import { ATCClient } from './atc.client';
import { TmuxService } from './tmux.service';
import { Logger } from '../utils/logger';

export class SSHService {
    private server!: Server;
    private atc: ATCClient;
    private tmux: TmuxService;
    private sessions: Map<string, {shell: pty.IPty; isTmux: boolean}> = new Map();
    
    constructor(private readonly port: number = 2222) {
        this.atc = new ATCClient('ws://localhost:8000/ws');
        this.tmux = new TmuxService();
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
            // Parse the initial command from the socket data
            const initialData = socket.read();
            const command = initialData ? initialData.toString().trim() : '';
            const isTmux = command.startsWith('tmux');
            let shell: pty.IPty;
            
            if (isTmux) {
                // Extract tmux command parts
                const parts = command.split(' ');
                const tmuxAction = parts[1] || 'new-session';
                const tmuxArgs = parts.slice(2);
                
                if (tmuxAction === 'attach' || tmuxAction === 'attach-session') {
                    // For attach commands, just attach to the specified session
                    shell = pty.spawn('tmux', [tmuxAction, ...tmuxArgs], {
                        name: 'xterm-color',
                        cols: 80,
                        rows: 24,
                        cwd: process.env.HOME,
                        env: process.env
                    });
                } else {
                    // For other commands (like new-session), create a new session
                    await this.tmux.createSession(sessionId);
                    shell = pty.spawn('tmux', ['attach-session', '-t', sessionId], {
                        name: 'xterm-color',
                        cols: 80,
                        rows: 24,
                        cwd: process.env.HOME,
                        env: process.env
                    });
                }
            } else {
                // Non-tmux session, just spawn bash
                shell = pty.spawn('bash', [], {
                    name: 'xterm-color',
                    cols: 80,
                    rows: 24,
                    cwd: process.env.HOME,
                    env: process.env
                });
            }
            
            this.sessions.set(sessionId, { shell, isTmux });
            
            // If we had initial data that wasn't a tmux command, write it to the shell
            if (!isTmux && initialData) {
                shell.write(initialData);
            }
            
            shell.onData((data) => {
                this.atc.send({ type: 'terminal', sessionId, data });
                socket.write(data);
            });
            
            socket.on('data', (data: Buffer) => {
                shell.write(data.toString());
            });
            
            socket.on('close', async () => {
                const session = this.sessions.get(sessionId);
                if (!session) return;
                
                if (!session.isTmux) {
                    session.shell.kill();
                    this.sessions.delete(sessionId);
                    Logger.info(`Session ${sessionId} closed`);
                } else {
                    Logger.info(`Socket closed but keeping tmux session ${sessionId} alive`);
                    // Detach from tmux session but keep it running
                    await this.tmux.executeCommand('detach-client', ['-s', sessionId]);
                }
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
            for (const [sessionId, session] of this.sessions) {
                if (session.isTmux) {
                    await this.tmux.killSession(sessionId);
                }
                session.shell.kill();
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