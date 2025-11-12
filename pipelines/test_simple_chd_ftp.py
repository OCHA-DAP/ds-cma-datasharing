from urllib.request import urlopen

public_ip = urlopen("https://api.ipify.org").read().decode()
print("Public IP:", public_ip)
