# Bicing-bot

This bot is a part of a university project included in the Bachelor in data science and engineering. The final purpose of this activity is to provide a sort of functionalities related to geometric graphs defined over Barcelona 'bicing' stations. It includes some usefull tools as to know the nearest station to your location or visualize a graph which connects all the bicing stations in a certain distance.   



## Getting started

Once you have installed and unzip the folder you must install all the packages contained in the requirements.txt. In order to install all the requirements just write in the console:

```bash
pip install -r requirements.txt
```
Then to run the bot execute the program:
```bash
python3 bot.py
```

## Functionalities

Whenever you're using the bot, you can see all functionaities using the command **/help**. They include:

### /start

Starts the bot and creates a graph of distance 1000 by default and displays a welcome message. If you wanted to change the graph's distance anytime, just use the command **/graph**

### /graph '_distance_'

Creates a graph with the given distance. If you don't specify any distance it will be automatically created with distance 1000. To deepen in how different algorithms are used to create the graph to guarantee the maximum efficiency see `Graph creation`.

### /route '_address1_' '_address2_'

Displays a map of the route from address1 to address2 navigating through the graph with a condition, the user can cycle only once. If only an address is indicated, the route will be created from your current location. If it hasn't been given, the bot will ask for it. Moreover, it will calculate the journey's time considering that the walking speed is 4 km/h and 10 km/h if cycling.

### /fastest\_route '_address1_' '_address2_'

This command does the same work that the **/route** command but with the unique difference that it allows the user to cycle more than once. This command is little slower than the previous one but it ensures the fastest route from the start point to the destination.

### /authors
It shows the authors of the project.

### /nodes

Prints the node's graph number.

### /edges

Prints the edges' graph number.

### /components

Prints the connected components' graph number.

### /nearest\_station

This command indicates the nearest station to your current location, sends an image of the route and indicates the expected time.

### /plotgraph

This command sends an image of the graph onto the map of Barcelona.

### /help

As I've told before, the **/help** command sends an message with a summary of the commands.

### /distribute '_number of bicycles_' '_number of empty docks_'

Given 'a' and 'b' parameters, this command tries to guarantee 'a' bicycles and 'b' empty docks at each bicing station by moving bikes from the stations with a excess of bikes to the ones with a lack of them.
To do the calculations, we use the network_simplex algorithm from the Pandas python library.


Furthermore, the bot handles some other situations like unknown commands.



## Graph creation

In order to maximize efficiency the graph uses two different algorithms depending on the size of the matrix.

### Algorithm 1

The first algorihtm is used for medium distances (most of them) and creates a matrix in which bicing stations are classified and then, box by box creates the edges to a bicing station st comparing the distance of the stations in the same box an four neighbour boxes to st and adding the edges between st and those stations nearer to st than the given distance.

One may tink that accessing to all the positions of the matrix when comparating may be slow but, when comparating times we realized that there was no real difference and accessing station by station was most of times slower actually.

### Algorithm 2

When distances are little, or more than a third of the graph total size, first algorithm is very slow: in the first case because of the enormous size of the matrix and in the second one because as distance grows, the first algorithm tends to behave quadratically.

In order to prevent this situation a second algorithm has been implemented O(n\*sqrt(n)). It sorts the stations by x-axis position and compares the distances to a given station st if an only if the distance in the x-axis is smaller than the given distance. The criteria to sort by x-axis instead of sorting by y-axis was the form of Barcelona. In this way the algorithm is little faster.


You can observe the efficiency of both algorithm here below:

* **Red** - *Algorithm1* - accesing all the matrix boxes
* **Green** - *Algorihtm1* - avoiding empty matrix boxes
* **Blue** - *Algorithm2* -

**Little distances:**

![efficieny2.png](efficieny2.png)

**Big distances:**

![efficieny.png](efficieny.png)

## Authors

The authors of this projects are:

* **Elías Abad Rocamora** - *elias.abad@est.fib.upc.edu*  -
* **Alex Ferrando de las Morenas** - *alex.ferrando@est.fib.upc.edu* -

With the original idea of:

* **Jordi Cortadella Fortuny** - *jordi.cortadella@upc.edu* -
* **Jordi Petit Silvestre** - *jpetit@cs.upc.edu* -
