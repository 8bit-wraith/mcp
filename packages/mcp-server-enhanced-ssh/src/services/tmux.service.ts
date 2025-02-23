import { spawn } from 'child_process';
import { Logger } from '../utils/logger';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

/**
 * Represents a window within a Tmux session
 */
interface TmuxWindow {
    /** Unique window identifier */
    id: string;
    /** Window name (user-defined or default) */
    name: string;
    /** Whether this window is currently active */
    active: boolean;
    /** Number of panes in this window */
    panes: number;
}

/**
 * Represents a Tmux session with its associated windows and metadata
 */
interface TmuxSession {
    /** Unique session identifier */
    id: string;
    /** Session name (user-defined or default) */
    name: string;
    /** List of windows in this session */
    windows: TmuxWindow[];
    /** Session creation timestamp */
    created: Date;
    /** Unix socket path for this session */
    socket?: string;
    /** Unix group for shared access */
    group?: string;
}

/**
 * Service for managing Tmux sessions and windows
 *
 * This service provides high-level operations for:
 * - Creating and managing Tmux sessions
 * - Window and pane management
 * - Session persistence and restoration
 * - Multi-user session sharing
 * - Custom socket handling
 *
 * Features:
 * - Persistent sessions with automatic state saving
 * - Group-based access control
 * - Custom socket directory management
 * - Window layout customization
 * - Error handling and logging
 */
export class TmuxService {
    /** Directory for storing Tmux socket files */
    private readonly SOCKET_DIR = path.join(os.homedir(), '.tmux-sockets');
    /** Default window layout configuration */
    private readonly DEFAULT_LAYOUT = 'even-horizontal';
    /** Directory for storing session persistence data */
    private readonly RESURRECT_DIR = path.join(os.homedir(), '.tmux/resurrect');

    /**
     * Initializes the TmuxService and creates required directories
     *
     * Creates:
     * - Socket directory for Tmux communication
     * - Resurrect directory for session persistence
     */
    constructor() {
        if (!fs.existsSync(this.SOCKET_DIR)) {
            fs.mkdirSync(this.SOCKET_DIR, { recursive: true });
        }
        
        // Ensure resurrect directory exists
        if (!fs.existsSync(this.RESURRECT_DIR)) {
            fs.mkdirSync(this.RESURRECT_DIR, { recursive: true });
        }
    }

    /**
     * Gets the Unix socket path for a given session
     * @param sessionId - Unique identifier for the session
     * @returns Full path to the session's Unix socket file
     */
    public getSocketPath(sessionId: string): string {
        return path.join(this.SOCKET_DIR, `${sessionId}.sock`);
    }
    
    /**
     * Creates a new Tmux session with specified options
     *
     * @param sessionId - Unique identifier for the new session
     * @param options - Session configuration options
     * @param options.name - Display name for the session (defaults to sessionId)
     * @param options.group - Unix group for shared access
     * @param options.layout - Window layout (defaults to even-horizontal)
     * @param options.persist - Whether to enable session persistence
     *
     * @throws Error if session creation fails
     */
    async createSession(sessionId: string, options: {
        name?: string,
        group?: string,
        layout?: string,
        persist?: boolean
    } = {}): Promise<void> {
        try {
            const socketPath = this.getSocketPath(sessionId);
            const args = [
                'new-session',
                '-d',  // Detached
                '-s', options.name || sessionId,
                '-P'  // Print session info
            ];

            if (options.layout) {
                args.push('-l', options.layout);
            }

            // Use custom socket
            args.unshift('-S', socketPath);

            await this.executeCommand('new-session', args);

            // Set group permissions if specified
            if (options.group) {
                fs.chmodSync(socketPath, 0o770);
                await this.executeCommand('run-shell', [`chgrp ${options.group} ${socketPath}`]);
            }

            // Enable session persistence if requested
            if (options.persist) {
                await this.enablePersistence(sessionId);
            }

            Logger.info(`Created new tmux session: ${sessionId} (socket: ${socketPath})`);
        } catch (error) {
            Logger.error(`Failed to create tmux session: ${error}`);
            throw error;
        }
    }

    async killSession(sessionId: string): Promise<void> {
        try {
            const socketPath = this.getSocketPath(sessionId);
            await this.executeCommand('kill-session', ['-S', socketPath, '-t', sessionId]);
            
            // Clean up socket file
            if (fs.existsSync(socketPath)) {
                fs.unlinkSync(socketPath);
            }
            
            Logger.info(`Killed tmux session: ${sessionId}`);
        } catch (error) {
            Logger.error(`Failed to kill tmux session: ${error}`);
            throw error;
        }
    }

    async listSessions(): Promise<TmuxSession[]> {
        try {
            const format = [
                '#{session_id}',
                '#{session_name}',
                '#{session_created}',
                '#{socket_path}'
            ].join(',');
            
            const output = await this.executeCommand('list-sessions', ['-F', format]);
            return output.split('\n')
                .filter(Boolean)
                .map(line => {
                    const [id, name, created, socket] = line.split(',');
                    return {
                        id,
                        name,
                        created: new Date(parseInt(created) * 1000),
                        socket,
                        windows: []  // Populated by listWindows if needed
                    };
                });
        } catch (error) {
            Logger.error(`Failed to list tmux sessions: ${error}`);
            throw error;
        }
    }

    /**
     * Lists all windows in a Tmux session
     *
     * @param sessionId - ID of the session to list windows for
     * @returns Array of TmuxWindow objects containing window details
     * @throws Error if unable to list windows
     *
     * Each window object includes:
     * - Window ID and name
     * - Active status
     * - Number of panes
     */
    async listWindows(sessionId: string): Promise<TmuxWindow[]> {
        try {
            const format = [
                '#{window_id}',
                '#{window_name}',
                '#{window_active}',
                '#{window_panes}'
            ].join(',');
            
            const output = await this.executeCommand('list-windows', [
                '-S', this.getSocketPath(sessionId),
                '-t', sessionId,
                '-F', format
            ]);
            
            return output.split('\n')
                .filter(Boolean)
                .map(line => {
                    const [id, name, active, panes] = line.split(',');
                    return {
                        id,
                        name,
                        active: active === '1',
                        panes: parseInt(panes)
                    };
                });
        } catch (error) {
            Logger.error(`Failed to list tmux windows: ${error}`);
            throw error;
        }
    }

    /**
     * Splits a Tmux window into multiple panes
     *
     * @param sessionId - ID of the session containing the window
     * @param windowId - ID of the window to split
     * @param direction - Split direction: 'h' for horizontal, 'v' for vertical
     * @throws Error if window split fails
     *
     * Creates a new pane by:
     * - Splitting the specified window
     * - Using the specified direction
     * - Maintaining the current working directory
     */
    async splitWindow(sessionId: string, windowId: string, direction: 'h' | 'v'): Promise<void> {
        try {
            await this.executeCommand('split-window', [
                '-S', this.getSocketPath(sessionId),
                '-t', `${sessionId}:${windowId}`,
                direction === 'h' ? '-h' : '-v'
            ]);
            Logger.info(`Split window ${windowId} in session ${sessionId} ${direction === 'h' ? 'horizontally' : 'vertically'}`);
        } catch (error) {
            Logger.error(`Failed to split window: ${error}`);
            throw error;
        }
    }

    async resizePane(sessionId: string, paneId: string, size: number, direction: 'U' | 'D' | 'L' | 'R'): Promise<void> {
        try {
            await this.executeCommand('resize-pane', [
                '-S', this.getSocketPath(sessionId),
                '-t', `${sessionId}:${paneId}`,
                `-${direction}`,
                size.toString()
            ]);
        } catch (error) {
            Logger.error(`Failed to resize pane: ${error}`);
            throw error;
        }
    }

    async enablePersistence(sessionId: string): Promise<void> {
        try {
            // Save session state
            await this.executeCommand('run-shell', [
                '-S', this.getSocketPath(sessionId),
                `tmux-resurrect save ${path.join(this.RESURRECT_DIR, sessionId)}`
            ]);
            Logger.info(`Enabled persistence for session ${sessionId}`);
        } catch (error) {
            Logger.error(`Failed to enable session persistence: ${error}`);
            throw error;
        }
    }

    async restoreSession(sessionId: string): Promise<void> {
        try {
            await this.executeCommand('run-shell', [
                '-S', this.getSocketPath(sessionId),
                `tmux-resurrect restore ${path.join(this.RESURRECT_DIR, sessionId)}`
            ]);
            Logger.info(`Restored session ${sessionId}`);
        } catch (error) {
            Logger.error(`Failed to restore session: ${error}`);
            throw error;
        }
    }

    async sendKeys(sessionId: string, target: string, keys: string): Promise<void> {
        try {
            await this.executeCommand('send-keys', [
                '-S', this.getSocketPath(sessionId),
                '-t', `${sessionId}:${target}`,
                keys,
                'Enter'
            ]);
        } catch (error) {
            Logger.error(`Failed to send keys: ${error}`);
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