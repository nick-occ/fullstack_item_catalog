"""
@author: Nicholas Occhipinti
@summary: Add catalog item to sports store catalog db
"""

#modules
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, CategoryItem, User

#create db file
engine = create_engine('sqlite:///catalogwithusers.db')

Base.metadata.bind = engine

#create session
DBSession = sessionmaker(bind=engine)
session = DBSession()

#create user object
User1 = User(name="Nicholas Occhipinti",
             email="nicholasocchipinti@gmail.com",
             picture="https://media.licdn.com/mpr/mpr/shrinknp_200_200/AAEAAQAAAAAAAAR2AAAAJDgyY2Y1YWQxLWJhZTktNDg4OS1hNzU1LWUwOGE1NmVkOTFhYg.jpg")
session.add(User1)

#create category objects
category1 = Category(user_id=1,
                     name = "Soccer")
session.add(category1)
session.commit()

category2 = Category(user_id=1,
                     name = "Basketball")
session.add(category2)
session.commit()

category3 = Category(user_id=1,
                     name = "Baseball")
session.add(category3)
session.commit()

category4 = Category(user_id=1,
                     name = "Frisbee")
session.add(category4)
session.commit()

category5 = Category(user_id=1,
                     name = "Snowboarding")
session.add(category5)
session.commit()

category6 = Category(user_id=1,
                     name = "Rock Climbing")
session.add(category6)
session.commit()

category7 = Category(user_id=1,
                     name = "Foosball")
session.add(category7)
session.commit()

category8 = Category(user_id=1,
                     name = "Skating")
session.add(category8)
session.commit()

category9 = Category(user_id=1,
                     name = "Hockey")
session.add(category9)
session.commit()

#create category item objects
categoryItem1 = CategoryItem(user_id=1,name="Stick",
                             description="This is a hockey stick.",
                             category=category9)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(user_id=1,name="Goggles",
                             description="This is a pair of goggles.",
                             category=category5)

session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(user_id=1,name="Snowboard",
                             description="This is a snowboard.",
                             category=category5)

session.add(categoryItem3)
session.commit()

categoryItem4 = CategoryItem(user_id=1,name="Two Shinguards",
                             description="This is a pair of shinguards.",
                             category=category1)

session.add(categoryItem4)
session.commit()

categoryItem5 = CategoryItem(user_id=1,name="Shinguards",
                             description="This is a pair of shinguards.",
                             category=category1)

session.add(categoryItem5)
session.commit()

categoryItem6 = CategoryItem(user_id=1,name="Frisbee",
                             description="This is a frisbee.",
                             category=category4)

session.add(categoryItem6)
session.commit()

categoryItem7 = CategoryItem(user_id=1,name="Bat",
                             description="This is a bat.",
                             category=category3)

session.add(categoryItem7)
session.commit()

categoryItem8 = CategoryItem(user_id=1,name="Jersey",
                             description="This is a jersey.",
                             category=category1)

session.add(categoryItem8)
session.commit()

categoryItem9 = CategoryItem(user_id=1,name="Soccer Cleats",
                             description="This is a pair of soccer cleats.",
                             category=category1)

session.add(categoryItem9)
session.commit()

print ("added catalog items!")
