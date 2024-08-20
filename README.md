# FlexiGate

## What is FlexiGate?

**FlexiGate** is a versatile file server and uploader built using Flask. It provides a simple way to upload files to a server and access them via a browser or command-line tool like `curl`. The application can serve files with a classic directory listing when accessed via a browser and provides JSON output for programmatic access.

FlexiGate is ideal for lightweight file sharing, especially during pentesting assessments where quick and flexible file transfer capabilities are essential.

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

   ```
   http://<FlexiGate-IP>:<PORT>/files
   ```

   This will display a classic directory listing.

### 3. **Downloading a File**

   **Command-line (`curl`):**

   ```bash
   curl http://<FlexiGate-IP>:<PORT>/download/folder1/file3.txt -o file3.txt
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

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

### Author

FlexiGate was created by **q3alique**. Contributions and suggestions are welcome!
