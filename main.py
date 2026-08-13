from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel, Field, field_validator
from fastapi.staticfiles import StaticFiles


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


books =[
    {"id": 1, "title": "파이썬 입문", "author": "김철수", "year": 2021, "tags": [],"publisher": None},
    {"id": 2, "title": "FastAPI 실전", "author": "이영희", "year": 2023, "tags": [],"publisher": None},
    {"id": 3, "title": "파이썬 웹개발", "author": "김철수", "year": 2022, "tags": [],"publisher": None},
    {"id": 4, "title": "데이터 분석 기초", "author": "박민수", "year": 2020, "tags": [],"publisher": None},
    {"id": 5, "title": "FastAPI로 배우는 백엔드", "author": "이영희", "year": 2024, "tags": [],"publisher": None},
]


class Publisher(BaseModel):
    name: str
    city: str = "서울"

class BookCreate(BaseModel):
    title : str = Field(min_length = 1, max_length = 50)
    author : str = Field(min_length = 1, max_length = 20)
    year : int = Field(ge=1900, le=2026)
    tags: list[str] = Field(default_factory=list)
    publisher: Publisher | None = None

    @field_validator("title")
    @classmethod
    def strip_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
           raise ValueError("제목은 공백일 수 없습니다")
        return v

class BookResponse(BookCreate):
    id: int

@app.get("/")
def health():
    return {"message": "Hello!!!!!!!!!!!!!!!"}

@app.get("/health")
def health():
    return {"status": "ok"}
    
@app.get("/info") # 요청 파라미터
def info():
    return {"name": "도서 관리 API", "version": "0.1.0"}

@app.get("/books", response_model=list[BookResponse])
def list_books():
    return books

@app.get("/books/search")
def search_books(keyword: str = ""):
    if not keyword:
        return books
    return [b for b in books if keyword in b["title"]]

@app.get("/books/filter")
def filter_books(keyword: str="", sort: str=""):
    result = books
    #for book in books:
    # 리스트 컴프리헨션 - for + if > 리스트
    if keyword:
        result = [b for b in result if b["author"] == keyword]
    if sort == "year":
        result = sorted(result, key = lambda b:b["year"])
    return result

@app.get("/books/page")
def page_books(skip: int = 0, limit: int = 2):
    return books[skip: skip + limit]


@app.get("/books/{book_id}", response_model=BookResponse)
def read_book(book_id: int):
    for book in books:
        if book_id == book['id']:
            return book
        # return {"error":"not found"}
    raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")


@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate):
    for b in books:
        if b["title"] == book.title:
            raise HTTPException(status_code=409, detail="이미 등록된 제목입니다")

    new_id = max([b["id"] for b in books], default = 0) + 1
    # new_book = {'id':new_id,
    #             'title': book.title,
    #             'author': book.author,
    #             'year': book.year
    #             }
    new_book = {'id': new_id, **book.model_dump()}
    books.append(new_book)
    return new_book