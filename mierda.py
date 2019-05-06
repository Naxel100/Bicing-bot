from jutge import read

def hola(x):
    print("hola "*x)

def mierda(x):
    print(x,"mierdas!")

def main():
    x, y = read(int, int)
    for i in range(y): x *= y
    print(x)
    hola(x)
    mierda(x)
main()
