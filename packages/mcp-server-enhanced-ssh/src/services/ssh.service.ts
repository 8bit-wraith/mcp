import { Server, ServerConfig, Client, Session, SFTPWrapper, AuthContext, Stats, Attributes, Connection } from 'ssh2';
import * as fs from 'fs';
import * as path from 'path';
import * as pty from 'node-pty';
import * as os from 'os';
import { ATCClient } from './atc.client';
import { TmuxService } from './tmux.service';
import { Logger } from '../utils/logger';

/**
 * SFTP file operation mode flags
 * Used to determine the type of file operation being requested
 */
const SFTP_OPEN_MODE = {
    READ: 0x00000001,
    WRITE: 0x00000002,
    APPEND: 0x00000004,
    CREATE: 0x00000008,
    TRUNCATE: 0x00000010,
    EXCL: 0x00000020
} as const;

/**
 * SFTP Status Codes
 * Used for responding to SFTP client requests with appropriate status codes
 * These codes follow the SSH File Transfer Protocol specification
 */
const SFTP_STATUS = {
    OK: 0,
    EOF: 1,
    NO_SUCH_FILE: 2,
    PERMISSION_DENIED: 3,
    FAILURE: 4,
    BAD_MESSAGE: 5,
    NO_CONNECTION: 6,
    CONNECTION_LOST: 7,
    OP_UNSUPPORTED: 8
} as const;

interface ClientInfo {
    // Connection details
    ip: string;
    port: number;
    username?: string;
    connectTime: Date;
    lastActivity: Date;
    
    // Client capabilities
    clientVersion: string;
    supportedAuth: string[];
    
    // System info
    serverHostname: string;
    serverPlatform: string;
    serverArch: string;
    
    // Session stats
    bytesRead: number;
    bytesWritten: number;
    activeChannels: number;
}

interface SessionData {
    shell: pty.IPty;
    isTmux: boolean;
    clientInfo: ClientInfo;
}

/**
 * Enhanced SSH Service with Tmux Integration
 */
export class SSHService {
    /** The underlying SSH server instance */
    private server!: Server;
    /** Client for ATC (Awesome Tool Collection) integration */
    private atc: ATCClient;
    /** Service for managing Tmux sessions */
    private tmux: TmuxService;
    /** Map of active sessions indexed by session ID */
    private sessions: Map<string, SessionData> = new Map();
    /** Generated password for SSH authentication */
    private generatedPassword: string = '';

    constructor(private readonly port: number = 6480, apiPort: number = 6481) {
        this.atc = new ATCClient(`ws://localhost:${apiPort}/ws`);
        this.tmux = new TmuxService();
    }

    /**
     * Generates a secure random password for SSH authentication
     * @returns A random password string
     */
    private generateSecurePassword(): string {
        const length = 24;
        const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?';
        let password = '';
        for (let i = 0; i < length; i++) {
            const randomIndex = Math.floor(Math.random() * charset.length);
            password += charset[randomIndex];
        }
        return password;
    }

    async start(): Promise<void> {
        try {
            // Generate secure password for this server instance
            this.generatedPassword = this.generateSecurePassword();
            Logger.info(`
=== GENERATED SSH PASSWORD ===
${this.generatedPassword}
===========================
Please save this password securely. It will be required for SSH password authentication.
`);

            // Initialize SSH server with host keys
            const hostKeyPath = path.join(process.cwd(), 'config', 'ssh_host_rsa_key');
            
            const config: ServerConfig = {
                hostKeys: [fs.readFileSync(hostKeyPath)],
                debug: (msg: string) => Logger.debug(`SSH Debug: ${msg}`)
            };

            this.server = new Server(config, (client: Connection) => {
                const now = new Date();
                const clientInfo: ClientInfo = {
                    ip: (client as any)._sock?.remoteAddress || 'unknown',
                    port: (client as any)._sock?.remotePort || 0,
                    connectTime: now,
                    lastActivity: now,
                    clientVersion: (client as any)._client?.version || 'unknown',
                    supportedAuth: [],
                    serverHostname: os.hostname(),
                    serverPlatform: os.platform(),
                    serverArch: os.arch(),
                    bytesRead: 0,
                    bytesWritten: 0,
                    activeChannels: 0
                };

                Logger.info(`New SSH connection from ${clientInfo.ip}:${clientInfo.port} (${clientInfo.clientVersion})`);

                // Track data transfer
                (client as any)._sock?.on('data', (data: Buffer) => {
                    clientInfo.bytesRead += data.length;
                    clientInfo.lastActivity = new Date();
                });

                client.on('authentication', (ctx: AuthContext) => {
                    clientInfo.username = ctx.username;
                    // Get supported auth methods from the context
                    if ((ctx as any).authMethods) {
                        clientInfo.supportedAuth = (ctx as any).authMethods;
                    } else {
                        clientInfo.supportedAuth = ['password', 'publickey'];  // Default supported methods
                    }
                    this.handleAuth(ctx);
                });

                client.on('ready', () => {
                    Logger.info(`Client ${clientInfo.username}@${clientInfo.ip} authenticated successfully`);
                    this.handleClientReady(client, clientInfo);
                });

                client.on('error', (err: Error) => {
                    Logger.error(`SSH client error for ${clientInfo.username}@${clientInfo.ip}: ${err}`);
                    client.end();
                });

                // Track channel creation/closure
                client.on('session', () => {
                    clientInfo.activeChannels++;
                });

                client.on('end', () => {
                    const duration = new Date().getTime() - clientInfo.connectTime.getTime();
                    Logger.info(
                        `Client ${clientInfo.username}@${clientInfo.ip} disconnected after ${duration/1000}s. ` +
                        `Data transferred: ${clientInfo.bytesRead}B read, ${clientInfo.bytesWritten}B written`
                    );
                });
            });

            // Start listening
            await new Promise<void>((resolve, reject) => {
                this.server.on('error', reject);
                this.server.listen(this.port, '0.0.0.0', () => {
                    Logger.info(`SSH service listening on port ${this.port}`);
                    resolve();
                });
            });

            // Connect to ATC server with retries
            try {
                await this.atc.connect(5, 2000);
                Logger.info('Successfully connected to ATC server');
            } catch (error) {
                Logger.warn(`Failed to connect to ATC server: ${error}. Will continue without ATC integration.`);
            }

            Logger.info('SSH service started successfully');
        } catch (error) {
            Logger.error(`Failed to start SSH service: ${error}`);
            if (this.server) {
                this.server.close();
            }
            throw error;
        }
    }

    /**
     * Handles client authentication requests
     */
    private handleAuth(ctx: AuthContext): void {
        if (ctx.method === 'publickey') {
            this.handlePublicKeyAuth(ctx);
        } else if (ctx.method === 'password') {
            this.handlePasswordAuth(ctx);
        } else {
            ctx.reject(['password', 'publickey']);
        }
    }

    /**
     * Handles public key authentication
     */
    private handlePublicKeyAuth(ctx: AuthContext): void {
        if (ctx.method !== 'publickey') return;
        
        const authorized_keys = path.join(process.cwd(), 'config', 'authorized_keys');
        
        try {
            const keys = fs.readFileSync(authorized_keys, 'utf8');
            const pubKey = (ctx as any).key?.data?.toString('base64');
            if (pubKey && keys.includes(pubKey)) {
                ctx.accept();
            } else {
                ctx.reject();
            }
        } catch (error) {
            Logger.error(`Key auth error: ${error}`);
            ctx.reject();
        }
    }

    /**
     * Handles password authentication requests
     */
    private handlePasswordAuth(ctx: AuthContext): void {
        if (ctx.method !== 'password') return;
        
        const password = (ctx as any).password;
        if (password === this.generatedPassword) {
            ctx.accept();
        } else {
            ctx.reject();
        }
    }

    /**
     * Sets up session handlers for authenticated clients
     */
    private handleClientReady(client: Connection, clientInfo: ClientInfo): void {
        const sessionId = `session_${Date.now()}`;
        
        client.on('session', (accept: () => Session) => {
            const session: Session = accept();
            
            session.on('pty', (accept: () => void) => {
                accept();
            });

            session.on('shell', (accept: () => any) => {
                const stream = accept();
                this.handleShellSession(sessionId, stream, clientInfo);
            });

            session.on('sftp', (accept: () => SFTPWrapper) => {
                const sftp: SFTPWrapper = accept();
                this.handleSFTP(sftp);
            });
        });
    }

    /**
     * Handles shell session creation and management with Tmux integration
     */
    private async handleShellSession(sessionId: string, stream: any, clientInfo: ClientInfo): Promise<void> {
        try {
            // Check if there's an existing tmux session to attach to
            const existingSessions = await this.tmux.listSessions();
            const existingSession = existingSessions.find(s => s.name === clientInfo.username);
            
            let tmuxSessionId: string;
            let isTmux = true;

            if (existingSession) {
                // Attach to existing session
                tmuxSessionId = existingSession.id;
                Logger.info(`Attaching to existing tmux session for ${clientInfo.username}`);
            } else {
                // Create new tmux session
                tmuxSessionId = `${clientInfo.username}_${Date.now()}`;
                await this.tmux.createSession(tmuxSessionId, {
                    name: clientInfo.username,
                    group: 'ssh-users',  // Allow other SSH users to attach
                    persist: true,       // Enable session persistence
                    layout: 'even-horizontal'
                });
                Logger.info(`Created new tmux session for ${clientInfo.username}`);
            }

            // Spawn shell that attaches to tmux session
            const shell = pty.spawn('tmux', [
                '-S', this.tmux.getSocketPath(tmuxSessionId),
                'attach-session',
                '-t', tmuxSessionId
            ], {
                name: 'xterm-color',
                cols: 80,
                rows: 24,
                cwd: process.env.HOME,
                env: {
                    ...process.env,
                    SSH_CLIENT: `${clientInfo.ip} ${clientInfo.port}`,
                    SSH_CONNECTION: `${clientInfo.ip} ${clientInfo.port} ${os.hostname()} ${this.port}`,
                    SSH_TTY: '/dev/pts/0',
                    TMUX_SOCKET: this.tmux.getSocketPath(tmuxSessionId)
                }
            });

            this.sessions.set(sessionId, { shell, isTmux, clientInfo });

            // Set up data handlers
            shell.onData((data) => {
                clientInfo.bytesWritten += data.length;
                clientInfo.lastActivity = new Date();
                
                // Send to ATC for logging/monitoring
                this.atc.send({
                    type: 'terminal',
                    sessionId,
                    data,
                    metadata: {
                        username: clientInfo.username,
                        ip: clientInfo.ip,
                        timestamp: new Date().toISOString(),
                        isTmux: true,
                        tmuxSession: tmuxSessionId
                    }
                });
                
                stream.write(data);
            });

            stream.on('data', (data: Buffer) => {
                clientInfo.bytesRead += data.length;
                clientInfo.lastActivity = new Date();
                shell.write(data.toString());
            });

            // Handle window resize events
            stream.on('resize', (rows: number, cols: number) => {
                shell.resize(cols, rows);
            });

            stream.on('close', async () => {
                const session = this.sessions.get(sessionId);
                if (session) {
                    if (session.isTmux) {
                        // Save session state before closing
                        await this.tmux.enablePersistence(tmuxSessionId);
                    }
                    session.shell.kill();
                    this.sessions.delete(sessionId);
                    clientInfo.activeChannels--;
                    Logger.info(
                        `Session ${sessionId} closed for ${clientInfo.username}@${clientInfo.ip}. ` +
                        `Active channels remaining: ${clientInfo.activeChannels}`
                    );
                }
            });

        } catch (error) {
            Logger.error(`Shell session error for ${clientInfo.username}@${clientInfo.ip}: ${error}`);
            stream.end();
        }
    }

    /**
     * Handles SFTP subsystem operations
     */
    private handleSFTP(sftp: SFTPWrapper): void {
        // Implement SFTP handlers
        sftp.on('MKDIR', (reqid: number, path: string) => {
            fs.mkdir(path, { recursive: true }, (err) => {
                if (err) {
                    sftp.status(reqid, SFTP_STATUS.FAILURE);
                    return;
                }
                sftp.status(reqid, SFTP_STATUS.OK);
            });
        });

        sftp.on('STAT', (reqid: number, path: string) => {
            fs.stat(path, (err, stats) => {
                if (err) {
                    sftp.status(reqid, SFTP_STATUS.NO_SUCH_FILE);
                    return;
                }
                const attrs: Attributes = {
                    mode: stats.mode,
                    uid: stats.uid,
                    gid: stats.gid,
                    size: stats.size,
                    atime: Math.floor(stats.atime.getTime() / 1000),
                    mtime: Math.floor(stats.mtime.getTime() / 1000)
                };
                sftp.attrs(reqid, attrs);
            });
        });

        // Handle file reading
        sftp.on('READ', (reqid: number, handle: Buffer, offset: number, length: number) => {
            // Read file in chunks
            const buffer = Buffer.alloc(length);
            fs.read(handle.readInt32BE(0), buffer, 0, length, offset, (err, bytesRead, buffer) => {
                if (err) {
                    sftp.status(reqid, SFTP_STATUS.FAILURE);
                    return;
                }
                if (bytesRead === 0) {
                    sftp.status(reqid, SFTP_STATUS.EOF);
                    return;
                }
                sftp.data(reqid, buffer.slice(0, bytesRead));
            });
        });

        // Handle file writing
        sftp.on('WRITE', (reqid: number, handle: Buffer, offset: number, data: Buffer) => {
            fs.write(handle.readInt32BE(0), data, 0, data.length, offset, (err) => {
                if (err) {
                    sftp.status(reqid, SFTP_STATUS.FAILURE);
                    return;
                }
                sftp.status(reqid, SFTP_STATUS.OK);
            });
        });

        // Handle file opening
        sftp.on('OPEN', (reqid: number, filename: string, flags: number, _attrs: Attributes) => {
            // Convert SFTP flags to fs.open flags
            let fsFlags = 'r';
            if (flags & SFTP_OPEN_MODE.READ && flags & SFTP_OPEN_MODE.WRITE) {
                fsFlags = 'r+';
            } else if (flags & SFTP_OPEN_MODE.WRITE) {
                fsFlags = 'w';
            }

            fs.open(filename, fsFlags, (err, fd) => {
                if (err) {
                    sftp.status(reqid, SFTP_STATUS.NO_SUCH_FILE);
                    return;
                }
                const handle = Buffer.alloc(4);
                handle.writeInt32BE(fd, 0);
                sftp.handle(reqid, handle);
            });
        });

        // Handle file closing
        sftp.on('CLOSE', (reqid: number, handle: Buffer) => {
            fs.close(handle.readInt32BE(0), (err) => {
                if (err) {
                    sftp.status(reqid, SFTP_STATUS.FAILURE);
                    return;
                }
                sftp.status(reqid, SFTP_STATUS.OK);
            });
        });

        // Handle directory listing
        sftp.on('READDIR', (reqid: number, handle: Buffer) => {
            const path = handle.toString();
            fs.readdir(path, { withFileTypes: true }, (err, files) => {
                if (err) {
                    sftp.status(reqid, SFTP_STATUS.NO_SUCH_FILE);
                    return;
                }
                if (files.length === 0) {
                    sftp.status(reqid, SFTP_STATUS.EOF);
                    return;
                }

                // Get process IDs safely
                const uid = typeof process.getuid === 'function' ? process.getuid() : 0;
                const gid = typeof process.getgid === 'function' ? process.getgid() : 0;

                const entries = files.map(file => ({
                    filename: file.name,
                    longname: `${file.isDirectory() ? 'd' : '-'}rwxr-xr-x 1 ${uid} ${gid} 0 Jan 1 1970 ${file.name}`,
                    attrs: {
                        mode: file.isDirectory() ? 0o755 | 0o040000 : 0o644,
                        uid,
                        gid,
                        size: 0,
                        atime: 0,
                        mtime: 0
                    }
                }));
                sftp.name(reqid, entries);
            });
        });

        // Handle file removal
        sftp.on('REMOVE', (reqid: number, path: string) => {
            fs.unlink(path, (err) => {
                if (err) {
                    sftp.status(reqid, SFTP_STATUS.NO_SUCH_FILE);
                    return;
                }
                sftp.status(reqid, SFTP_STATUS.OK);
            });
        });

        // Handle directory removal
        sftp.on('RMDIR', (reqid: number, path: string) => {
            fs.rmdir(path, (err) => {
                if (err) {
                    sftp.status(reqid, SFTP_STATUS.NO_SUCH_FILE);
                    return;
                }
                sftp.status(reqid, SFTP_STATUS.OK);
            });
        });

        // Handle file/directory renaming
        sftp.on('RENAME', (reqid: number, oldPath: string, newPath: string) => {
            fs.rename(oldPath, newPath, (err) => {
                if (err) {
                    sftp.status(reqid, SFTP_STATUS.NO_SUCH_FILE);
                    return;
                }
                sftp.status(reqid, SFTP_STATUS.OK);
            });
        });
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