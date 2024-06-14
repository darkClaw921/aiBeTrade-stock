from sqlalchemy import (create_engine, Column, 
                        Integer, Float, String,
                        DateTime, JSON, ARRAY, 
                        BigInteger, func, text, 
                        BOOLEAN, URL, ForeignKey, cast)
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship, declarative_base
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from pprint import pprint


load_dotenv()
userName = os.environ.get('POSTGRES_USER')
password = os.environ.get('POSTGRES_PASSWORD')
db = os.environ.get('POSTGRES_DB')
url = os.environ.get('POSTGRES_URL')

# print(f'{userName=}')
# print(f'{password=}')
# print(f'{db=}')

# Создаем подключение к базе данных
engine = create_engine(f'postgresql://{userName}:{password}@{url}:5432/{db}')
# engine = create_engine('mysql://username:password@localhost/games')




 
# Определяем базу данных
Base = declarative_base()



class User(Base):
    __tablename__ = 'User'
    
    id = Column(BigInteger, primary_key=True)
    created_date = Column(DateTime)
    nickname = Column(String)

    all_token=Column(Float)
    all_token_price=Column(Float)
    payload=Column(String)
    groups = Column(ARRAY(BigInteger), default=[])
    # firs_message=Column(BOOLEAN, default=False)
    # isAdmin=Column(BOOLEAN, default=False)
    # groupsAdmin=relationship('Group', back_populates='admins')
    def add_group(self, groupID:int):
        if groupID not in self.groups:
            self.groups.append(groupID)
            


class Group(Base):
    __tablename__ = 'Group'
    id = Column(BigInteger, primary_key=True) 
    name=Column(String)
    telegram_group_link = Column(String, nullable=False)
    create_date = Column(DateTime)
    admins = Column(ARRAY(BigInteger), default=[])
    active=Column(BOOLEAN, default=True)
    
    def __init__(self, id, name ,create_date):
        self.id = id
        self.name = name
        self.telegram_group_link = f"https://t.me/{id}"
        self.create_date = datetime.now()
    
    def add_admin(self, adminID:int):
        if adminID not in self.admins:
            self.admins.append(adminID) 

class Message(Base):
    __tablename__ = 'Message'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_date = Column(DateTime)
    group_id = Column(BigInteger, ForeignKey('Group.id'))
    user_id = Column(BigInteger, ForeignKey('User.id'))    
    message_id = Column(BigInteger)
    payload = Column(String)
    type_chat = Column(String)
    text = Column(String)

class Task(Base):
    __tablename__ = 'Task'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_date = Column(DateTime)
    first_message=Column(String)
    promt_message=Column(String)
    groups=Column(ARRAY(BigInteger))
    payload = Column(String)
    type_chat = Column(String)
    status = Column(String)
    

class Calls(Base):
    __tablename__ = 'Calls'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_date = Column(DateTime)
    group_id = Column(BigInteger, ForeignKey('Group.id'))
    user_id = Column(BigInteger, ForeignKey('User.id'))

    payload = Column(String)
    type_chat = Column(String)
    text = Column(String)
    status = Column(String)
    is_dialog=Column(BOOLEAN)
    is_first_message=Column(BOOLEAN)

class CallMessage(Base):
    __tablename__ = 'CallMessage'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_date = Column(DateTime)
    group_id = Column(BigInteger, ForeignKey('Group.id'))
    user_id = Column(BigInteger, ForeignKey('User.id'))
    # first_message=Column(String)

    message_id = Column(BigInteger)
    payload = Column(String)
    type_chat = Column(String)
    text = Column(String)
    status = Column(String)
    

Base.metadata.create_all(engine)
# Base.metadata.update_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
# session


def add_new_user(userID:int, nickname:str, gropupID:int):
    with Session() as session:
        newUser=User(
            created_date=datetime.now(),
            id=userID,
            nickname=nickname,
            all_token=0,
            all_token_price=0,         
        )
        
        session.add(newUser)
        session.commit()

        add_group(userID, gropupID)

def add_group(userID:int, groupID:int):
    with Session() as session:
        user=session.query(User).filter(User.id==userID).one()
        pprint(user.__dict__)
        
        groups=user.groups
        if groupID not in groups:
            groups.append(groupID)
        

        _update_group_for_user(userID, groups)

def add_admin(groupID:int, adminID:int):
    with Session() as session:
        group=session.query(Group).filter(Group.id==groupID).one()
        admins=group.admins
        if adminID not in admins:
            admins.append(adminID)
        _update_admin_for_group(groupID, admins)

def add_new_group(groupID:int, name:str,):
    with Session() as session:
        newGroup=Group(
            create_date=datetime.now(),
            id=groupID,
            name=name,
            # telegram_group_link=telegram_group_link,
        )
        session.add(newGroup)
        session.commit()

def add_new_message(messageID:int, chatID:int, userID:int, text:str, type_chat:str,payload:str):
    with Session() as session:
        newMessage=Message(
            message_id=messageID,
            created_date=datetime.now(),
            group_id=chatID,
            user_id=userID,
            text=text,
            type_chat=type_chat,
            payload=payload
        )
        session.add(newMessage)
        session.commit()

def add_new_task(first_message:str, promt_message:str, groups:list[int]):
    with Session() as session:
        newTask=Task(
            created_date=datetime.now(),
            first_message=first_message,
            promt_message=promt_message,
            groups=groups,
            status='new'
        )
        session.add(newTask)
        session.commit()

def add_call(groupID:int=None, userID:int=None, text:str='', is_dialog:bool=False, is_first_message:bool=False, status:str='new'):
    with Session() as session:
        newCall=Calls(
            created_date=datetime.now(),
            group_id=groupID,
            user_id=userID,
            text=text,
            is_dialog=is_dialog,
            is_first_message=is_first_message,
            status=status
        )
        session.add(newCall)
        session.commit()

def add_call_message(groupID:int, userID:int, messageID:int, text:str, status:str='new'):
    with Session() as session:
        newCallMessage=CallMessage(
            created_date=datetime.now(),
            group_id=groupID,
            user_id=userID,
            message_id=messageID,
            text=text,
            status=status
        )
        session.add(newCallMessage)
        session.commit()




def update_payload(userID:int, payload:str):
    with Session() as session:
        session.query(User).filter(User.id==userID)\
            .update({User.payload:payload}) 
        session.commit()

def update_token_for_user(userID:int, token:float):
    with Session() as session:
        user=session.query(User).filter(User.id==userID).one()
        user.all_token+=token
        session.commit()

def update_token_price_for_user(userID:int, tokenPrice:float):
    with Session() as session:
        user=session.query(User).filter(User.id==userID).one()
        user.all_token_price+=tokenPrice
        session.commit()

def update_post(postID:int, theme:str, location:list[str], targets:list[str], location_str:str=None):
    # location_str=','.join(location)
    
    # print(f'{location_str=}')
    with Session() as session:
        session.query(Post).filter(Post.id==postID)\
            .update({Post.theme:theme, Post.location_str:location_str,
                     Post.targets:targets}) 
        session.commit()

def _update_group_for_user(userID:int, groups:list[int]):
    with Session() as session:
        user=session.query(User).filter(User.id==userID).one()
        user.groups=groups
        # session.add(user)
        # user.groups.append(groupID)
        session.commit()

def _update_admin_for_group(groupID:int, admins:list[int]):
    with Session() as session:
        group=session.query(Group).filter(Group.id==groupID).one()
        group.admins=admins
        session.commit()

def update_status_task(taskID:str, status:str):
    with Session() as session:
        session.query(Task).filter(Task.id==taskID)\
            .update({Task.status:status}) 
        session.commit()

def update_status_call(callID:str, status:str):
    with Session() as session:
        session.query(Calls).filter(Calls.id==callID)\
            .update({Calls.status:status}) 
        session.commit()

def update_call_is_first_message(callID:str, is_first_message:bool):
    with Session() as session:
        session.query(Calls).filter(Calls.id==callID)\
            .update({Calls.is_first_message:is_first_message}) 
        session.commit()
def update_call_is_dialog(callID:str, is_dialog:bool):
    with Session() as session:
        session.query(Calls).filter(Calls.id==callID)\
            .update({Calls.is_dialog:is_dialog}) 
        session.commit()




def get_user(userID:int)->User:
    with Session() as session:
        user=session.query(User).filter(User.id==userID).one()
        return user
 
def get_payload(userID:int)->str:
    with Session() as session:
        user=session.query(User).filter(User.id==userID).one()
        return user.payload

def get_targets_for_user(userID)->list[str]:
    with Session() as session:
        user=session.query(User).filter(User.id==userID).one()
        return user.targets

def get_all_active_groups_ids()->list[int]:
    with Session() as session:
        groups=session.query(Group).filter(Group.active==True).all()
        return groups

def get_top_count_targets()->list[str]:
    with Session() as session:
        """WITH data AS (
    SELECT unnest(public.post.targets) AS element
    FROM public.post
)
SELECT element, COUNT(*) AS count
FROM data
GROUP BY element
ORDER BY count DESC;"""
        # targets=session.query(Post.targets, func.count(Post.targets)).group_by(Post.targets).order_by(func.count(Post.targets).desc()).all()
        query = session.query(
            func.unnest(Post.targets).label('element'),
            func.count().label('count')
        ).from_statement(
            text("""
            WITH data AS (
            SELECT unnest(public.post.targets) AS element
            FROM public.post
            )
            SELECT element, COUNT(*) AS count
            FROM data
            GROUP BY element
            ORDER BY count DESC
            """)
        ).all()
        return query

def get_all_user_ids()->list[int]:
    ids=[]
    with Session() as session:
        users=session.query(User.id).all()
        for user in users:
            ids.append(user.id)
        return ids

def get_promt_task(taskID:str)->str:
    with Session() as session:
        task=session.query(Task).filter(Task.id==taskID).one()
        return task.promt_message

def get_first_message_task(taskID:str)->str:
    with Session() as session:
        task=session.query(Task).filter(Task.id==taskID).one()
        return task.first_message

def get_all_users_for_task(taskID:str)->list[Message]:
    with Session() as session:
        task=session.query(Task).filter(Task.id==taskID).one()
        pprint(task.__dict__)
        groups=task.groups
        users=[]
        # users=session.query(User).filter(User.groups.any(groups)).all()
        #get all users for groups in task 
        # users=session.query(User).filter(User.groups.op('&&')(cast(groups, ARRAY(BigInteger))).distinct(User.id)).all()
        users=session.query(Message).filter(Message.group_id.in_(groups)).distinct(Message.user_id).all()

        # users=session.query(User).filter(User.groups.op('&&')(cast(groups, ARRAY(BigInteger))))
        pprint(users)
        # for groupID in groups:
            
        #     print(users)
            # users.append()
        return users

def get_last_messages_for_user(userID:int, count:int=10)->list[Message]:
    with Session() as session:
        messages=session.query(Message).filter(Message.user_id==userID).order_by(Message.created_date.desc()).limit(count).all()
        return messages

def get_status_task(taskID:str)->str:
    with Session() as session:
        task=session.query(Task).filter(Task.id==taskID).one()
        return task.status

def get_status_call(callID:str)->str:
    with Session() as session:
        call=session.query(Calls).filter(Calls.id==callID).one()
        return call.status

def get_groups_for_task(taskID:str)->list[Group]:
    with Session() as session:
        task=session.query(Task).filter(Task.id==taskID).one()
        groups=task.groups
        groups=session.query(Group).filter(Group.id.in_(groups)).all()
        return groups
    
def get_all_calls_for_task(taskID:str)->list[Calls]:
    with Session() as session:
        calls=session.query(Calls).filter(Calls.group_id==taskID).all()
        return calls



def check_post(textPost:str)->bool:
    with Session() as session:
        posts=session.query(Post).filter(Post.text==textPost).all()
        if len(posts) > 0:
            return True
        else:
            return False

def check_user(userID:int)->bool:
    with Session() as session:
        users=session.query(User).filter(User.id==userID).all()
        if len(users) > 0:
            return True
        else:
            return False
def check_group(groupID:int)->bool:
    with Session() as session:
        groups=session.query(Group).filter(Group.id==groupID).all()
        if len(groups) > 0:
            return True
        else:
            return False

if __name__ == '__main__':
    # pass
    # add_new_user(1, 'test', 2)
    # # add_group(1, 6)
    # add_new_group(2, 'test')    
    # a=get_all_users_for_task(1)
    # a=get_last_messages_for_user()
    # messages=get_last_messages_for_user(7083893297)   
    # allMessages=''
    # for message in messages:
    #     allMessages+=message.text+'\n'
    # pprint(allMessages) 
    a=get_all_users_for_task(2)

    pprint(a)
    # session.commit()
    # print(user.__dict__)
# a=get_top_count_targets()
# pprint(a)
# for i in a:
#     print(f'{i[0]},')
# a=get_posts_for_targets_and_location(['танцы','бизнес'], 'убуд')
# print(a)
# posts=get_posts()
# for post in posts:
#     pprint(post.__dict__)
#     # post.location=''.join(post.location).lower()
#     # print(f'{post.location=}')
#     # for i,lock in enumerate(post.location):
#     #     print(lock)
#     #     post.location[i]=''.join(lock)
#     if post.location_str is None:
#         post.location_str='бали'
#     if post.location_str =='':
#         post.location_str='бали'

#     find=post.location_str.find('бали')
#     print(f'{find=}')
#     if find==-1:
#         post.location_str+=',бали'
        
#     print(f'{post.location_str=}')
#     # post.location_str=','.join(post.location).lower()
#     update_post(post.id, post.theme, [post.location], post.targets, location_str=post.location_str)

# a= get_posts_for_targets(['танцы','бизнес'])
# a= get_posts_for_targets(['танцы','бизнес'])
# pprint(len(a))
# a= get_posts_for_targets(['танцы'])
# pprint(len(a))
# a=get_posts()
# print(a)