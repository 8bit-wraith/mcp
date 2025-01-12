import { Server } from 'ssh2';
import * as pty from 'node-pty';
import { WebSocket } from 'ws';
import { ATCClient } from './atc.client';

export class SSHService {
    private server: Server;
    private atc: ATCClient;

    constructor() {
        this.server = new Server({
            hostKeys: [/* we'll load these from config */]
        });
        this.atc = new ATCClient('ws://localhost:8000/ws/terminal');
    }

    private async handleSession(accept: any, reject: any): Promise<void> {
        const session = accept();
        const sessionId = `mcp-${Date.now()}`;
        
        // Connect to ATC
        await this.atc.connect(sessionId);
        
        session.on('shell', (accept: any) => {
            const shell = accept();
            
            // Now our shell commands go through ATC
            this.atc.on('data', (data) => shell.write(data));
            shell.on('data', (data: Buffer) => this.atc.send({
                type: 'terminal',
                data: data.toString()
            }));
        });
    }
} 