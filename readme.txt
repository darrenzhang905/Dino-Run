DINO RUN
=================================================================================
DESCRIPTION

This game is my personal adaptation of Google Chrome's Dinosaur Game. It has additional features such as powerups and beat detection. The game is completely controlled by the player's voice. High pitch is for jumping and low pitch is for ducking. If the player wants to listen to music
while playing the game, they can upload a .wav file and the obstacles generate
based on that beat.
=================================================================================
HOW TO RUN

Paste the code into an editor and run the file as a script.
=================================================================================
SHORTCUTS

While playing the game, the player can press P to pause and unpause the game.
WHile the game is paused, the player can press Esc to go back to the main menu.
=================================================================================
INSTALLATION

These are the modules that are going to be used in my game:
-pygame
-pyaudio
-aubio (w/ numpy)

To get all these modules, make sure you have pip and type into
Command Prompt the following: 
pip install pygame
pip install pyaudio
pip install aubio (comes with numpy)

IF YOU HAVE ANY TROUBLE INSTALLING THESE MODULES, KEEP READING

For pyaudio, if an error comes up that says cannot find portaudio.h or
something like that, downgrade to Python 3.6 

For pyaudio and aubio, you may need to download Microsoft Visual Studio.
You can get it here: https://visualstudio.microsoft.com/downloads/

Get the community version and run the installer. 

Under Workloads, click on Desktop Development with C++ and 
check all the options found at this link:
https://gyazo.com/b7df766405edca64d530401fb52d9227

This is for Windows only, I'm not really sure about Macs.

