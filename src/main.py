#!/usr/bin/env python3
"""
Portfolio Manager Application Entry Point

This application can be run in web server mode (default) or desktop mode.

Usage:
    python main.py              # Start web server (default)
    python main.py --web        # Start web server  
    python main.py --desktop    # Start desktop GUI (not implemented yet)
"""

import argparse
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_web_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = True):
    """Run the FastAPI web server."""
    import uvicorn
    from web_server.app import app
    
    print(f"Starting Portfolio Manager web server...")
    print(f"Access the application at: http://{host}:{port}")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "web_server.app:app",
        host=host,
        port=port,
        reload=reload,
        reload_dirs=["."]
    )


def run_desktop_app():
    """Run the desktop GUI application (not implemented yet)."""
    print("Desktop mode is not implemented yet.")
    print("Please use web mode: python main.py --web")
    sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Portfolio Manager Application")
    parser.add_argument(
        "--mode",
        choices=["web", "desktop"],
        default="web",
        help="Application mode (default: web)"
    )
    parser.add_argument(
        "--web",
        action="store_const",
        const="web",
        dest="mode",
        help="Run in web server mode"
    )
    parser.add_argument(
        "--desktop",
        action="store_const",
        const="desktop",
        dest="mode",
        help="Run in desktop GUI mode"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind the web server to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the web server to (default: 8000)"
    )
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Disable auto-reload for production"
    )
    
    args = parser.parse_args()
    
    if args.mode == "web":
        run_web_server(
            host=args.host,
            port=args.port,
            reload=not args.no_reload
        )
    elif args.mode == "desktop":
        run_desktop_app()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()