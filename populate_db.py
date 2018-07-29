from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Vendor, Base, Items, User

engine = create_engine('sqlite:///geekshack.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

user = User(email_id="sales@emc.com")
user.Name = "EMC"
user.hash_password("testme")

user2 = User(email_id="sales@cisco.com")
user2.Name = "CISCO"
user2.hash_password("testme")

vendor1 = Vendor(name="EMC")
vendor1.user = user

vendor2 = Vendor(name="CISCO")
vendor2.user = user2

session.add(vendor1)
session.commit()


menuItem2 = Items(name="Monitor", description="LED monitor",
                     price="7.50", stock=100, vendor=vendor1)

session.add(menuItem2)
session.commit()

menuItem2 = Items(name="Monitor1", description="LED monitor  aksndnlkasdk kas",
                     price="71.50", stock=100, vendor=vendor2)

session.add(menuItem2)
session.commit()
print("added menu items!")
