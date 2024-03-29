# f4obscontroller  
A simple application that reads Falcon BMS shared memory to manage OBS recordings.
## Features
* Automatically start & stop OBS recording when the user enters or exits 3D
* Record voice only when Push-to-Talk keys are depressed (VHF, UHF, and guard) regardless what the keys are bound to
## Prerequisites  
**[OBS Studio](https://obsproject.com/)** version 28.0.0 or higher
## Setup  
### OBS
1. [Download](https://github.com/fishbedding/f4obscontroller/releases) the zip and place the executable and settings.txt in the same directory somewhere on disk  
2. Launch OBS  
3. Navigate to **tools -> obs-websocket Settings**  
4. Check **Enable Websocket server** to enable obs-websocket  
5. Uncheck **Enable Authentication** (Unless you are running obs-websocket on an unprotected port exposed to the internet, there's no need for a password)  
6. Click **OK**
### Settings.txt
1. Configure **server.port** and set that to the same port # in the obs-websocket settings  
2. Configure **server.password** If you had set a password in step 5 from above, otherwise either delete the line or leave it commented out (preceded by ";")  
3. Configure **scene.name** This should be the Scene that you are using to record BMS.  
4. Configure **audio.capture.feed** If you want f4obscontroller to handle Push-To-Talk microphone capture in OBS, set this to the name of the audio input capture source that you configured in OBS to record microphone input. Otherwise, you can delete this line
### Running The Application
For voice recording, the .exe must be run in admin mode
## References
**[obs-websocket](https://github.com/obsproject/obs-websocket)** API reference  
  
**[simpleobsws](https://github.com/IRLToolkit/simpleobsws)** sample requests  
  
**[lightningtools](https://github.com/lightningviper/lightningstools)** BMS Shared Memory structure  