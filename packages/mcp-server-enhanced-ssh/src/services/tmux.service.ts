import { spawn } from 'child_process';
import { Logger } from '../utils/logger';

export class TmuxService {
    constructor() {}
    
    async createSession(sessionId: string): Promise<void> {
        try {
            await this.executeCommand('new-session', ['-d', '-s', sessionId]);
            Logger.info(`Created new tmux session: ${sessionId}`);
        } catch (error) {
            Logger.error(`Failed to create tmux session: ${error}`);
            throw error;
        }
    }
    
    async killSession(sessionId: string): Promise<void> {
        try {
            await this.executeCommand('kill-session', ['-t', sessionId]);
            Logger.info(`Killed tmux session: ${sessionId}`);
        } catch (error) {
            Logger.error(`Failed to kill tmux session: ${error}`);
            throw error;
        }
    }
    
    async listSessions(): Promise<string[]> {
        try {
            const output = await this.executeCommand('list-sessions', ['-F', '#{session_name}']);
            return output.split('\n').filter(Boolean);
        } catch (error) {
            Logger.error(`Failed to list tmux sessions: ${error}`);
            throw error;
        }
    }
    
    public executeCommand(command: string, args: string[]): Promise<string> {
        return new Promise((resolve, reject) => {
            const tmux = spawn('tmux', [command, ...args]);
            let output = '';
            let error = '';
            
            tmux.stdout.on('data', (data) => {
                output += data.toString();
            });
            
            tmux.stderr.on('data', (data) => {
                error += data.toString();
            });
            
            tmux.on('close', (code) => {
                if (code === 0) {
                    resolve(output.trim());
                } else {
                    reject(new Error(`tmux ${command} failed: ${error}`));
                }
            });
        });
    }
}