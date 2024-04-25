# Computer-Networks

# Server Side

In the `server.py` file, the `__init__` function of the `Server` class initializes the server and starts its operation. Upon initialization, two files are defined: one for registered users' information and another for logging user activities (`userlog.txt`). Registered users are read from the file, and a list is created containing information for each user, including their block status, username, password, and the number of password attempts.

In the main section, the `start()` function is executed immediately after creating the `Server` object, initiating the server to listen for incoming requests indefinitely. When a user sends a request, a new thread is created for that user's session, allowing the server to handle multiple sessions concurrently.

During a session, the user is prompted to log in, and the `auth` function handles the login process. It receives the username and password from the user and provides feedback based on the accuracy of these values. If the password is entered incorrectly multiple times, the user is temporarily blocked by the system for 10 seconds. If authentication is successful, the thread is redirected to the `handle_client` function.

The `handle_client` function listens for incoming requests from the client and responds accordingly until receiving the "OUT" request. While the user is active, incoming requests are processed by the `preprocess()` function, which acts as a router, forwarding requests to the appropriate functions and ensuring correct input handling to prevent errors.

Functions such as `BCM`, `ATU`, `SRB`, and `SRM` perform tasks based on the instructions received from the `preprocess` function.

# Client Side

The `client.py` file contains the `Main` class responsible for establishing the client-side connection to the server. Information regarding the server connection is retrieved via command-line arguments, and the `auth()` function is executed upon session initiation.

The `auth()` function communicates with the server, sending the username and password information. If the information is correct, the server responds positively, and the `auth` function terminates, calling the `loop()` function.

The `loop()` function handles user input, forwarding it to the server. Different control codes are triggered when the input is "UPD" or "OUT". The "OUT" command exits the session, while the "UPD" command initiates a protocol to send a file to the target user.

When the "UPD" command is executed, the `send_file()` function is activated to send the file in pieces.

Additionally, the `check_file()` function runs in the background thread, periodically checking for incoming files. Upon receiving a file, it imports the file in chunks and saves it locally.
