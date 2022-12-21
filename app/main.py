from typing import Optional
from fastapi import FastAPI,Response,status,HTTPException,Depends
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import time
import psycopg2
from . import models
from . database import engine,get_db
from sqlalchemy.orm import Session
from psycopg2.extras import RealDictCursor

models.Base.metadata.create_all(bind=engine)
app = FastAPI()


class Post(BaseModel):
    title:str
    content:str
    published:bool=True
while True:    
    try:
        conn=psycopg2.connect(host='localhost',database='ojiamboloc',user='postgres',password='Ojiamboloc@4',cursor_factory=RealDictCursor)
        cursor=conn.cursor()
        print("Database Connection was succesfull")
        break
    except Exception as error:
        print("Connection  to database failed")
        print("Error:", error)  
        time.sleep(4)  
#my_posts=[{"title":"title of part 1","content":"content of post 1","id":1},{"title":"title of part 2","content":"I like pizza","id":2}]
@app.get("/")
def root():
    return {"Hello": "World"}
    #0-5:00:00
@app.get("/sqlalchemy")
def test_posts(db:Session=Depends(get_db)):
    post=db.query(models.Post).all()
    return{"post":post}

@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts=cursor.fetchall()
    #print(posts)
    return {"data": posts}
@app.post("/posts",status_code=status.HTTP_201_CREATED)
def create_posts(post:Post):
    cursor.execute("""INSERT INTO posts (title,content) VALUES (%s,%s) RETURNING * """,
                  (post.title,post.content))
    new_post=cursor.fetchone()
    conn.commit()
    return{"data":new_post}
@app.get("/posts/{id}")
def get_post(id:int):
    cursor.execute("""SELECT * FROM posts WHERE id=%s""",(str(id)))
    post=cursor.fetchone()
    print(post)
    #post=find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail=f"post with id:{id} was not found")
    return{"post-detail":post}    
@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int):
    cursor.execute("""DELETE FROM posts WHERE id=%s returning *""",(str(id),))  
    deleted_post=cursor.fetchone() 
    conn.commit()
    #index=find_index_post(id)
    if deleted_post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"post with id: {id} does not exist") 
    return Response(status_code=status.HTTP_204_NO_CONTENT)    
@app.put("/posts/{id}")  
def update_post(id:int,post:Post):
    cursor.execute("""UPDATE posts SET title=%s,content=%s WHERE id=%sRETURNING *""",(post.title,post.content,(str(id))))  
    updated_post=cursor.fetchone()
    conn.commit()
    if updated_post==None:
        raise HTTPException(status_code==status.HTTP_404_NOT_FOUND, detail=f"post with id:{id} does not exist")
    return {"data":updated_post}    