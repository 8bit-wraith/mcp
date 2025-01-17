import { EventEmitter } from 'events';
import WebSocket from 'ws';
import { Logger } from '../utils/logger';

export class ATCClient extends EventEmitter {
    private ws: WebSocket | null = null;
    
    constructor(private readonly url: string) {
        super();
    }
    
    async connect(retries = 5, delay = 2000): Promise<void> {
        return new Promise((resolve, reject) => {
            const attemptConnect = (attemptsLeft: number) => {
                try {
                    this.ws = new WebSocket(this.url);
                    
                    this.ws.onopen = () => {
                        Logger.info('Connected to ATC server');
                        this.emit('connected');
                        resolve();
                    };
                    
                    this.ws.onmessage = (event: WebSocket.MessageEvent) => {
                        const data = JSON.parse(event.data.toString());
                        this.emit('data', data);
                    };
                    
                    this.ws.onerror = (error: WebSocket.ErrorEvent) => {
                        Logger.warn(`WebSocket connection attempt failed: ${error.message}`);
                        if (attemptsLeft > 0) {
                            Logger.info(`Retrying connection in ${delay/1000} seconds... (${attemptsLeft} attempts left)`);
                            setTimeout(() => attemptConnect(attemptsLeft - 1), delay);
                        } else {
                            const finalError = new Error('Failed to connect to ATC server after multiple attempts');
                            Logger.error(finalError.message);
                            reject(finalError);
                        }
                    };
                    
                    this.ws.onclose = () => {
                        Logger.info('Disconnected from ATC server');
                        this.emit('disconnected');
                    };
                } catch (error) {
                    Logger.error(`Failed to create WebSocket: ${error}`);
                    reject(error);
                }
            };
            
            attemptConnect(retries);
        });
    }
    
    async send(data: any) {
        if (!this.ws) {
            throw new Error('Not connected to ATC server');
        }
        this.ws.send(JSON.stringify(data));
    }
    
    async disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
}