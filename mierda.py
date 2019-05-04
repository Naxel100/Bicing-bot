from jutge import read

def main():
    x, y = read(int, int)
    for i in range(y): x *= y
    print(x)
main()
