import jwt

text = jwt.encode({
    "name": "KRISH",
}, "dilpejhakahamkhatehjaansegujarteh", "HS256")

print(text)

text = jwt.decode(text, "dilpejhakahamkhatehjaansegujarteh", "HS256")
print(text)
