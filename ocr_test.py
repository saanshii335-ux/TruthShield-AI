import easyocr

reader = easyocr.Reader(['en'])

result = reader.readtext("uploads/test.png")

for item in result:
    print(item[1])