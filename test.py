import re
sku= "DJ4891-061"
if sku.find("-") >= 1:
    if sku.count("-") > 1:
        sliced_sku = sku[:sku.rfind("-")]
        if re.search("^[A-Z0-9]{2}[0-9]{4}-[0-9]{3}$", sliced_sku):
            print("Type2:Nike")
        else:
            print("other")
    else:
        if re.search("^[A-Z0-9]{2}[0-9]{4}-[0-9]{3}$", sku):
            print("Type1:Nike")
        sliced_sku = sku[:sku.find("-")]
        if re.search("^[A-Z]{2}[0-9]{4}$", sliced_sku):
            print("Type2:Adidas")
        else:
            print("other")
elif re.search("^[A-Z]{2}[0-9]{4}$", sku):
    print("Type1:Adidas")
else:
    print("other")
