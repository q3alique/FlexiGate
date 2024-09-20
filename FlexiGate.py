from flask import Flask, request, jsonify, send_from_directory, abort, render_template_string
import os
import argparse
import socket
import psutil
import threading
import subprocess
from termcolor import colored
from colorama import Fore, Style, init
import sys
import logging

# Initialize colorama
init(autoreset=True)

def print_logo():
    logo = """
   / \\__
  (    @\\___
  /         O
 /   (_____/
/_____/   U
"""
    print(Fore.YELLOW + Style.BRIGHT + logo)
    print(Fore.CYAN + Style.BRIGHT + "FlexiGate 1.1 by q3alique")
    print(Fore.CYAN + "Release Date: September 20, 2024")

# Initialize Flask app
app = Flask(__name__)

# Set up logging to only display HTTP requests and status codes
log = logging.getLogger('werkzeug')
log.setLevel(logging.INFO)  # Set logging to INFO level to display HTTP codes

# Flask route for file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return jsonify({"message": f"File {file.filename} uploaded successfully"}), 200

# Helper function to recursively list files and directories
def list_files_recursive(directory):
    file_tree = {}
    for root, dirs, files in os.walk(directory):
        relative_path = os.path.relpath(root, directory)
        if relative_path == ".":
            relative_path = ""
        file_tree[relative_path] = {"files": files, "subfolders": dirs}
    return file_tree

# Helper function to render a directory listing as HTML
def render_directory_as_html(directory, path=""):
    html = f"<h1>Index of /{path}</h1><ul>"
    parent_dir = os.path.dirname(path.rstrip('/'))
    if parent_dir:
        html += f'<li><a href="/files/{parent_dir}">../ (Parent Directory)</a></li>'
    
    for root, dirs, files in os.walk(directory):
        for dir_name in sorted(dirs):
            html += f'<li><a href="/files/{os.path.join(path, dir_name)}">{dir_name}/</a></li>'
        for file_name in sorted(files):
            html += f'<li><a href="/{os.path.join(path, file_name)}">{file_name}</a></li>'
        break  # Don't recurse further, just show the current directory
    html += "</ul>"
    return html

# Flask route for listing files
@app.route('/files', defaults={'path': ''})
@app.route('/files/<path:path>', methods=['GET'])
def list_files(path):
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], path)
    if not os.path.exists(full_path):
        return abort(404)

    if 'text/html' in request.headers.get('Accept', ''):
        # Return HTML if requested
        return render_template_string(render_directory_as_html(full_path, path))
    else:
        # Return JSON listing if not HTML
        files = list_files_recursive(full_path)
        return jsonify(files), 200

@app.route('/robots.txt', methods=['GET'])
def robots():
    return "User-agent: *\nDisallow: /"

# Flask route for downloading a file
@app.route('/<path:filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"message": "File not found"}), 404

# Function to get all network interfaces and their IP addresses
def get_all_ip_addresses():
    interfaces = {}
    for interface_name, interface_info in psutil.net_if_addrs().items():
        for addr in interface_info:
            if addr.family == socket.AF_INET:
                interfaces[interface_name] = addr.address
    return interfaces

# Function to prioritize tun0 if it exists or return the first non-loopback IP
def get_priority_ip(interfaces):
    if 'tun0' in interfaces:
        return interfaces['tun0']
    for interface, ip in interfaces.items():
        if ip != '127.0.0.1':
            return ip
    return '127.0.0.1'  # Fallback to localhost

# Function to show commands for sending and downloading files
def show_commands(ip_address, port, file_name=None, current_directory=None):
    if file_name:
        file_path = os.path.join(current_directory, file_name)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            # Correct file path and show download commands
            full_path = os.path.relpath(file_path, app.config['UPLOAD_FOLDER'])
            print(colored(f"\nCommands to download the file '{file_name}':\n", 'cyan', attrs=['bold']))
            print(colored("### Linux Command to Download:", 'yellow', attrs=['bold']))
            print(colored(f'curl http://{ip_address}:{port}/{full_path} -o {file_name}\n', 'white'))
            print(colored("### PowerShell Command to Download:", 'yellow', attrs=['bold']))
            print(colored(f'$fileUrl = "http://{ip_address}:{port}/{full_path}"; Invoke-WebRequest -Uri $fileUrl -OutFile "C:\\path\\{file_name}"\n', 'white'))
        else:
            print(colored(f"File '{file_name}' does not exist in the current directory.\n", 'red'))
    else:
        print(colored("\nUse the following commands to send and download files:\n", 'cyan', attrs=['bold']))
        print(colored("### PowerShell Command to Upload:", 'yellow', attrs=['bold']))
        print(colored(f'$filePath = "C:\\path\\file.txt"; $serverUrl = "http://{ip_address}:{port}/upload"; $boundary = [System.Guid]::NewGuid().ToString(); $LF = "`r`n"; $headers = @{{"Content-Type" = "multipart/form-data; boundary=$boundary"}}; $fileBytes = [System.IO.File]::ReadAllBytes($filePath); $fileContent = [System.Text.Encoding]::GetEncoding("iso-8859-1").GetString($fileBytes); $body = "--$boundary$LF" + "Content-Disposition: form-data; name=`"file`"; filename=`"$([System.IO.Path]::GetFileName($filePath))`"$LF" + "Content-Type: application/octet-stream$LF$LF" + $fileContent + "$LF--$boundary--$LF"; Invoke-RestMethod -Uri $serverUrl -Method Post -Headers $headers -Body ([System.Text.Encoding]::GetEncoding("iso-8859-1").GetBytes($body)) | Write-Output\n', 'white'))
        print(colored("### Linux Command to Upload:", 'yellow', attrs=['bold']))
        print(colored(f'curl -F "file=@/path/to/file.txt" http://{ip_address}:{port}/upload\n', 'white'))
        print(colored("### Command to List Files:", 'yellow', attrs=['bold']))
        print(colored(f'curl http://{ip_address}:{port}/files\n', 'white'))
        print(colored("### Command to Download a File:", 'yellow', attrs=['bold']))
        print(colored(f'curl http://{ip_address}:{port}/<file_to_download> -o <file_to_store>\n', 'white'))

# Function to display listening interfaces
def show_interfaces(interfaces, port):
    print(colored(f"\nServer is listening on the following interfaces:", 'green', attrs=['bold']))
    for interface, ip in interfaces.items():
        print(colored(f"Interface {interface}: http://{ip}:{port}\n", 'green', attrs=['bold']))

# Function to handle command-line interaction
def cli_thread(upload_folder, ip_address, port, interfaces):
    current_directory = upload_folder
    while True:
        try:
            user_input = input(colored(f"FlexiGate [{current_directory}]> ", 'yellow')).strip()
            if user_input.lower() == "exit":
                print(colored("Exiting CLI...", 'red'))
                break
            elif user_input.lower() == "help":
                print(colored("Available commands:", 'cyan'))
                print("ls - List files in the current directory (Unix)")
                print("dir - List files in the current directory (Windows)")
                print("tree - Show directory tree structure")
                print("cp <src> <dst> - Copy a file from <src> to <dst>")
                print("mv <src> <dst> - Move or rename a file from <src> to <dst>")
                print("rm <file> - Remove a file")
                print("cd <path> - Change directory")
                print("cd .. - Go up one directory")
                print("show - Display the upload, download, and list commands")
                print("show <file> - Show download command for the specified file")
                print("interfaces - Show the current listening interfaces")
                print("exit - Exit the CLI\n")
            elif user_input.lower().startswith("show"):
                parts = user_input.split(maxsplit=1)
                if len(parts) == 2:
                    file_name = parts[1].strip()
                    show_commands(ip_address, port, file_name, current_directory)
                else:
                    show_commands(ip_address, port)
            elif user_input.lower() == "cd ..":
                new_directory = os.path.dirname(current_directory)
                if new_directory:
                    current_directory = new_directory
                    print(colored(f"Moved up to {current_directory}", 'green'))
                else:
                    print(colored(f"Already at the root directory.", 'red'))
            elif user_input.lower().startswith("cd "):
                path = user_input[3:].strip()
                new_directory = os.path.join(current_directory, path)
                if os.path.isdir(new_directory):
                    current_directory = new_directory
                    print(colored(f"Changed directory to {current_directory}", 'green'))
                else:
                    print(colored(f"Directory {new_directory} not found.", 'red'))
            elif user_input.lower() == "interfaces":
                show_interfaces(interfaces, port)
            elif user_input.lower().startswith("cp ") or user_input.lower().startswith("mv ") or user_input.lower().startswith("rm "):
                try:
                    command_parts = user_input.split()
                    if len(command_parts) < 2:
                        print(colored("Error: Invalid command syntax", 'red'))
                    elif command_parts[0].lower() == "rm":
                        target = os.path.join(current_directory, command_parts[1])
                        if os.path.exists(target):
                            os.remove(target)
                            print(colored(f"File {command_parts[1]} removed.", 'green'))
                        else:
                            print(colored(f"File {command_parts[1]} not found.", 'red'))
                    elif len(command_parts) == 3:
                        src = os.path.join(current_directory, command_parts[1])
                        dst = os.path.join(current_directory, command_parts[2])
                        if command_parts[0].lower() == "cp":
                            if os.path.exists(src):
                                subprocess.run(f"cp {src} {dst}", shell=True)
                                print(colored(f"File copied from {command_parts[1]} to {command_parts[2]}.", 'green'))
                            else:
                                print(colored(f"Source file {command_parts[1]} not found.", 'red'))
                        elif command_parts[0].lower() == "mv":
                            if os.path.exists(src):
                                subprocess.run(f"mv {src} {dst}", shell=True)
                                print(colored(f"File moved from {command_parts[1]} to {command_parts[2]}.", 'green'))
                            else:
                                print(colored(f"Source file {command_parts[1]} not found.", 'red'))
                except Exception as e:
                    print(colored(f"Error: {str(e)}", 'red'))
            else:
                process = subprocess.Popen(user_input, cwd=current_directory, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                if stdout:
                    print(stdout.decode())
                if stderr:
                    print(stderr.decode())
        except Exception as e:
            print(colored(f"Error: {str(e)}", 'red'))

# Main entry point
if __name__ == '__main__':
    print_logo()

    # Set up argument parsing
    parser = argparse.ArgumentParser(description='FlexiGate File Upload and Serve Server')
    parser.add_argument('--port', type=int, default=80, help='Port to listen on')
    parser.add_argument('--path', type=str, default=os.getcwd(), help='Directory to store and serve files')
    args = parser.parse_args()

    # Set the upload folder to the current working directory by default or the user-provided one
    upload_folder = args.path

    # Ensure the upload folder exists
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Set the upload folder as static folder for serving files
    app.config['UPLOAD_FOLDER'] = upload_folder

    # Get all IP addresses from network interfaces
    all_interfaces = get_all_ip_addresses()
    ip_address = get_priority_ip(all_interfaces)

    # Show the commands for sending files
    print(colored(f"\nServer is listening on the following interfaces:", 'green', attrs=['bold']))
    for interface, ip in all_interfaces.items():
        print(colored(f"Interface {interface}: http://{ip}:{args.port}\n", 'green', attrs=['bold']))

    show_commands(ip_address, args.port)

    # Start Flask server in a separate thread with logs enabled for HTTP status codes
    def run_flask():
        app.run(host='0.0.0.0', port=args.port, use_reloader=False)

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # After the server is running, show the FlexiGate CLI
    print(colored("\nFlexiGate Command-Line Interface:", 'green', attrs=['bold']))
    print(colored("Type 'help' for a list of commands or 'exit' to quit the CLI.\n", 'green'))

    cli_thread(upload_folder, ip_address, args.port, all_interfaces)
