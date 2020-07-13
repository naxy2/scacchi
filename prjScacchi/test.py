import threading


def conta(n):
    for i in range(100):
        print(n)

a = threading.Thread(target=conta("a"))
b = threading.Thread(target=conta("b"))

a.start()
b.start()

print("fine")