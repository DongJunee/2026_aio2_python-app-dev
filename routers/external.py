from fastapi import APIRouter, HTTPException
from schemas import BookUpdate, ExternalBook, WeatherResponse, BookResponse, BookCreate, GoogleBooks
from external_api import fetch_weather, fetch_books, load_fallback_books
from database import books, save_books
import httpx

router = APIRouter(tags=["외부 연동"])

@router.get("/weather", response_model=WeatherResponse)
async def weather(latitude: float= 36.8, longitude: float=127.1):
    return await fetch_weather(latitude, longitude)

# @app.get("/books/external", response_model=list[GoogleBooks])
# async def search_external_books(keyword: str, limit:int=5):
#     return await fetch_books(keyword, limit)

@router.get("/books/external", response_model=list[ExternalBook])
async def search_external_books(keyword: str, limit: int = 5, fallback: bool = False):
    """
    Google Books에서 도서를 검색합니다.

    - **keyword**: 검색어. 한국어도 가능합니다
    - **limit**: 가져올 개수. 기본 5
    - **fallback**: true이면 외부 API 실패 시 예비 데이터를 반환합니다

    외부 서비스에 의존하므로 502, 504가 발생할 수 있습니다.
    """
    try:
        return await fetch_books(keyword, limit)
    except httpx.TimeoutException:
        if fallback:
            return load_fallback_books()
        raise HTTPException(status_code=504, detail="외부 API 응답이 지연됩니다")
    except httpx.HTTPStatusError:
        if fallback:
            return load_fallback_books()
        raise HTTPException(status_code=502, detail="외부 API가 오류를 반환했습니다")
    except httpx.RequestError:
        if fallback:
            return load_fallback_books()
        raise HTTPException(status_code=502, detail="외부 API에 연결할 수 없습니다")

@router.post("/books/from-external", response_model=BookResponse, status_code=201)
def create_from_external(book: ExternalBook):
    for b in books:
        if b["title"] == book.title:
            raise HTTPException(status_code=409, detail="이미 등록된 제목입니다")

    year = 2000
    if book.published_date[:4].isdigit():
        year = int(book.published_date[:4])

    new_id = max([b["id"] for b in books], default=0) + 1
    new_book = {
        "id": new_id,
        "title": book.title,
        "author": book.authors[0] if book.authors else "미상",
        "year": year,
        "tags": ["외부검색"],
        "publisher": None,
    }
    books.append(new_book)
    save_books()
    return new_book