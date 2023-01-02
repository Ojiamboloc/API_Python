from typing import Optional,List
from fastapi import FastAPI,Response,status,HTTPException,Depends
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import time
import psycopg2
from . import models,schemas
from . database import engine,get_db
from sqlalchemy.orm import Session
from psycopg2.extras import RealDictCursor

models.Base.metadata.create_all(bind=engine)
app = FastAPI()



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
#@app.get("/sqlalchemy")
#def test_posts(db:Session=Depends(get_db)):
   # posts=db.query(models.Post).all()
    
    #return posts

@app.get("/posts",response_model=List[schemas.Post])
def get_posts(db:Session=Depends(get_db)):
   # cursor.execute("""SELECT * FROM posts""")
   # posts=cursor.fetchall()
    #print(posts)
    
    posts=db.query(models.Post).all()
    return  posts
@app.post("/posts",status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def create_posts(post:schemas.PostCreate,db:Session=Depends(get_db)):
    #cursor.execute("""INSERT INTO posts (title,content) VALUES (%s,%s) RETURNING * """,
                  #(post.title,post.content))
    #new_post=cursor.fetchone()
    #conn.commit()
    
    new_post=models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.get("/posts/{id}",response_model=schemas.Post)
def get_post(id:int,db:Session=Depends(get_db)):
    #cursor.execute("""SELECT * FROM posts WHERE id=%s""",(str(id)))
   # post=cursor.fetchone()
   # print(post)
    #post=find_post(id)
    post=db.query(models.Post).filter(models.Post.id==id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail=f"post with id:{id} was not found")
    return post

@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int,db:Session=Depends(get_db)):
    #cursor.execute("""DELETE FROM posts WHERE id=%s returning *""",(str(id),))  
    #deleted_post=cursor.fetchone() 
    #conn.commit()
    #index=find_index_post(id)
    post=db.query(models.Post).filter(models.Post.id==id)
    if post.first()==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"post with id: {id} does not exist") 
    post.delete(synchronize_session=False)  
    db.commit()  
    return Response(status_code=status.HTTP_204_NO_CONTENT)  
  
@app.put("/posts/{id}",status_code=status.HTTP_404_NOT_FOUND,response_model=schemas.Post)  
def update_post(id:int,updated_post:schemas.PostCreate,db:Session=Depends(get_db)):
    #cursor.execute("""UPDATE posts SET title=%s,content=%s WHERE id=%sRETURNING *""",(post.title,post.content,(str(id))))  
    #updated_post=cursor.fetchone()
    #conn.commit()
    post_query=db.query(models.Post).filter(models.Post.id==id)
    post=post_query.first()
    if post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id:{id} does not exist")
    post_query.update(updated_post.dict(),synchronize_session=False)
    db.commit()
    return post_query.first()   