from flask import Flask, request, jsonify, send_from_directory, abort, render_template_string
import os
import argparse
import socket
from termcolor import colored
from colorama import Fore, Style, init

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
    print(Fore.CYAN + Style.BRIGHT + "FlexiGate 1.0 by q3alique")
    print(Fore.CYAN + "Release Date: August 19, 2024")

# Initialize Flask app
app = Flask(__name__)

# Function to get the local non-loopback IP address
def get_non_loopback_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # This doesn't actually send data, just sets the socket's address
        s.connect(('8.8.8.8', 1))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = '127.0.0.1'
    finally:
        s.close()
    return ip_address

# Helper function to list files and directories recursively
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
            html += f'<li><a href="/download/{os.path.join(path, file_name)}">{file_name}</a></li>'
        break  # Don't recurse further, just show the current directory
    html += "</ul>"
    return html

# Main entry point
if __name__ == '__main__':
    print_logo()  # Print the logo and script information

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

    # Define the file upload route
    @app.route('/upload', methods=['POST'])
    def upload_file():
        if 'file' not in request.files:
            return jsonify({"message": "No file part"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"message": "No selected file"}), 400
        file.save(os.path.join(upload_folder, file.filename))
        return jsonify({"message": f"File {file.filename} uploaded successfully"}), 200

    # Define a route to list all files and folders recursively
    @app.route('/files', defaults={'path': ''}, methods=['GET'])
    @app.route('/files/<path:path>', methods=['GET'])
    def list_files(path):
        try:
            full_path = os.path.join(upload_folder, path)
            if not os.path.exists(full_path):
                return abort(404)

            # Check if the request is from a browser
            if "text/html" in request.headers.get('Accept', ''):
                # Render classic directory listing as HTML
                return render_template_string(render_directory_as_html(full_path, path))
            else:
                # Return recursive JSON output
                files = list_files_recursive(full_path)
                return jsonify(files), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 500

    # Define a route to download a specific file from any folder
    @app.route('/download/<path:filename>', methods=['GET'])
    def download_file(filename):
        try:
            return send_from_directory(upload_folder, filename, as_attachment=True)
        except FileNotFoundError:
            return jsonify({"message": "File not found"}), 404


    @app.route('/robotx.txt', methods=['GET'])
    def robots():
        return "User-agent: *\nDisallow: /"

    # Get the non-loopback IP address
    ip_address = get_non_loopback_ip()

    # Show the commands for sending files with colors
    print(colored(f"\nServer is listening on http://{ip_address}:{args.port}\n", 'green', attrs=['bold']))
    print(colored("Use the following commands to send and download files:\n", 'cyan', attrs=['bold']))

    # PowerShell command for upload
    print(colored("### PowerShell Command to Upload:", 'yellow', attrs=['bold']))
    print(colored(f'$filePath = "C:\\path\\file.txt"; $serverUrl = "http://{ip_address}:{args.port}/upload"; $boundary = [System.Guid]::NewGuid().ToString(); $LF = "`r`n"; $headers = @{{"Content-Type" = "multipart/form-data; boundary=$boundary"}}; $fileBytes = [System.IO.File]::ReadAllBytes($filePath); $fileContent = [System.Text.Encoding]::GetEncoding("iso-8859-1").GetString($fileBytes); $body = "--$boundary$LF" + "Content-Disposition: form-data; name=`"file`"; filename=`"$([System.IO.Path]::GetFileName($filePath))`"$LF" + "Content-Type: application/octet-stream$LF$LF" + $fileContent + "$LF--$boundary--$LF"; Invoke-RestMethod -Uri $serverUrl -Method Post -Headers $headers -Body ([System.Text.Encoding]::GetEncoding("iso-8859-1").GetBytes($body)) | Write-Output\n', 'white'))

    # Linux command for upload (using curl)
    print(colored("### Linux Command to Upload:", 'yellow', attrs=['bold']))
    print(colored(f'curl -F "file=@/path/to/file.txt" http://{ip_address}:{args.port}/upload\n', 'white'))

    # Command to list files
    print(colored("### Command to List Files:", 'yellow', attrs=['bold']))
    print(colored(f'curl http://{ip_address}:{args.port}/files\n', 'white'))

    # Command to download a specific file
    print(colored("### Command to Download a File:", 'yellow', attrs=['bold']))
    print(colored(f'curl http://{ip_address}:{args.port}/download/<file_to_download> -o <file_to_store>\n', 'white'))

    # Run the Flask app with the specified port
    app.run(host='0.0.0.0', port=args.port)
