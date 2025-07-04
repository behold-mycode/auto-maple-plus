<h1 align="center">
  Auto Maple
</h1>

Auto Maple Plus is an intelligent Python bot that plays MapleStory, a 2D side-scrolling MMORPG, using simulated key presses, TensorFlow machine learning, OpenCV template matching, and other computer vision techniques.

**Recent Updates**: Enhanced detection system with improved template matching, Non-Maximum Suppression (NMS) for better accuracy, and robust error handling. See [DETECTION_IMPROVEMENTS_SUMMARY.md](DETECTION_IMPROVEMENTS_SUMMARY.md) for details.

**This fork adds cross-platform support** by replacing Windows-only interception libraries with an **Arduino Leonardo-based USB HID keyboard system**, enabling the bot to work on **Windows, macOS, and Linux** with genuine hardware-level keystrokes that are completely undetectable.

Community-created resources, such as **command books** for each class and **routines** for each map, can be found in the **[resources repository](https://github.com/tanjeffreyz/auto-maple-resources)**.

<br>


<h2 align="center">
  Cross-Platform Arduino Enhancement
</h2>

<table align="center" border="0">
  <tr>
    <td width="350px">
      <p align="center">
        <img src="https://user-images.githubusercontent.com/placeholder/arduino-leonardo.png" width="300px"/>
        <br>
        <sub>
          Arduino Leonardo acts as a USB HID keyboard controller
        </sub>
      </p>
    </td>
    <td>
This version replaces the original Windows-only interception library with an <b>Arduino Leonardo-based USB HID keyboard system</b>. The Arduino receives commands from the Python bot over serial communication and sends genuine hardware keyboard events to the computer.
<br><br>
<b>Key advantages:</b>
<ul>
  <li><b>Cross-Platform:</b> Works on Windows, macOS, and Linux</li>
  <li><b>Undetectable:</b> Sends actual hardware keyboard events</li>
  <li><b>Reliable:</b> No dependency on OS-specific APIs</li>
  <li><b>Future-Proof:</b> Hardware solution unaffected by OS updates</li>
</ul>
The setup requires an Arduino Leonardo (or compatible ATmega32u4 board) and takes just a few minutes to configure. See <a href="ARDUINO_SETUP.md">ARDUINO_SETUP.md</a> for complete setup instructions.
    </td>
  </tr>
</table>

<br>


<h2 align="center">
  Minimap
</h2>

<table align="center" border="0">
  <tr>
    <td>
Auto Maple uses <b>OpenCV template matching</b> to determine the bounds of the minimap as well as the various elements within it, allowing it to accurately track the player's in-game position. If <code>record_layout</code> is set to <code>True</code>, Auto Maple will record the player's previous positions in a <b>quadtree-based</b> Layout object, which is periodically saved to a file in the "layouts" directory. Every time a new routine is loaded, its corresponding layout file, if it exists, will also be loaded. This Layout object uses the <b>A* search algorithm</b> on its stored points to calculate the shortest path from the player to any target location, which can dramatically improve the accuracy and speed at which routines are executed.
    </td>
    <td align="center" width="400px">
      <img align="center" src="https://user-images.githubusercontent.com/69165598/123177212-b16f0700-d439-11eb-8a21-8b414273f1e1.gif"/>
    </td>
  </tr>
</table>

<br>








<h2 align="center">
  Command Books
</h2>

<p align="center">
  <img src="https://user-images.githubusercontent.com/69165598/123372905-502e5d00-d539-11eb-81c2-46b8bbf929cc.gif" width="100%"/>
  <br>
  <sub>
    The above video shows Auto Maple consistently performing a mechanically advanced ability combination.
  </sub>
</p>
  
<table align="center" border="0">
  <tr>
    <td width="100%">
Designed with modularity in mind, Auto Maple can operate any character in the game as long as it is provided with a list of in-game actions, or a "command book". A command book is a Python file that contains multiple classes, one for each in-game ability, that tells the program what keys it should press and when to press them. Once a command book is imported, its classes are automatically compiled into a dictionary that Auto Maple can then use to interpret commands within routines. Commands have access to all of Auto Maple's global variables, which can allow them to actively change their behavior based on the player's position and the state of the game.
    </td>
  </tr>
</table>
  
<br>







<h2 align="center">
  Routines
</h2>

<table align="center" border="0">
  <tr>
    <td width="350px">
      <p align="center">
        <img src="https://user-images.githubusercontent.com/69165598/150469699-d8a94ab4-7d70-49c3-8736-a9018996f39a.png"/>
        <br>
        <sub>
          Click <a href="https://github.com/tanjeffreyz02/auto-maple/blob/f13d87c98e9344e0a4fa5c6f85ffb7e66860afc0/routines/dcup2.csv">here</a> to view the entire routine.
        </sub>
      </p>
    </td>
    <td>
A routine is a user-created CSV file that tells Auto Maple where to move and what commands to use at each location. A custom compiler within Auto Maple parses through the selected routine and converts it into a list of <code>Component</code> objects that can then be executed by the program. An error message is printed for every line that contains invalid parameters, and those lines are ignored during the conversion. 
<br><br>
Below is a summary of the most commonly used routine components:
<ul>
  <li>
    <b><code>Point</code></b> stores the commands directly below it and will execute them in that order once the character is within <code>move_tolerance</code> of the specified location. There are also a couple optional keyword arguments:
    <ul>
      <li>
        <code>adjust</code> fine-tunes the character's position to be within <code>adjust_tolerance</code> of the target location before executing any commands.
      </li>
      <li>
        <code>frequency</code> tells the Point how often to execute. If set to N, this Point will execute once every N iterations.
      </li>
      <li>
        <code>skip</code> tells the Point whether to run on the first iteration or not. If set to True and frequency is N, this Point will execute on the N-1th iteration.
      </li>
    </ul>
  </li>
  <li>
    <b><code>Label</code></b> acts as a reference point that can help organize the routine into sections as well as create loops.
  </li>
  <li>
    <b><code>Jump</code></b> jumps to the given label from anywhere in the routine.
  </li>
  <li>
    <b><code>Setting</code></b> updates the specified setting to the given value. It can be placed anywhere in the routine, so different parts of the same routine can have different settings. All editable settings can be found at the bottom of <a href="https://github.com/tanjeffreyz02/auto-maple/blob/v2/settings.py">settings.py</a>.
  </li>
</ul>
    </td>
  </tr>
</table>

<br>








<h2 align="center">
  Runes
</h2>

<p align="center">
  <img src="https://user-images.githubusercontent.com/69165598/123479558-f61fad00-d5b5-11eb-914c-8f002a96dd62.gif" width="100%"/>
</p>

<table align="center" border="0">
  <tr>
    <td width="100%">
Auto Maple has the ability to automatically solve "runes", or in-game arrow key puzzles. It first uses OpenCV's color filtration and <b>Canny edge detection</b> algorithms to isolate the arrow keys and reduce as much background noise as possible. Then, it runs multiple inferences on the preprocessed frames using a custom-trained <b>TensorFlow</b> model until two inferences agree. Because of this preprocessing, Auto Maple is extremely accurate at solving runes in all kinds of (often colorful and chaotic) environments.
    </td>
  </tr>
</table>


<br>









<h2 align="center">
  Video Demonstration
</h2>

<p align="center">
  <a href="https://www.youtube.com/watch?v=qs8Nw55edhg"><b>Click below to watch the full video</b></a>
</p>

<p align="center">
  <a href="https://www.youtube.com/watch?v=qs8Nw55edhg">
    <img src="https://user-images.githubusercontent.com/69165598/123308656-c5b61100-d4d8-11eb-99ac-c465665474b5.gif" width="600px"/>
  </a>
</p>

<br>



<h2 align="center">
  Setup
</h2>

<ol>
  <li>
    <b>Hardware Requirements:</b> Get an <a href="https://store.arduino.cc/products/arduino-leonardo">Arduino Leonardo</a> (or any Arduino with ATmega32u4 that supports USB HID).
  </li>
  <li>
    Download and install <a href="https://www.python.org/downloads/">Python3</a>.
  </li>
  <li>
    Download and install the <a href="https://www.arduino.cc/en/software">Arduino IDE</a>.
  </li>
  <li>
    Download and install the latest version of <a href="https://developer.nvidia.com/cuda-downloads">CUDA Toolkit</a> (optional, for ML features).
  </li>
  <li>
    Download and install <a href="https://git-scm.com/">Git</a>.
  </li>
  <li>
    Clone or download this repository:
    <pre><code>git clone https://github.com/yourusername/auto-maple-plus.git</code></pre>
  </li>
  <li>
    <b>Arduino Setup:</b> Upload the <code>arduino_keyboard_controller.ino</code> sketch to your Arduino Leonardo using the Arduino IDE.
  </li>
  <li>
    Download the <a href="https://drive.google.com/drive/folders/1SPdTNF4KZczoWyWTgfyTBRvLvy7WSGpu?usp=sharing">TensorFlow model</a> and unzip the "models" folder into the "assets" directory (optional, for rune solving).
  </li>
  <li>
    Install Python dependencies:
    <pre><code>python -m pip install -r requirements.txt</code></pre>
  </li>
  <li>
    <b>Configure Arduino Port:</b> Edit <code>src/common/settings.py</code> and set your Arduino's serial port:
    <pre><code>arduino_port = "/dev/tty.usbmodem14101"  # macOS/Linux
arduino_port = "COM3"                    # Windows</code></pre>
  </li>
  <li>
    <b>Quick Start:</b> Run the quick start script to auto-detect your Arduino:
    <pre><code>python quick_start.py</code></pre>
  </li>
</ol>