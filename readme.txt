I wrote a modular (class Connectz can be used in other context like GUI app or thought rest api, class Connectz also
accepts as a constructor argument a TextIO object so the input may be different than file (e.g. HTTP request)
solution, which return Enum for correct input or throws an exception for wrong input (I assume that for most times
the input will be correct).
In my solution between every move he status of the game is checked. There are less CPU time consuming solutions like
checking the status after all moves were done but I decided to do that because now I'm easily able to reuse this class
to watch for a rules in live game. I took also additional constraint that x, y and z have to be not less that 1.