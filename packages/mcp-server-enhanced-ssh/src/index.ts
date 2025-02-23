import { SSHService } from './services/ssh.service';
import { Logger } from './utils/logger';

async function main() {
    const port = parseInt(process.env.SSH_PORT || '6480', 10);
    const apiPort = parseInt(process.env.API_PORT || '6481', 10);
    const sshService = new SSHService(port, apiPort);
    
    // Handle graceful shutdown
    process.on('SIGINT', async () => {
        Logger.info('Shutting down SSH service...');
        try {
            await sshService.stop();
            process.exit(0);
        } catch (error) {
            Logger.error(`Error during shutdown: ${error}`);
            process.exit(1);
        }
    });
    
    try {
        await sshService.start();
    } catch (error) {
        Logger.error(`Failed to start SSH service: ${error}`);
        process.exit(1);
    }
}

main().catch((error) => {
    Logger.error(`Unhandled error: ${error}`);
    process.exit(1);
});