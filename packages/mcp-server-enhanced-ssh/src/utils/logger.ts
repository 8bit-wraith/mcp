export class Logger {
    static info(message: string) {
        console.log(`[INFO] ${message}`);
    }

    static error(message: string) {
        console.error(`[ERROR] ${message}`);
    }

    static warn(message: string) {
        console.warn(`[WARN] ${message}`);
    }

    static debug(message: string) {
        console.debug(`[DEBUG] ${message}`);
    }
}