import os
from dotenv import load_dotenv

load_dotenv()

var = os.getenv("CLIENT_NAME")
print(var)
