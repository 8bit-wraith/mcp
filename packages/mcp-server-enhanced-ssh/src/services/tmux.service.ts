import { spawn } from 'child_process';
import { Logger } from '../utils/logger';

export interface TmuxSession {
    id: string;
    name: string;
    windows: string[];
    created: Date;
}

export class TmuxService {
    private logger: Logger;
    private sessions: Map<string, TmuxSession>;

    constructor() {
        this.logger = new Logger('TmuxService');
        this.sessions = new Map();
    }

    public createSession(name?: string): TmuxSession {
        const sessionId = name || `mcp-${Date.now()}`;
        
        // Create new tmux session
        spawn('tmux', ['new-session', '-d', '-s', sessionId]);

        const session: TmuxSession = {
            id: sessionId,
            name: name || sessionId,
            windows: ['main'],
            created: new Date()
        };

        this.sessions.set(sessionId, session);
        this.logger.info(`Created new tmux session: ${sessionId}`);

        return session;
    }

    public listSessions(): TmuxSession[] {
        return Array.from(this.sessions.values());
    }

    public async attachToSession(sessionId: string): Promise<boolean> {
        const session = this.sessions.get(sessionId);
        if (!session) {
            this.logger.error(`Session not found: ${sessionId}`);
            return false;
        }

        return true;
    }

    public createWindow(sessionId: string, name: string): boolean {
        const session = this.sessions.get(sessionId);
        if (!session) return false;

        spawn('tmux', ['new-window', '-t', sessionId, '-n', name]);
        session.windows.push(name);
        
        return true;
    }
} 