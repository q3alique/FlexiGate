# FlexiGate

## What is FlexiGate?

**FlexiGate** is a versatile file server and uploader built using Flask. It provides a simple way to upload, download, and manage files via a browser or command-line tools like `curl`. The application supports classic directory listing when accessed via a browser and provides JSON output for programmatic access.

FlexiGate is ideal for lightweight file sharing, especially during pentesting assessments where quick and flexible file transfer and file management capabilities are essential.

## Installation

### Prerequisites

- **Python 3.7+** installed on your system.
- **pip** (Python package installer).

### Installation Steps

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/flexigate.git
    cd flexigate
    ```

2. **Install required Python dependencies:**

    Run the following command to install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. **Run the application:**

    ```bash
    python flexigate.py --port 4444
    ```

    Replace `4444` with your desired port number.

## Capabilities

### 1. **File Uploading**
   - FlexiGate provides a `/upload` endpoint that allows you to upload files to the server using a `POST` request.
   - Uploaded files are stored in the directory where the script is run or a specified directory.

### 2. **File Serving**
   - FlexiGate serves files with a classic directory listing when accessed via a browser.
   - JSON output is provided when accessed via command-line tools like `curl`.
   - Supports recursive directory listing, including subfolders.

### 3. **Recursive Directory Listing**
   - FlexiGate lists all files and folders recursively, showing nested directories and their contents.

### 4. **Download Files**
   - Files can be downloaded directly from the server using either the browser or `curl`.
   - Supports downloading files from nested directories.
   - Files can now be downloaded directly by accessing their full path from the server URL.

### 5. **Command-Line Interface (CLI)**
   - FlexiGate includes an interactive CLI to manage files and directories without leaving the application. The CLI supports the following commands:
     - **ls / dir**: List files in the current directory.
     - **tree**: Display the directory structure.
     - **cp**: Copy a file from one location to another.
     - **mv**: Move or rename a file.
     - **rm**: Remove a file.
     - **cd**: Change directories.
     - **cd ..**: Navigate up one directory level.
     - **show**: Display upload, download, and file listing commands.
     - **show file**: Display download commands for a specific file. 
     - **interfaces**: Display the current listening interfaces of the server.
     - **exit**: Quit the CLI.

### 6. **Display Listening Interfaces**
   - The interfaces command allows you to display all the network interfaces the server is listening on, including both loopback and external IPs.

### 7. **HTTP Status Codes**
   - FlexiGate displays HTTP status codes (e.g., 200, 404) for each request made to the server, providing better visibility into the status of file transfers.

## Usage Examples

### 1. **Uploading a File**

   **PowerShell:**

   ```powershell
$filePath = "C:\path\to\file.txt"; $serverUrl = "http://<FlexiGate-IP>:<PORT>/upload"; $boundary = [System.Guid]::NewGuid().ToString(); $LF = "`r`n"; $headers = @{"Content-Type" = "multipart/form-data; boundary=$boundary"}; $fileBytes = [System.IO.File]::ReadAllBytes($filePath); $fileContent = [System.Text.Encoding]::GetEncoding("iso-8859-1").GetString($fileBytes); $body = "--$boundary$LF" + "Content-Disposition: form-data; name=`"file`"; filename=`"$([System.IO.Path]::GetFileName($filePath))`"$LF" + "Content-Type: application/octet-stream$LF$LF" + $fileContent + "$LF--$boundary--$LF"; Invoke-RestMethod -Uri $serverUrl -Method Post -Headers $headers -Body ([System.Text.Encoding]::GetEncoding("iso-8859-1").GetBytes($body)) | Write-Output
   ```

   **Linux (`curl`):**

   ```bash
   curl -F "file=@/path/to/file.txt" http://<FlexiGate-IP>:<PORT>/upload
   ```

### 2. **Listing Files**

   **Command-line (JSON):**

   ```bash
   curl http://<FlexiGate-IP>:<PORT>/files
   ```

   **Browser (HTML):**

   Navigate to:

   ```bash
   http://<FlexiGate-IP>:<PORT>/files
   ```

   This will display a classic directory listing.

### 3. **Downloading a File**

   **Command-line (`curl`):**

   ```bash
   curl http://<FlexiGate-IP>:<PORT>/<path-to-file>/file.txt -o file.txt
   ```

   **Browser:**

   Click on the file name in the directory listing to download it.

## Additional Information

### Customization

You can customize the server by providing additional arguments:

- **Specify a custom path for storage:**

  ```bash
  python flexigate.py --port 4444 --path /custom/directory
  ```

- **Default path:**

  By default, files are stored in the directory where the script is run.

FlexiGate was created by **q3alique**. Contributions and suggestions are welcome!
