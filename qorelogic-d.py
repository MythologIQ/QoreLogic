import sys
import os
import signal
import time
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

from local_fortress.mcp_server.server import mcp

# Setup basic logging for the daemon wrapper
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [DAEMON] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("QORELOGIC-Daemon")

SHUTDOWN_FLAG = False

def signal_handler(signum, frame):
    global SHUTDOWN_FLAG
    logger.info(f"Signal {signum} received. Initiating graceful shutdown...")
    SHUTDOWN_FLAG = True
    # In a real asyncio server, we might need to cancel tasks here or rely on KeyboardInterrupt
    # propagating if this runs in main thread. 
    # Since server_main() blocks, we might need to rely on the server's own handling.
    # However, standard python signal handling raises KeyboardInterrupt or SystemExit in main thread.
    sys.exit(0)

def main():
    logger.info("Starting QoreLogic Persistent Daemon...")
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Write PID file
    pid = os.getpid()
    pid_file = PROJECT_ROOT / "qorelogic.pid"
    with open(pid_file, "w") as f:
        f.write(str(pid))
        
    logger.info(f"Daemon running with PID {pid}")
    
    try:
        # Run the server
        # Note: If mcp.run() handles its own signals, it might override ours.
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Daemon interrupted.")
    except Exception as e:
        logger.error(f"Daemon crashed: {e}", exc_info=True)
    finally:
        logger.info("Cleaning up...")
        if pid_file.exists():
            pid_file.unlink()
        logger.info("Daemon stopped.")

if __name__ == "__main__":
    main()
