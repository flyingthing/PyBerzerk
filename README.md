**PyBerzerk**
===================
Clone of the 1980s **Berzerk** arcade game. Written by TerryO as a  **Python** development exercise using **Pygame**. To date, tested on Windows and Ubuntu platforms.

**SCREENSHOTS:**
<table>
 <tr>
  <td><img src="./Screenshots/Gameplay3.png" alt="GamePlay3" /></td>
  <td><img src="./Screenshots/Gameplay2.png" alt="GamePlay2" /></td>
 </tr>
 <tr>
  <td><img src="./Screenshots/GamePlayDemo.gif" alt="GamePlayDemo" /></td>
  <td><img src="./Screenshots/HighScore.png" alt="HighScore" /></td>
 </tr>
</table>

----------

**REQUIREMENTS:**
Before running the game, make sure you have [Python v2.7](http://www.python.org/download/) installed. You will also need to install [Pygame v1.9.1](http://www.pygame.org/download.shtml), as the game will not run without it.

From the command line: python pyberzerk.py

> **NOTE:** This game has not been tested on Python 3.x


**GAME PLAY:**
Use the **ARROW** key(s) to navigate the player through a maze filled with robots who have an extreme dislike for humanoids.  Hold the **SPACEBAR** and press **ARROW** key(s) to fire player's laser weapon. The player can be killed by being blasted by a robot, running into a robot, exploding robot shrapnel, coming into contact with the electrified maze walls or being touched by Evil Otto(bouncing smiley face).

<table>
 <tr>
  <th align="left">Game Controls</th>
  <th align="left">Player/Laser</th>
 </tr>
 <tr>
  <td><kbd>&larr;</kbd> LEFT ARROW</td>
  <td>Move the player left</td>
 </tr>
  <tr>
  <td><kbd>&rarr;</kbd> RIGHT ARROW</td>
  <td>Move the player right</td>
 </tr>
  <tr>
  <td><kbd>&uarr;</kbd> UP ARROW</td>
  <td>Move the player up</td>
 </tr>
  <tr>
  <td><kbd>&darr;</kbd> DOWN ARROW</td>
  <td>Move the player down</td>
 </tr>
  <tr>
  <td><kbd>SPACEBAR</kbd></td>
  <td>Fire laser in direction of ARROW key(s)</td>
 </tr>
</table>

> **Helpful Hints:**
> 
> - Robots can destroy themselves by running into walls or each other, shooting each other, or colliding with Evil Otto.
> - Robot lasers cannot penetrate the maze walls, use this to your advantage.
> - Evil Otto is impervious to lasers, robots or the electrified maze walls.
> - If player nears an electrified maze wall that section of the wall changes color.
> - Each robot destroyed is worth 50 points,  bonus points are earned by destroying all robots. A new life is awarded at 5,000 points.

**Have fun!**
Critiques regarding game play, bugs, glitches are most welcome.

-----------------------------------------------------------------------------
**TODO:**
 
1. Make standalone executable.
1. Add joystick control.
1. Add sound/voice.
1. Necktie(bullet goes thru player body and head)
1. Custom font(ttf)

#### References
1. https://en.wikipedia.org/wiki/Berzerk_(video_game)
1. http://www.robotron2084guidebook.com/home/games/berzerk/
