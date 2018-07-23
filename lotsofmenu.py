from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Vendor, Base, Items

engine = create_engine('sqlite:///geekshack.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Menu for UrbanBurger
vendor1 = Vendor(name="DELL")

session.add(vendor1)
session.commit()


menuItem2 = Items(name="Monitor", description="LED monitor",
                     price="$7.50", stock=100, vendor=vendor1)

session.add(menuItem2)
session.commit()


menuItem1 = Items(name="Keyboard", description="USB Keyboard",
                     price="$2.99", stock=100, vendor=vendor1)

session.add(menuItem1)
session.commit()

# Menu for UrbanBurger
vendor1 = Vendor(name="HP")

session.add(vendor1)
session.commit()


menuItem2 = Items(name="Monitor 32", description="LED monitor",
                     price="$7.50", stock=100, vendor=vendor1)

session.add(menuItem2)
session.commit()


menuItem1 = Items(name="Keyboard combo", description="USB Keyboard",
                     price="$2.99", stock=100, vendor=vendor1)

session.add(menuItem1)
session.commit()



# Menu for UrbanBurger
vendor1 = Vendor(name="Samsung")

session.add(vendor1)
session.commit()


menuItem2 = Items(name="Hard disk", description="SSD hardisk",
                     price="$77.50", stock=100, vendor=vendor1)

session.add(menuItem2)
session.commit()


menuItem1 = Items(name="Keyboard 1", description="USB Keyboard",
                     price="$22.99", stock=100, vendor=vendor1)

session.add(menuItem1)
session.commit()

# Menu for UrbanBurger
vendor1 = Vendor(name="CISCO")

session.add(vendor1)
session.commit()


menuItem2 = Items(name="Nexus 9k", description="Switch",
                     price="$137.50", stock=100, vendor=vendor1)

session.add(menuItem2)
session.commit()


menuItem1 = Items(name="LAN cable", description="2m cables",
                     price="$12.99", stock=100, vendor=vendor1)

session.add(menuItem1)
session.commit()
'''
menuItem2 = MenuItem(name="Chicken Burger", description="Juicy grilled chicken patty with tomato mayo and lettuce",
                     price="$5.50", course="Entree", restaurant=restaurant1)

session.add(menuItem2)
session.commit()

menuItem3 = MenuItem(name="Chocolate Cake", description="fresh baked and served with ice cream",
                     price="$3.99", course="Dessert", restaurant=restaurant1)

session.add(menuItem3)
session.commit()

menuItem4 = MenuItem(name="Sirloin Burger", description="Made with grade A beef",
                     price="$7.99", course="Entree", restaurant=restaurant1)

session.add(menuItem4)
session.commit()

menuItem5 = MenuItem(name="Root Beer", description="16oz of refreshing goodness",
                     price="$1.99", course="Beverage", restaurant=restaurant1)

session.add(menuItem5)
session.commit()

menuItem6 = MenuItem(name="Iced Tea", description="with Lemon",
                     price="$.99", course="Beverage", restaurant=restaurant1)

session.add(menuItem6)
session.commit()

menuItem7 = MenuItem(name="Grilled Cheese Sandwich", description="On texas toast with American Cheese",
                     price="$3.49", course="Entree", restaurant=restaurant1)

session.add(menuItem7)
session.commit()

menuItem8 = MenuItem(name="Veggie Burger", description="Made with freshest of ingredients and home grown spices",
                     price="$5.99", course="Entree", restaurant=restaurant1)

session.add(menuItem8)
session.commit()

'''

print("added menu items!")
