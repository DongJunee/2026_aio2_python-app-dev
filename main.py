from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database import books, save_books
from routers import system
from routers import books
from routers import external


tags_metadata = [
    {"name": "도서", "description": "도서 등록, 조회, 검색"},
    {"name": "외부 연동", "description": "Google Books와 날씨 API 연동"},
    {"name": "시스템", "description": "서버 상태 확인"},
]

app = FastAPI(
    title="도서 관리 API",
    description="도서를 등록·조회하고 외부 검색으로 정보를 가져오는 API",
    version="1.0.0",
    contact={"name": "동준", "email": "dong@example.com"},
    openapi_tags=tags_metadata
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(system.router)
app.include_router(books.router)
app.include_router(external.router)







# def get_book_or_404(book_id: int) -> dict:
#     for b in books:
#         if b["id"] == book_id:
#             return b
#     raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")


# @app.get("/", tags=["시스템"])
# def read_root():
#     return {"message": "Hello World!!!"}

# @app.get("/health", tags=["시스템"])
# def health():
#     return {"status" : "ok"}

# @app.get("/info", tags=["시스템"])
# def info():
#     return {"name": "도서관리API", "version":"0.1.0"}


# #도서의 목록을 제공하는 엔드포인트
# @app.get("/books", response_model=list[BookResponse], tags=["도서"])
# def list_books():
#     return books

# @app.get("/books/search", tags=["도서"])
# def search_books(keyword: str = ""):
#     if not keyword:
#         return books
#     return [b for b in books if keyword in b["title"]]

# @app.get("/books/filter", tags=["도서"])
# def filter_books(keyword: str="", sort: str = ""):
#     result = books
#     #for book in books:  
#     # 리스트 컴프리헨션 - for + if > 리스트
#     result = [b for b in result if b['author'] == keyword]
#     if sort == "year":
#         result = sorted(result, key= lambda b: b["year"])
#     return result

# @app.get("/books/page", tags=["도서"])
# def page_books(skip: int=0, limit: int=2):
#     return books[skip: skip+limit]

  
# @app.post("/books", response_model=BookResponse, 
#           status_code=status.HTTP_201_CREATED,
#           tags=["도서"],
#           summary="도서 등록",
#           response_description="등록된 도서 정보"
#           )
# def create_book(book: BookCreate):
#     """
#     새 도서를 내 목록에 등록합니다.

#     - **title**: 1자 이상 100자 이하. 앞뒤 공백은 자동 제거됩니다
#     - **author**: 1자 이상 50자 이하
#     - **year**: 1900 이상 2100 이하
#     - **tags**: 선택. 문자열 목록
#     - **publisher**: 선택. 출판사 정보

#     같은 제목이 이미 있으면 409를 반환합니다.
#     """
#     for b in books:
#         if b['title'] == book.title :
#             raise HTTPException(status_code=409, detail='기존에 등록된 도서입니다.!')
        
#     new_id = max([ b["id"] for b in books ], default=0) +1
#     new_book =  {"id": new_id, **book.model_dump()}
#     books.append( new_book )
#     save_books()
#     return new_book

# @app.put("/books/{book_id}",
#          response_model=BookResponse,tags=["도서"],
#         summary="도서 전체 수정",
#         responses={404: {"description": "해당 번호의 도서가 없습니다"}},)
# def update_book(book_id: int, book: BookCreate):
#     """도서 정보 전면 교체
#     일부 수정시, PATCH 사용하세요"""

#     # 원래 도서 정보 탐색
#     old_book = get_book_or_404(book_id)
#     new_book = {"id":book_id,**book.model_dump()}
#     books[books.index(old_book)]=new_book
#     save_books()
#     return new_book


#     # for i,b in enumerate(books):
#     #     if b["id"] == book_id:
#     #         books[i] = {"id":book_id, **book.model_dump()}
#     #         # 성공시
#     #         return books[i]
#     # # 실패시
#     # raise HTTPException(status_code=404, detail="도서번호를 확인하세요")


# @app.patch("/books/{book_id}",
#            response_model=BookResponse,tags=["도서"],
#            summary="도서 일부 정보 수정",
#            responses={404: {"description": "해당 번호의 도서가 없습니다"}},)
# def patch_book(book_id: int, patch: BookUpdate):
#     """도서 정보 일부 수정
#         전면 수정시, PUT 사용하세요"""
    
#     # 원래 도서 정보 탐색
#     book = get_book_or_404(book_id)
#     book.update(patch.model_dump(exclude_unset=True))
#     save_books()
#     return book

#     # for b in books:
#     #     if b["id"] == book_id:
#     #         changes = patch.model_dump(exclude_unset=True)
#     #         b.update(changes)
#     #         # 성공시
#     #         return b
#     # raise HTTPException(status_code=404, detail="도서번호를 확인하세요")

# @app.delete(
#     "/books/{book_id}",
#     status_code=204,
#     tags=["도서"],
#     summary="도서 삭제",
#     responses={404: {"description": "해당 번호의 도서가 없습니다"}},
# )
# def delete_book(book_id: int):
#     """
#     도서를 삭제합니다. 성공 시 본문 없이 204를 반환합니다.
#     """
#     book = get_book_or_404(book_id)
#     books.remove(book)
#     save_books()
#     # for i, b in enumerate(books):
#     #     if b["id"] == book_id:
#     #         books.pop(i)
#     #         return None
#     # raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")




# 테스트 시나리오 
# 1. 새로운 책 등록
# 2. 책 목록을 조회
# 3. 등록한 책을 검색


# @app.get("/weather/raw")
# async def weather_raw():
#     async with httpx.AsyncClient(timeout=5.0) as client:
#         response = await client.get(
#             "https://api.open-meteo.com/v1/forecast",
#             params={
#                 "latitude": 36.8,
#                 "longitude": 127.1,
#                 "current": "temperature_2m",
#             },
#         )
#         return response.json()


# @app.get("/weather", response_model=WeatherResponse, tags=["외부 연동"])
# async def weather(latitude: float= 36.8, longitude: float=127.1):
#     return await fetch_weather(latitude, longitude)

# # @app.get("/books/external", response_model=list[GoogleBooks])
# # async def search_external_books(keyword: str, limit:int=5):
# #     return await fetch_books(keyword, limit)

# @app.get("/books/external", response_model=list[ExternalBook], tags=["외부 연동"])
# async def search_external_books(keyword: str, limit: int = 5, fallback: bool = False):
#     """
#     Google Books에서 도서를 검색합니다.

#     - **keyword**: 검색어. 한국어도 가능합니다
#     - **limit**: 가져올 개수. 기본 5
#     - **fallback**: true이면 외부 API 실패 시 예비 데이터를 반환합니다

#     외부 서비스에 의존하므로 502, 504가 발생할 수 있습니다.
#     """
#     try:
#         return await fetch_books(keyword, limit)
#     except httpx.TimeoutException:
#         if fallback:
#             return load_fallback_books()
#         raise HTTPException(status_code=504, detail="외부 API 응답이 지연됩니다")
#     except httpx.HTTPStatusError:
#         if fallback:
#             return load_fallback_books()
#         raise HTTPException(status_code=502, detail="외부 API가 오류를 반환했습니다")
#     except httpx.RequestError:
#         if fallback:
#             return load_fallback_books()
#         raise HTTPException(status_code=502, detail="외부 API에 연결할 수 없습니다")

# @app.post("/books/from-external", response_model=BookResponse, status_code=201, tags=["외부 연동"])
# def create_from_external(book: ExternalBook):
#     for b in books:
#         if b["title"] == book.title:
#             raise HTTPException(status_code=409, detail="이미 등록된 제목입니다")

#     year = 2000
#     if book.published_date[:4].isdigit():
#         year = int(book.published_date[:4])

#     new_id = max([b["id"] for b in books], default=0) + 1
#     new_book = {
#         "id": new_id,
#         "title": book.title,
#         "author": book.authors[0] if book.authors else "미상",
#         "year": year,
#         "tags": ["외부검색"],
#         "publisher": None,
#     }
#     books.append(new_book)
#     save_books()
#     return new_book

# # 항상 마지막
# @app.get("/books/{book_id}", response_model=BookResponse, tags=["도서"],
#          responses={404 : {"description" : "해당 번호의 도서를 찾을 수 없습니다."}})
# def read_book(book_id: int):
#     for book in books:
#         if book_id == book['id'] :
#             return book
#     return get_book_or_404(book_id)
#     # raise HTTPException(status_code=404, detail="우리책이 아니에요")