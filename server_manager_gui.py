#!/usr/bin/env python3
"""
Server Manager GUI with PyGame
Complete server management and testing interface
"""

import pygame
import pygame_gui
import sys
import os
import threading
import queue
import time
import json
import subprocess
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver
import webbrowser

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 123, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (200, 200, 200)

class ServerManager:
    """Manages the test server"""
    def __init__(self, port=8080):
        self.port = port
        self.server = None
        self.thread = None
        self.running = False
        self.log_queue = queue.Queue()
        
    def log(self, message, level="INFO"):
        """Add log message to queue"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_queue.put({
            'timestamp': timestamp,
            'level': level,
            'message': message
        })
        
    def start(self):
        """Start the server"""
        if self.running:
            self.log("Server already running", "WARNING")
            return
            
        try:
            handler = SimpleHTTPRequestHandler
            self.server = socketserver.TCPServer(("", self.port), handler)
            self.server.allow_reuse_address = True
            
            def serve():
                self.running = True
                self.log(f"Server started on http://localhost:{self.port}", "SUCCESS")
                self.server.serve_forever()
                
            self.thread = threading.Thread(target=serve)
            self.thread.daemon = True
            self.thread.start()
            time.sleep(0.5)
            
        except Exception as e:
            self.log(f"Failed to start server: {e}", "ERROR")
            
    def stop(self):
        """Stop the server"""
        if self.server and self.running:
            self.server.shutdown()
            self.server.server_close()
            self.running = False
            self.log("Server stopped", "SUCCESS")
        else:
            self.log("Server not running", "WARNING")
            
    def restart(self):
        """Restart the server"""
        self.log("Restarting server...", "INFO")
        self.stop()
        time.sleep(1)
        self.start()

class TestRunner:
    """Runs automated tests"""
    def __init__(self, server_manager):
        self.server_manager = server_manager
        self.running = False
        self.thread = None
        
    def run_tests(self):
        """Run the test suite in a separate thread"""
        if self.running:
            self.server_manager.log("Tests already running", "WARNING")
            return
            
        def test_thread():
            self.running = True
            self.server_manager.log("Starting automated tests...", "INFO")
            
            try:
                # Run the test script
                result = subprocess.run([
                    sys.executable, 
                    "test_server.py"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.server_manager.log("All tests passed!", "SUCCESS")
                else:
                    self.server_manager.log("Tests failed! Check logs for details", "ERROR")
                    
                # Parse test results if available
                try:
                    with open('test_results.json', 'r') as f:
                        results = json.load(f)
                        for test in results:
                            status = "PASS" if test['passed'] else "FAIL"
                            self.server_manager.log(f"{status}: {test['test']} - {test['message']}", 
                                                  "SUCCESS" if test['passed'] else "ERROR")
                except:
                    pass
                    
            except Exception as e:
                self.server_manager.log(f"Test error: {e}", "ERROR")
            finally:
                self.running = False
                
        self.thread = threading.Thread(target=test_thread)
        self.thread.daemon = True
        self.thread.start()

class ServerManagerGUI:
    """PyGame GUI for server management"""
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("CFW Schedule Server Manager")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize UI manager
        self.ui_manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # Server manager
        self.server_manager = ServerManager()
        self.test_runner = TestRunner(self.server_manager)
        
        # UI Elements
        self.create_ui()
        
        # Log display
        self.log_messages = []
        self.max_log_messages = 20
        
    def create_ui(self):
        """Create UI elements"""
        # Title
        self.title_font = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 24)
        self.log_font = pygame.font.Font(None, 18)
        
        # Buttons
        button_width = 150
        button_height = 40
        button_spacing = 10
        start_x = 50
        start_y = 100
        
        self.start_button = pygame.Rect(start_x, start_y, button_width, button_height)
        self.stop_button = pygame.Rect(start_x + button_width + button_spacing, start_y, button_width, button_height)
        self.restart_button = pygame.Rect(start_x + 2 * (button_width + button_spacing), start_y, button_width, button_height)
        self.test_button = pygame.Rect(start_x + 3 * (button_width + button_spacing), start_y, button_width, button_height)
        
        # Additional buttons
        self.open_browser_button = pygame.Rect(start_x, start_y + 60, 200, button_height)
        self.clear_logs_button = pygame.Rect(start_x + 220, start_y + 60, 150, button_height)
        
        # Status indicator
        self.status_rect = pygame.Rect(WINDOW_WIDTH - 200, 20, 180, 30)
        
        # Log area
        self.log_area = pygame.Rect(20, 220, WINDOW_WIDTH - 40, WINDOW_HEIGHT - 240)
        
    def draw_button(self, rect, text, color, hover=False):
        """Draw a button"""
        if hover:
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, WHITE, rect, 2)
        else:
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, DARK_GRAY, rect, 2)
            
        text_surface = self.font.render(text, True, WHITE if color != WHITE else BLACK)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
        
    def draw_status(self):
        """Draw server status indicator"""
        status_color = GREEN if self.server_manager.running else RED
        status_text = "Server: Running" if self.server_manager.running else "Server: Stopped"
        
        pygame.draw.rect(self.screen, status_color, self.status_rect)
        pygame.draw.rect(self.screen, BLACK, self.status_rect, 2)
        
        text_surface = self.font.render(status_text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.status_rect.center)
        self.screen.blit(text_surface, text_rect)
        
    def update_logs(self):
        """Update log messages from queue"""
        while not self.server_manager.log_queue.empty():
            try:
                log_entry = self.server_manager.log_queue.get_nowait()
                self.log_messages.append(log_entry)
                if len(self.log_messages) > self.max_log_messages:
                    self.log_messages.pop(0)
            except:
                break
                
    def draw_logs(self):
        """Draw log messages"""
        # Log area background
        pygame.draw.rect(self.screen, WHITE, self.log_area)
        pygame.draw.rect(self.screen, BLACK, self.log_area, 2)
        
        # Title
        title_surface = self.font.render("Server Logs", True, BLACK)
        self.screen.blit(title_surface, (self.log_area.x + 10, self.log_area.y - 30))
        
        # Log messages
        y_offset = 10
        for log in self.log_messages:
            # Color based on level
            if log['level'] == 'ERROR':
                color = RED
            elif log['level'] == 'SUCCESS':
                color = GREEN
            elif log['level'] == 'WARNING':
                color = (255, 165, 0)  # Orange
            else:
                color = BLACK
                
            text = f"[{log['timestamp']}] {log['message']}"
            text_surface = self.log_font.render(text, True, color)
            
            if text_surface.get_width() > self.log_area.width - 20:
                # Truncate long messages
                text = text[:80] + "..."
                text_surface = self.log_font.render(text, True, color)
                
            self.screen.blit(text_surface, (self.log_area.x + 10, self.log_area.y + y_offset))
            y_offset += 20
            
    def handle_events(self):
        """Handle pygame events"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.start_button.collidepoint(mouse_pos):
                    self.server_manager.start()
                elif self.stop_button.collidepoint(mouse_pos):
                    self.server_manager.stop()
                elif self.restart_button.collidepoint(mouse_pos):
                    self.server_manager.restart()
                elif self.test_button.collidepoint(mouse_pos):
                    if self.server_manager.running:
                        self.test_runner.run_tests()
                    else:
                        self.server_manager.log("Start server before running tests", "WARNING")
                elif self.open_browser_button.collidepoint(mouse_pos):
                    if self.server_manager.running:
                        webbrowser.open(f"http://localhost:{self.server_manager.port}")
                    else:
                        self.server_manager.log("Start server first", "WARNING")
                elif self.clear_logs_button.collidepoint(mouse_pos):
                    self.log_messages.clear()
                    
            self.ui_manager.process_events(event)
            
    def draw(self):
        """Draw the GUI"""
        self.screen.fill(LIGHT_GRAY)
        
        # Title
        title_surface = self.title_font.render("CFW Schedule Server Manager", True, BLACK)
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, 40))
        self.screen.blit(title_surface, title_rect)
        
        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw buttons
        self.draw_button(self.start_button, "Start Server", 
                        GREEN if not self.server_manager.running else GRAY,
                        self.start_button.collidepoint(mouse_pos))
        self.draw_button(self.stop_button, "Stop Server", 
                        RED if self.server_manager.running else GRAY,
                        self.stop_button.collidepoint(mouse_pos))
        self.draw_button(self.restart_button, "Restart", BLUE,
                        self.restart_button.collidepoint(mouse_pos))
        self.draw_button(self.test_button, "Run Tests", 
                        BLUE if not self.test_runner.running else GRAY,
                        self.test_button.collidepoint(mouse_pos))
        
        self.draw_button(self.open_browser_button, "Open in Browser", BLUE,
                        self.open_browser_button.collidepoint(mouse_pos))
        self.draw_button(self.clear_logs_button, "Clear Logs", GRAY,
                        self.clear_logs_button.collidepoint(mouse_pos))
        
        # Draw status
        self.draw_status()
        
        # Draw logs
        self.draw_logs()
        
        # Port info
        port_text = self.font.render(f"Port: {self.server_manager.port}", True, BLACK)
        self.screen.blit(port_text, (WINDOW_WIDTH - 200, 60))
        
    def run(self):
        """Main GUI loop"""
        self.server_manager.log("Server Manager Started", "SUCCESS")
        
        while self.running:
            time_delta = self.clock.tick(FPS) / 1000.0
            
            self.handle_events()
            self.update_logs()
            self.ui_manager.update(time_delta)
            
            self.draw()
            self.ui_manager.draw_ui(self.screen)
            
            pygame.display.flip()
            
        # Cleanup
        self.server_manager.stop()
        pygame.quit()
        sys.exit()

def install_dependencies():
    """Install required dependencies"""
    dependencies = ['pygame', 'pygame-gui', 'selenium']
    
    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))
        except ImportError:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])

if __name__ == "__main__":
    # Install dependencies if needed
    install_dependencies()
    
    # Create and run GUI
    gui = ServerManagerGUI()
    gui.run()