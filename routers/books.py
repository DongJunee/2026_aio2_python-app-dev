from fastapi import APIRouter, HTTPException, status
from database import books, save_books
from schemas import BookUpdate, ExternalBook, WeatherResponse, BookResponse, BookCreate, GoogleBooks

router = APIRouter(prefix="/books",tags=["도서"])

def get_book_or_404(book_id: int) -> dict:
    for b in books:
        if b["id"] == book_id:
            return b
    raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")

#도서의 목록을 제공하는 엔드포인트
@router.get("", response_model=list[BookResponse])
def list_books():
    return books

@router.get("/search")
def search_books(keyword: str = ""):
    if not keyword:
        return books
    return [b for b in books if keyword in b["title"]]

@router.get("/page")
def page_books(skip: int=0, limit: int=2):
    return books[skip: skip+limit]


@router.get("/filter")
def filter_books(keyword: str="", sort: str = ""):
    result = books
    #for book in books:  
    # 리스트 컴프리헨션 - for + if > 리스트
    result = [b for b in result if b['author'] == keyword]
    if sort == "year":
        result = sorted(result, key= lambda b: b["year"])
    return result

@router.get("/page")
def page_books(skip: int=0, limit: int=2):
    return books[skip: skip+limit]



@router.post("", response_model=BookResponse, 
          status_code=status.HTTP_201_CREATED,
          summary="도서 등록",
          response_description="등록된 도서 정보"
          )
def create_book(book: BookCreate):
    """
    새 도서를 내 목록에 등록합니다.

    - **title**: 1자 이상 100자 이하. 앞뒤 공백은 자동 제거됩니다
    - **author**: 1자 이상 50자 이하
    - **year**: 1900 이상 2100 이하
    - **tags**: 선택. 문자열 목록
    - **publisher**: 선택. 출판사 정보

    같은 제목이 이미 있으면 409를 반환합니다.
    """
    for b in books:
        if b['title'] == book.title :
            raise HTTPException(status_code=409, detail='기존에 등록된 도서입니다.!')
        
    new_id = max([ b["id"] for b in books ], default=0) +1
    new_book =  {"id": new_id, **book.model_dump()}
    books.append( new_book )
    save_books()
    return new_book

@router.put("/{book_id}",
         response_model=BookResponse,
        summary="도서 전체 수정",
        responses={404: {"description": "해당 번호의 도서가 없습니다"}},)
def update_book(book_id: int, book: BookCreate):
    """도서 정보 전면 교체
    일부 수정시, PATCH 사용하세요"""

    # 원래 도서 정보 탐색
    old_book = get_book_or_404(book_id)
    new_book = {"id":book_id,**book.model_dump()}
    books[books.index(old_book)]=new_book
    save_books()
    return new_book


    # for i,b in enumerate(books):
    #     if b["id"] == book_id:
    #         books[i] = {"id":book_id, **book.model_dump()}
    #         # 성공시
    #         return books[i]
    # # 실패시
    # raise HTTPException(status_code=404, detail="도서번호를 확인하세요")


@router.patch("/{book_id}",
           response_model=BookResponse,
           summary="도서 일부 정보 수정",
           responses={404: {"description": "해당 번호의 도서가 없습니다"}},)
def patch_book(book_id: int, patch: BookUpdate):
    """도서 정보 일부 수정
        전면 수정시, PUT 사용하세요"""
    
    # 원래 도서 정보 탐색
    book = get_book_or_404(book_id)
    book.update(patch.model_dump(exclude_unset=True))
    save_books()
    return book

    # for b in books:
    #     if b["id"] == book_id:
    #         changes = patch.model_dump(exclude_unset=True)
    #         b.update(changes)
    #         # 성공시
    #         return b
    # raise HTTPException(status_code=404, detail="도서번호를 확인하세요")

@router.delete(
    "/{book_id}",
    status_code=204,
    summary="도서 삭제",
    responses={404: {"description": "해당 번호의 도서가 없습니다"}},
)
def delete_book(book_id: int):
    """
    도서를 삭제합니다. 성공 시 본문 없이 204를 반환합니다.
    """
    book = get_book_or_404(book_id)
    books.remove(book)
    save_books()

    # 항상 마지막
@router.get("/{book_id}", response_model=BookResponse,
         responses={404 : {"description" : "해당 번호의 도서를 찾을 수 없습니다."}})
def read_book(book_id: int):
    for book in books:
        if book_id == book['id'] :
            return book
    return get_book_or_404(book_id)
    # raise HTTPException(status_code=404, detail="우리책이 아니에요")