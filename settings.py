# DEFAULT ADMIN ACCOUNT SETTINGS
DEFAULT_NAME = "Filip Pernea"
DEFAULT_BIO = "administrator account"
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "password"
DEFAULT_ROLE = 255

# PLM SETTINGS
PART_TYPE_VALUES = ["manufactured", "purchased", "document", "level"]
ECO_STATUS_VALUES = ["pending", "released"]
ECO_CHANGE_TYPE_VALUES = ["bom_item_modify", "bom_item_create", "bom_item_delete", "part_modify", "part_create"]
ECO_CHANGE_VALUE_VALUES = ["description", "customer_revision", "customer_eco",  "unit", "manufacturer", "mpn", "bom", "quantity"]
PART_UM_VALUES = ["m", "mm", "pcs", "kg", "g", "l"]

# PLM STYLE SETTINGS
CHANGE_TYPE_STYLE = {
    "": "",
    "part_create": "Create part",
    "part_modify": "Modify part",
    "bom_item_create": "Create BOM item",
    "bom_item_modify": "Modify BOM item",
    "bom_item_delete": "Delete BOM item"
}
CHANGE_VALUE_STYLE = {
    "": "",
    "pn": "PN",
    "description": "Description",
    "internal_revision": "Internal revision",
    "internal_eco": "Internal ECO",
    "customer_revision": "Customer revision",
    "customer_eco": "Customer ECO",
    "type": "Type",
    "unit": "Unit",
    "manufacturer": "Manufacturer",
    "mpn": "MPN",
    "bom": "BOM",
    "quantity": "Quantity"
}
