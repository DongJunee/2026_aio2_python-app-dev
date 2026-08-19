# FastAPI 입문 5일차 — CRUD 완성과 코드 정리

> [!warning] 이용 조건
> 본 교육자료는 수강생 개인의 학습 목적에 한하여 이용할 수 있으며, 외부 AI 서비스에 업로드하거나 동영상을 포함한 2차 콘텐츠로 제작·재배포하는 행위를 금지합니다. 예외적 이용은 출처 표기, 비상업적 사용, 강사의 사전 동의를 모두 충족하는 경우에 한하여 허용됩니다.

> **교육생 배포용 실습 가이드**
> 이 문서 하나만 따라 하면 5일차 실습을 처음부터 끝까지 완성할 수 있습니다.
> 수업 중 놓친 부분이 있어도 이 문서로 혼자 복습할 수 있도록 모든 결과 코드를 포함했습니다.
>
> **코드 복사 방법 (Obsidian)** — `Ctrl + E`를 눌러 **읽기 모드**로 전환한 뒤, 코드 블록 위에 마우스를 올리면 우측 상단에 복사 버튼이 나타납니다. 편집 모드에서는 보이지 않습니다.

|항목|내용|
|---|---|
|과정|FastAPI 입문 (5일 과정) — **마지막 날**|
|주제|수정·삭제로 CRUD 완성, 파일 저장, 라우터 분리, 코드 리뷰|
|예제 앱|도서 관리 API (4일차 코드에 이어서 작업)|
|선수 조건|4일차 완료 (문서화 + Postman 컬렉션)|

**4일차와 오늘의 차이**

|구분|1~4일차|5일차 (오늘)|
|---|---|---|
|가능한 동작|**읽기(Read)**, **생성(Create)**|**수정(Update)**, **삭제(Delete)** 추가 → CRUD 완성|
|데이터 수명|서버를 끄면 **사라짐**|**파일에 저장**되어 유지됨|
|파일 구성|`main.py` 400줄+|`main.py` 30줄 + `routers/` 3개|
|작업 성격|기능 추가|기능 추가 + **정리·리뷰**|

> **참고:** 오늘 실습 1~5는 기능 추가, 6~8은 정리와 리뷰입니다.
> 4일차에 만든 Postman 컬렉션이 **오늘 정리 작업의 안전망** 이 됩니다. 각 단계마다 실행해 무엇도 망가지지 않았는지 확인하세요.

---

## 0. 시작 전 체크리스트

- [ ] 가상환경이 활성화되어 프롬프트 앞에 `(.venv)`가 보인다
- [ ] `cd 01-fastapi-basic` 후 `fastapi dev main.py`가 오류 없이 실행된다
- [ ] `/docs`에 태그 그룹 4개가 보인다 (4일차 결과)
- [ ] Postman에서 `Run collection`이 전부 통과한다
- [ ] `.env`에 `GOOGLE_BOOKS_API_KEY`와 `EXTERNAL_TIMEOUT`이 있다

### 완료 후 폴더 구조

```
01-fastapi-basic/
├── main.py                앱 생성과 라우터 등록 (약 30줄)  ← 대폭 축소
├── database.py            데이터 저장소와 파일 입출력      ← 오늘 새로 만듦
├── schemas.py             Pydantic 모델                    ← BookUpdate 추가
├── external_api.py        외부 API 호출                    (변경 없음)
├── routers/                                                ← 오늘 새로 만듦
│   ├── __init__.py        빈 파일
│   ├── system.py          /, /health, /info
│   ├── books.py           /books 관련 CRUD
│   └── external.py        /weather, 외부 도서 검색
├── books_data.json        저장된 데이터 (커밋 제외)        ← 자동 생성됨
├── sample_books.json      폴백 데이터
├── .env                   API 키와 설정 (커밋 제외)
├── .gitignore
└── static/
    ├── index.html         링크 2개 추가
    ├── 01~19-*.html       1~4일차 완성분
    ├── 20-edit.html       오늘 추가
    └── 21-manage.html     오늘 추가
```

---

## 1. CRUD 완성

### 1-1. 네 가지 동작

|동작|메서드|경로|상태|
|---|---|---|---|
|**C**reate 생성|`POST`|`/books`|2일차 완료|
|**R**ead 조회|`GET`|`/books`, `/books/{id}`|1일차 완료|
|**U**pdate 수정|`PUT`, `PATCH`|`/books/{id}`|**오늘**|
|**D**elete 삭제|`DELETE`|`/books/{id}`|**오늘**|

|용어|의미|
|---|---|
|**CRUD**|Create·Read·Update·Delete. 데이터를 다루는 **네 가지 기본 동작**|

### 1-2. PUT과 PATCH의 차이

수정 메서드가 둘인 이유는 **범위** 가 다르기 때문입니다.

|메서드|범위|보내지 않은 필드|
|---|---|---|
|`PUT`|**전체 교체**|기본값으로 **덮어씀**|
|`PATCH`|**부분 수정**|**그대로 유지**|

연도만 고치고 싶은 경우를 봅니다.

```
현재: {"title": "FastAPI 입문", "author": "김철수", "year": 2023}

PUT   {"year": 2024}  →  title과 author가 사라지거나 오류
PATCH {"year": 2024}  →  {"title": "FastAPI 입문", "author": "김철수", "year": 2024}
```

> **참고:** 실무에서는 대부분 `PATCH`를 씁니다.
> 전체를 다시 보내는 것은 낭비이고, 그 사이 **다른 사람이 고친 값을 덮어쓸 위험** 이 있습니다.

### 1-3. 삭제와 204

삭제가 성공하면 **돌려줄 데이터가 없습니다.** 이때 쓰는 상태 코드가 `204 No Content`입니다.

```python
@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    ...
    return None
```

> **주의:** `204`는 **본문이 없어야 하는** 상태 코드입니다.
> 딕셔너리를 반환해도 FastAPI가 본문을 비워 보내므로, 처음부터 `None`을 반환하는 것이 맞습니다.
> `response_model`도 지정하지 않습니다.

삭제 결과를 알려주고 싶다면 `200`에 메시지를 담는 방식도 있습니다. 어느 쪽이든 **팀 안에서 통일** 하는 것이 중요합니다.

### 1-4. 멱등성

`PUT`과 `DELETE`에는 **멱등성(idempotency)** 이라는 성질이 있습니다. **같은 요청을 여러 번 보내도 결과가 같다** 는 뜻입니다.

|메서드|멱등|설명|
|---|---|---|
|`GET`|예|몇 번 조회해도 상태가 안 변함|
|`POST`|**아니오**|3번 보내면 **3개가 생성됨**|
|`PUT`|예|같은 값으로 3번 덮어써도 결과가 같음|
|`DELETE`|예|이미 지워진 것을 또 지워도 결과가 같음|

실용적인 의미가 있습니다. 네트워크 오류로 응답을 못 받았을 때, **멱등한 요청은 안심하고 재시도** 할 수 있지만 `POST`는 중복 생성 위험이 있습니다.

> **참고:** 2일차에 중복 제목을 `409`로 막은 것이 이 문제에 대한 대응이었습니다.

### 1-5. 오늘 사용할 상태 코드

|코드|상황|
|---|---|
|`200`|조회, 수정 성공|
|`201`|생성 성공|
|**`204`**|**삭제 성공. 본문 없음**|
|`404`|대상이 없음|
|`409`|중복 등 충돌|
|`422`|입력값 검증 실패|

---

## 2. 부분 수정 모델

`PATCH`를 구현하려면 **"보내지 않은 필드"** 와 **"빈 값으로 보낸 필드"** 를 구분해야 합니다.

### 2-1. 모든 필드를 선택으로

```python
class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    year: int | None = None
    tags: list[str] | None = None
```

`BookCreate`와 달리 **필수 필드가 없습니다.** 무엇을 보내든 받아들입니다.

### 2-2. `exclude_unset`

`model_dump(exclude_unset=True)`는 **실제로 보낸 필드만** 딕셔너리로 만듭니다.

```python
patch.model_dump(exclude_unset=True)
```

PATCH를 제대로 구현하려면 `exclude_unset=True`가 필수입니다.

이유는 "건드리지 마라"(`{}`)와 "값을 비워라"(`{"title": null}`)를 구분해야 하기 때문입니다. 전체 덤프(`model_dump()`)를 쓰면 두 경우가 둘 다 `title: None`으로 뭉개져서, 요청 안 한 필드까지 None으로 덮어써 버립니다.

| 요청 본문               | `model_dump(exclude_unset=True)` | `model_dump()` (전체)                             |
| ------------------- | -------------------------------- | ----------------------------------------------- |
| `{"title": "새 제목"}` | `{'title': '새 제목'}`              | `{'title': '새 제목', 'year': None, 'tags': None}` |
| `{}`                | `{}`                             | `{'title': None, 'year': None, 'tags': None}`   |
| `{"title": null}`   | `{'title': None}`                | `{'title': None, 'year': None, 'tags': None}`   |
| `{"year": 2025}`    | `{'year': 2025}`                 | `{'title': None, 'year': 2025, 'tags': None}`   |

**세 번째 줄이 핵심입니다.** `null`을 명시해서 보내면 "보냈다"로 취급됩니다.
즉 **"필드를 안 보냄"과 "null로 보냄"이 구분됩니다.** 이 구분이 있어야 값을 비우는 요청과 건드리지 않는 요청을 다르게 처리할 수 있습니다.

### 2-3. 두 방식의 결과 차이

기존 도서가 `{"id": 1, "title": "원래제목", "author": "김철수", "year": 2021, "tags": ["a"]}`일 때,
`{"year": 2025}`만 보내면 이렇게 갈립니다.

|방식|결과|
|---|---|
|`exclude_unset=True`|`{'id': 1, 'title': '원래제목', 'author': '김철수', 'year': 2025, 'tags': ['a']}`|
|`model_dump()` (전체)|`{'id': 1, **'title': None**, 'author': '김철수', 'year': 2025, **'tags': None**}`|

> **주의:** `exclude_unset` 없이 `model_dump()`만 쓰면 **보내지 않은 필드가 전부 `None`으로 나와 기존 값을 지워버립니다.**
> `PATCH`를 만들 때 가장 자주 나는 사고입니다.

---

## 3. 데이터 영속화

지금은 서버를 끄면 등록한 도서가 전부 사라집니다. `books`가 **메모리에 있는 파이썬 리스트** 이기 때문입니다.

|용어|의미|
|---|---|
|**영속화 (Persistence)**|프로그램이 꺼져도 데이터가 **남아 있게** 만드는 것|

실무에서는 데이터베이스를 쓰지만, 입문 단계에서는 **JSON 파일** 로 같은 개념을 익힙니다.

- 서버가 시작될 때 파일에서 읽어 리스트에 채운다
- 데이터가 바뀔 때마다 파일에 쓴다

### 리스트를 재대입하면 안 되는 이유

핵심 주의점이 하나 있습니다. 다른 파일에서 `from database import books`로 가져오면 **리스트 객체 자체** 를 참조합니다.
여기서 `books = [...]`처럼 **새 리스트를 대입** 하면, 가져간 쪽은 **옛날 리스트를 계속 보게 됩니다.**

```python
# 잘못된 방법. 다른 파일이 참조하는 객체가 바뀌지 않음
def load():
    global books
    books = json.load(f)


# 올바른 방법. 같은 객체의 내용만 교체
def load():
    books.clear()
    books.extend(json.load(f))
```

|방식|무슨 일이 일어나나|
|---|---|
|`books = [...]`|**새 상자** 를 만들어 이름표만 옮김. 남들은 옛 상자를 봄|
|`books.clear()` + `books.extend(...)`|**같은 상자** 의 내용물만 갈아 끼움. 모두가 새 내용을 봄|

---

## 4. 코드 구조 마무리

3일차에 `schemas.py`와 `external_api.py`를 나눴습니다. 오늘 두 개를 더 나눠 **실무 구조** 를 완성합니다.

```
01-fastapi-basic_5days/
  main.py              앱 생성, 라우터 등록
  database.py          데이터 저장소와 파일 입출력
  schemas.py           Pydantic 모델
  external_api.py      외부 API 호출
  routers/
    __init__.py
    books.py           /books 관련 엔드포인트
    system.py          /health, /info
    external.py        /weather, /books/external
```

### 4-1. APIRouter

**`APIRouter`** 는 엔드포인트를 묶어 두었다가 앱에 한꺼번에 등록하는 도구입니다.

```python
# routers/books.py
from fastapi import APIRouter

router = APIRouter(prefix="/books", tags=["도서"])


@router.get("")
def list_books():
    ...


@router.get("/{book_id}")
def read_book(book_id: int):
    ...
```

```python
# main.py
from routers import books

app.include_router(books.router)
```

|인자|효과|
|---|---|
|`prefix="/books"`|각 함수에서는 **그 뒤 경로만** 씁니다. `/books` 자체는 `""`|
|`tags=["도서"]`|**라우터 단위로 한 번에** 지정. 4일차에 엔드포인트마다 붙였던 태그가 한 줄로 줄어듦|

### 4-2. 순환 import를 피하는 방법

`routers/books.py`가 `books` 리스트를 써야 하는데, 그 리스트가 `main.py`에 있으면 문제가 생깁니다.
`main.py`가 라우터를 가져오고 라우터가 다시 `main.py`를 가져오는 **순환** 이 되기 때문입니다.

해결은 **데이터를 별도 파일로 빼는 것** 입니다.

```
main.py        →  routers/books.py  →  database.py
                                    →  schemas.py
```

모든 화살표가 **한 방향** 입니다. `database.py`는 아무것도 가져오지 않습니다.

### 4-3. 라우터 등록 순서가 경로 충돌을 결정한다

라우터를 나눠도 **리터럴 경로 우선 규칙** 은 그대로입니다. 다만 이제 규칙이 **두 층** 이 됩니다.

|층|규칙|
|---|---|
|**라우터 안**|`/search`, `/filter`, `/page`가 `/{book_id}`보다 **위**|
|**라우터 사이**|`/books/external`을 가진 라우터를 `/books/{book_id}`를 가진 라우터보다 **먼저 등록**|

실제로 확인한 결과입니다.

|`include_router` 순서|`GET /books/external` 결과|
|---|---|
|`books` → `external`|**`422`** (`external`이 `{book_id}`로 해석돼 정수 변환 실패)|
|`external` → `books`|**`200`** (정상). `/books/3`도 정상 동작|

> **주의:** 그래서 `main.py`에서 **`external.router`를 `books.router`보다 먼저** 등록합니다.
> 문서에 표시되는 그룹 순서는 등록 순서가 아니라 `tags_metadata` 순서를 따르므로, 화면은 그대로입니다.

---

## 5. 코드 리뷰 관점

마지막 실습에서 서로의 코드를 봅니다. 무엇을 보는지 기준을 미리 정합니다.

|관점|무엇을 보는가|
|---|---|
|**이름**|함수와 변수 이름만 보고 무엇을 하는지 알 수 있는가|
|**중복**|같은 코드가 세 번 이상 반복되지 않는가|
|**책임**|한 함수가 한 가지 일만 하는가|
|**오류**|실패할 수 있는 지점에 처리가 있는가|
|**상태 코드**|상황에 맞는 코드를 쓰는가|
|**비밀 값**|키나 비밀번호가 코드에 직접 적혀 있지 않은가|
|**죽은 코드**|주석 처리된 옛 버전이 남아 있지 않은가|

> **참고:** 리뷰는 **사람이 아니라 코드** 를 대상으로 합니다.
> "이건 왜 이렇게 했어?"보다 **"여기를 이렇게 바꾸면 어떨까?"** 가 낫습니다.

---

## 6. 실습

4일차 코드에 이어서 작성합니다. 실습 1~4는 **기능 추가**, 5~8은 **정리** 입니다.

---

### 실습 1. 전체 수정 (PUT)

**목표:** 도서 정보를 통째로 교체한다.

**요구사항**
- `PUT /books/{book_id}` : `BookCreate`를 받아 기존 도서를 덮어쓴다
- 없는 번호면 `404`

**결과 코드** — `main.py`에 추가합니다.

```python
@app.put(
    "/books/{book_id}",
    response_model=BookResponse,
    tags=["도서"],
    summary="도서 전체 수정",
    responses={404: {"description": "해당 번호의 도서가 없습니다"}},
)
def update_book(book_id: int, book: BookCreate):
    """
    도서 정보를 전체 교체합니다. 보내지 않은 필드는 기본값으로 바뀝니다.
    일부만 고치려면 PATCH를 사용하세요.
    """
    for i, b in enumerate(books):
        if b["id"] == book_id:
            books[i] = {"id": book_id, **book.model_dump()}
            return books[i]
    raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")
```

> **참고:** `books[i] = ...`로 **그 자리를 통째로** 바꿉니다.
> `id`는 유지해야 하므로 새 딕셔너리에 다시 넣습니다.

**확인:** `/docs`에서 `PUT /books/{book_id}`를 펼쳐 `Try it out` → `book_id`에 `1` → `Request body`를 아래로 고쳐 `Execute`.

```json
{"title": "수정된 제목", "author": "박수정", "year": 2025}
```

|확인 항목|기대 결과|
|---|---|
|`Code`|`200`|
|`Response body`|`id`는 `1` 유지, 제목·저자·연도가 바뀜|
|`tags`|**빈 배열 `[]`로 초기화됨** (보내지 않았으므로)|
|`GET /books/1` 재실행|같은 값이 나옴|
|`book_id`를 `999`로|`404` + `"도서를 찾을 수 없습니다"`|

`tags`가 사라지는 것이 `PUT`의 특성입니다. 다음 실습에서 이 차이를 확인합니다.

---

### 실습 2. 부분 수정 (PATCH)

**목표:** 보낸 필드만 바꾼다.

**요구사항**
- `BookUpdate` 모델을 만든다 (모든 필드가 선택)
- `PATCH /books/{book_id}` : 보낸 필드만 수정한다

**1) `schemas.py`에 모델을 추가합니다.**

```python
class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    author: str | None = Field(default=None, min_length=1, max_length=50)
    year: int | None = Field(default=None, ge=1900, le=2100)
    tags: list[str] | None = None
    publisher: Publisher | None = None
```

> **참고:** 제약 조건(`min_length`, `ge` 등)은 `BookCreate`와 같게 유지합니다.
> 값을 **보냈을 때만** 검사하고, 안 보내면 검사 자체를 건너뜁니다.

**2) `main.py`에 엔드포인트를 추가합니다.**

```python
@app.patch(
    "/books/{book_id}",
    response_model=BookResponse,
    tags=["도서"],
    summary="도서 부분 수정",
    responses={404: {"description": "해당 번호의 도서가 없습니다"}},
)
def patch_book(book_id: int, patch: BookUpdate):
    """
    보낸 필드만 수정합니다. 보내지 않은 필드는 그대로 유지됩니다.
    """
    for b in books:
        if b["id"] == book_id:
            changes = patch.model_dump(exclude_unset=True)
            b.update(changes)
            return b
    raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")
```

> **참고:** `b.update(changes)`는 딕셔너리에 **바뀐 항목만** 덮어씁니다.
> 리스트 안의 딕셔너리를 **직접** 고치므로 `books[i] = ...`가 필요 없습니다.

**확인:** 실습 1과 **같은 도서에 같은 본문** 을 보내 차이를 비교합니다.

1. `GET /books/2`를 실행해 현재 값을 적어 둔다.
2. `PATCH /books/{book_id}`를 펼치고 `book_id`에 `2`, 본문에 `{"year": 2025}`만 넣어 `Execute`.

|확인 항목|기대 결과|
|---|---|
|`Code`|`200`|
|`title`, `author`|**그대로 유지됨**|
|`year`|`2025`로 바뀜|
|`tags`|**그대로 유지됨**|

3. 이번엔 `PUT /books/{book_id}`에 `book_id`를 `2`, 본문을 `{"title": "x", "author": "y", "year": 2025}`로 보낸다.
4. `tags`가 **빈 배열이 되는지** 확인한다. 이것이 `PUT`과 `PATCH`의 차이다.

---

### 실습 3. 삭제 (DELETE)

**목표:** 도서를 삭제하고 `204`를 반환한다.

**요구사항**
- `DELETE /books/{book_id}` : 삭제하고 본문 없이 `204`
- 없는 번호면 `404`

**결과 코드**

```python
@app.delete(
    "/books/{book_id}",
    status_code=204,
    tags=["도서"],
    summary="도서 삭제",
    responses={404: {"description": "해당 번호의 도서가 없습니다"}},
)
def delete_book(book_id: int):
    """
    도서를 삭제합니다. 성공 시 본문 없이 204를 반환합니다.
    """
    for i, b in enumerate(books):
        if b["id"] == book_id:
            books.pop(i)
            return None
    raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")
```

> **주의:** `response_model`을 **지정하지 않습니다.** `204`는 본문이 없으므로 응답 모델도 필요 없습니다.

**확인:** `/docs`에서 `DELETE /books/{book_id}` → `book_id`에 `5` → `Execute`.

|확인 항목|기대 결과|
|---|---|
|`Code`|`204`|
|`Response body`|**비어 있음** (`no content`)|
|`GET /books` 재실행|5번 도서가 목록에서 사라짐|
|**같은 번호를 다시 삭제**|`404` + `"도서를 찾을 수 없습니다"`|

---

### 실습 4. 중복 제거

**목표:** 네 번 반복된 조회 코드를 함수 하나로 만든다.

실습 1~3에서 **같은 반복문을 세 번** 썼습니다. 기존 조회 엔드포인트까지 하면 **네 번** 입니다.

**1) 공통 함수를 만듭니다.** (`main.py`의 엔드포인트들 위)

```python
def get_book_or_404(book_id: int) -> dict:
    """번호로 도서를 찾고, 없으면 404를 발생시킨다."""
    for b in books:
        if b["id"] == book_id:
            return b
    raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")
```

**2) 각 엔드포인트가 짧아집니다.**

```python
@app.get("/books/{book_id}", response_model=BookResponse, tags=["도서"])
def read_book(book_id: int):
    return get_book_or_404(book_id)


@app.patch("/books/{book_id}", response_model=BookResponse, tags=["도서"])
def patch_book(book_id: int, patch: BookUpdate):
    book = get_book_or_404(book_id)
    book.update(patch.model_dump(exclude_unset=True))
    return book


@app.delete("/books/{book_id}", status_code=204, tags=["도서"])
def delete_book(book_id: int):
    book = get_book_or_404(book_id)
    books.remove(book)
    return None
```

`PUT`은 **자리 교체** 가 필요해 인덱스를 씁니다.

```python
@app.put("/books/{book_id}", response_model=BookResponse, tags=["도서"])
def update_book(book_id: int, book: BookCreate):
    old = get_book_or_404(book_id)
    new_book = {"id": book_id, **book.model_dump()}
    books[books.index(old)] = new_book
    return new_book
```

> **참고:** **같은 코드가 세 번 이상 반복되면 함수로 빼는 것** 이 일반적인 기준입니다. 지금이 정확히 그 경우입니다.
> 위 코드는 `summary`·`responses`를 생략해 짧게 보였습니다. 실제로는 실습 1~3에서 붙인 인자를 **그대로 두고** 본문만 바꿉니다.

**확인:** 리팩토링 후 **아무것도 망가지지 않았는지** 확인하는 것이 핵심입니다.

1. 서버가 오류 없이 재시작된다.
2. Postman에서 `Run collection`을 실행한다. **4일차에 만든 테스트가 전부 통과** 한다.
3. `/docs`에서 `GET`·`PUT`·`PATCH`·`DELETE` 네 개를 각각 실행해 `200`·`200`·`200`·`204`가 나온다.
4. 없는 번호로 네 개를 각각 실행해 **모두 `404`** 가 나온다.

4번이 중요합니다. `get_book_or_404` 하나가 네 곳의 `404`를 모두 담당하게 되었습니다.

---

### 실습 5. 파일로 저장하기

**목표:** 서버를 껐다 켜도 데이터가 유지되게 한다.

**1) `database.py`를 새로 만듭니다.**

```python
import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "books_data.json"

DEFAULT_BOOKS = [
    {"id": 1, "title": "파이썬 입문", "author": "김철수", "year": 2021, "tags": [], "publisher": None},
    {"id": 2, "title": "FastAPI 실전", "author": "이영희", "year": 2023, "tags": [], "publisher": None},
    {"id": 3, "title": "파이썬 웹개발", "author": "김철수", "year": 2022, "tags": [], "publisher": None},
    {"id": 4, "title": "데이터 분석 기초", "author": "박민수", "year": 2020, "tags": [], "publisher": None},
    {"id": 5, "title": "FastAPI로 배우는 백엔드", "author": "이영희", "year": 2024, "tags": [], "publisher": None},
]

books: list[dict] = []


def load_books() -> None:
    """파일에서 도서 목록을 읽어 books에 채운다. 파일이 없으면 기본값을 쓴다."""
    books.clear()
    if DATA_FILE.exists():
        with open(DATA_FILE, encoding="utf-8") as f:
            books.extend(json.load(f))
    else:
        books.extend(DEFAULT_BOOKS)
        save_books()


def save_books() -> None:
    """현재 books 내용을 파일에 저장한다."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)


load_books()
```

|코드|의미|
|---|---|
|`Path(__file__).parent`|**이 파일이 있는 폴더.** 실행 위치와 무관하게 경로를 잡음 (3일차와 동일)|
|`books.clear()` + `extend()`|**같은 리스트 객체** 의 내용만 교체 (3절 참고)|
|`ensure_ascii=False`|**한글을 그대로 저장.** 없으면 `서울` 형태가 되어 읽을 수 없음|
|`indent=2`|사람이 보기 좋게 줄바꿈|
|맨 아래 `load_books()`|**모듈을 import하는 순간** 파일을 읽어 들임|

**2) `main.py`에서 리스트 정의를 지우고 가져옵니다.**

```python
from database import books, save_books
```

기존의 `books = [ ... 5권 ... ]` 정의는 **삭제** 합니다.

**3) 데이터를 바꾸는 엔드포인트마다 `save_books()`를 호출합니다.**

```python
@app.post("/books", response_model=BookResponse, status_code=201, tags=["도서"])
def create_book(book: BookCreate):
    ...
    books.append(new_book)
    save_books()          # 추가
    return new_book


@app.patch("/books/{book_id}", response_model=BookResponse, tags=["도서"])
def patch_book(book_id: int, patch: BookUpdate):
    book = get_book_or_404(book_id)
    book.update(patch.model_dump(exclude_unset=True))
    save_books()          # 추가
    return book
```

| 엔드포인트                       | `save_books()` 필요 |
| --------------------------- | ----------------- |
| `POST /books`               | 필요                |
| `PUT /books/{id}`           | 필요                |
| `PATCH /books/{id}`         | 필요                |
| `DELETE /books/{id}`        | 필요                |
| `POST /books/from-external` | 필요*               |
| `GET` 계열 전부                 | **불필요**           |

**4) `.gitignore`에 데이터 파일을 추가합니다.**

```
.venv/
__pycache__/
.env
books_data.json
```

> **참고:** 각자 다른 데이터를 가지므로 공유하면 **충돌** 합니다.

**확인:**

1. 서버를 재시작한다. **`books_data.json` 파일이 자동 생성** 된다.
2. 그 파일을 열어 본다. 한글이 **깨지지 않고** 보이고, 들여쓰기가 되어 있다.
3. `POST /books`로 새 도서를 등록한다.
4. **터미널에서 `Ctrl + C`로 서버를 완전히 끈다.**
5. `fastapi dev main.py`로 다시 켠다.
6. `GET /books`를 실행한다. **3번에서 등록한 도서가 그대로 있다.**
7. `books_data.json`을 다시 열어 그 도서가 파일에도 들어 있는지 본다.

4~6번이 이 실습의 핵심입니다. 어제까지는 서버를 끄면 사라졌습니다.

---

### 실습 6. 라우터 분리

**목표:** 엔드포인트를 주제별 파일로 나눈다.

**1) `routers` 폴더를 만들고 안에 빈 `__init__.py` 파일을 만듭니다.**

> **주의:** `__init__.py`가 **있어야** 파이썬이 폴더를 패키지로 인식합니다. 내용은 비워 둡니다.

**2) `routers/system.py`**

```python
from fastapi import APIRouter

router = APIRouter(tags=["시스템"])


@router.get("/", summary="루트")
def read_root():
    return {"message": "FastAPI 첫 서버"}


@router.get("/health", summary="서버 상태 확인")
def health():
    return {"status": "ok"}


@router.get("/info", summary="앱 정보")
def info():
    return {"name": "도서 관리 API", "version": "1.0.0"}
```

**3) `routers/books.py`** — `prefix` 덕분에 경로에서 `/books`가 빠집니다.

```python
from fastapi import APIRouter, HTTPException

from database import books, save_books
from schemas import BookCreate, BookResponse, BookUpdate, ErrorDetail

router = APIRouter(prefix="/books", tags=["도서"])


def get_book_or_404(book_id: int) -> dict:
    """번호로 도서를 찾고, 없으면 404를 발생시킨다."""
    for b in books:
        if b["id"] == book_id:
            return b
    raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")


@router.get("", response_model=list[BookResponse], summary="도서 목록 조회")
def list_books():
    """내 목록에 등록된 도서를 전부 반환합니다."""
    return books


@router.post(
    "",
    response_model=BookResponse,
    status_code=201,
    summary="도서 등록",
    responses={409: {"description": "이미 등록된 제목입니다", "model": ErrorDetail}},
)
def create_book(book: BookCreate):
    """새 도서를 등록합니다. 같은 제목이 이미 있으면 409를 반환합니다."""
    for b in books:
        if b["title"] == book.title:
            raise HTTPException(status_code=409, detail="이미 등록된 제목입니다")
    new_id = max([b["id"] for b in books], default=0) + 1
    new_book = {"id": new_id, **book.model_dump()}
    books.append(new_book)
    save_books()
    return new_book


# 리터럴 경로는 /{book_id}보다 먼저 선언한다
@router.get("/search", summary="제목 검색")
def search_books(keyword: str = ""):
    """제목에 키워드가 포함된 도서를 반환합니다. 비우면 전체를 반환합니다."""
    if not keyword:
        return books
    return [b for b in books if keyword in b["title"]]


@router.get("/filter", summary="저자 필터·연도 정렬")
def filter_books(author: str = "", sort: str = ""):
    """저자로 거르고 sort가 year이면 연도 오름차순으로 정렬합니다."""
    result = books
    if author:
        result = [b for b in result if b["author"] == author]
    if sort == "year":
        result = sorted(result, key=lambda b: b["year"])
    return result


@router.get("/page", summary="페이지네이션")
def page_books(skip: int = 0, limit: int = 2):
    """skip개를 건너뛰고 limit개만 반환합니다."""
    return books[skip: skip + limit]


@router.get(
    "/{book_id}",
    response_model=BookResponse,
    summary="도서 단건 조회",
    responses={404: {"description": "해당 번호의 도서가 없습니다", "model": ErrorDetail}},
)
def read_book(book_id: int):
    """도서 번호로 한 건을 조회합니다."""
    return get_book_or_404(book_id)


@router.put(
    "/{book_id}",
    response_model=BookResponse,
    summary="도서 전체 수정",
    responses={404: {"description": "해당 번호의 도서가 없습니다", "model": ErrorDetail}},
)
def update_book(book_id: int, book: BookCreate):
    """
    도서 정보를 전체 교체합니다. 보내지 않은 필드는 기본값으로 바뀝니다.
    일부만 고치려면 PATCH를 사용하세요.
    """
    old = get_book_or_404(book_id)
    new_book = {"id": book_id, **book.model_dump()}
    books[books.index(old)] = new_book
    save_books()
    return new_book


@router.patch(
    "/{book_id}",
    response_model=BookResponse,
    summary="도서 부분 수정",
    responses={404: {"description": "해당 번호의 도서가 없습니다", "model": ErrorDetail}},
)
def patch_book(book_id: int, patch: BookUpdate):
    """보낸 필드만 수정합니다. 보내지 않은 필드는 그대로 유지됩니다."""
    book = get_book_or_404(book_id)
    book.update(patch.model_dump(exclude_unset=True))
    save_books()
    return book


@router.delete(
    "/{book_id}",
    status_code=204,
    summary="도서 삭제",
    responses={404: {"description": "해당 번호의 도서가 없습니다", "model": ErrorDetail}},
)
def delete_book(book_id: int):
    """도서를 삭제합니다. 성공 시 본문 없이 204를 반환합니다."""
    book = get_book_or_404(book_id)
    books.remove(book)
    save_books()
    return None
```

**4) `routers/external.py`** — 경로가 섞여 있으므로 `prefix` 없이 만들고 전체 경로를 적습니다.

```python
import time

import httpx
from fastapi import APIRouter, HTTPException

from database import books, save_books
from external_api import (
    fetch_books,
    fetch_books_multi,
    fetch_weather,
    load_fallback_books,
)
from schemas import BookResponse, ErrorDetail, ExternalBook, WeatherResponse

router = APIRouter(tags=["외부 연동"])


@router.get(
    "/weather",
    response_model=WeatherResponse,
    summary="현재 날씨 조회",
    responses={
        502: {"description": "외부 API 연결 실패 또는 오류 응답", "model": ErrorDetail},
        504: {"description": "외부 API 응답 지연", "model": ErrorDetail},
    },
)
async def weather(latitude: float = 36.8, longitude: float = 127.1):
    """
    좌표로 현재 날씨를 조회합니다.

    - **latitude**: 위도. 기본값은 천안(36.8)
    - **longitude**: 경도. 기본값은 천안(127.1)
    """
    try:
        return await fetch_weather(latitude, longitude)
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="외부 API 응답이 지연됩니다")
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=502, detail="외부 API가 오류를 반환했습니다")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="외부 API에 연결할 수 없습니다")


@router.get(
    "/books/external",
    response_model=list[ExternalBook],
    summary="Google Books 검색",
    responses={
        502: {"description": "외부 API 연결 실패 또는 오류 응답", "model": ErrorDetail},
        504: {"description": "외부 API 응답 지연", "model": ErrorDetail},
    },
)
async def search_external_books(keyword: str, limit: int = 5, fallback: bool = False):
    """
    Google Books에서 도서를 검색합니다.

    - **keyword**: 검색어. 한국어도 가능합니다
    - **limit**: 가져올 개수. 기본 5
    - **fallback**: true이면 외부 API 실패 시 예비 데이터를 반환합니다
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


@router.get("/books/external/multi", summary="여러 키워드 동시 검색")
async def search_multi(keywords: str = "python,fastapi,django"):
    """쉼표로 구분한 여러 키워드를 동시에 검색합니다."""
    words = [w.strip() for w in keywords.split(",") if w.strip()]

    start = time.perf_counter()
    results = await fetch_books_multi(words)
    elapsed = round(time.perf_counter() - start, 2)

    return {"elapsed_seconds": elapsed, "results": results}


@router.post(
    "/books/from-external",
    response_model=BookResponse,
    status_code=201,
    summary="외부 검색 결과 담기",
    responses={409: {"description": "이미 등록된 제목입니다", "model": ErrorDetail}},
)
def create_from_external(book: ExternalBook):
    """
    Google Books 검색 결과를 내 도서 목록에 등록합니다.

    - **authors**: 첫 번째 저자만 사용하며, 비어 있으면 "미상"이 됩니다
    - **published_date**: 앞 4자리를 연도로 사용하며, 없으면 2000이 됩니다
    """
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
```

> **참고:** `/books/from-external`은 4일차까지 `도서` 태그였지만, 이 파일로 옮기면서 `외부 연동` 그룹으로 바뀝니다.
> 외부 데이터를 받아 처리하므로 이 분류가 더 맞습니다.

**5) `main.py`가 이렇게 짧아집니다.**

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers import books, external, system

tags_metadata = [
    {"name": "시스템", "description": "서버 상태와 앱 정보 확인"},
    {"name": "도서", "description": "내 도서 목록의 등록, 조회, 수정, 삭제"},
    {"name": "외부 연동", "description": "Google Books 도서 검색과 날씨 조회"},
]

app = FastAPI(
    title="도서 관리 API",
    description="도서를 등록·조회하고, 외부 서비스에서 정보를 가져오는 API",
    version="1.0.0",
    openapi_tags=tags_metadata,
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# 등록 순서 주의: /books/external 이 /books/{book_id} 보다 먼저 등록돼야 한다
app.include_router(system.router)
app.include_router(external.router)
app.include_router(books.router)
```

**400줄이 넘던 파일이 30줄이 됐습니다.**

> **주의 — 등록 순서**
> `external.router`를 `books.router`보다 **먼저** 등록해야 합니다.
> 순서를 바꾸면 `/books/external` 호출 시 `external`이 `{book_id}` 자리로 들어가 **`422`** 가 납니다.
> (`{"type": "int_parsing", "loc": ["path", "book_id"], "input": "external"}`)
>
> 문서 그룹 순서는 등록 순서가 아니라 `tags_metadata` 순서를 따르므로 **화면은 그대로** 입니다.

**확인:**

1. 서버를 **완전히 껐다가** 다시 실행한다. (`Ctrl + C` → `fastapi dev main.py`)
2. `/docs`에서 그룹이 **3개** 이고, 엔드포인트가 **하나도 빠지지 않았는지** 본다.
3. `GET /books/external?keyword=fastapi`를 실행한다. **`200`이 나오면 등록 순서가 맞다.** `422`가 나오면 순서를 확인한다.
4. `GET /books/3`을 실행해 `200`이 나오는지 본다.
5. **Postman에서 `Run collection`을 실행한다. 전부 통과해야 한다.**

5번이 이 실습의 최종 검증입니다. 파일을 네 개로 쪼갰는데 동작이 그대로라면 리팩토링이 성공한 것입니다.

---

### 실습 7. 정리와 검증

**목표:** 5일 동안 쌓인 잔여물을 걷어낸다.

체크리스트대로 진행합니다.

- [ ] 주석 처리된 옛 버전 코드를 전부 삭제한다
- [ ] `/slow-async`, `/slow-block`, `/weather/raw` 같은 학습용 엔드포인트를 정리한다
- [ ] 파일 맨 위로 import를 모으고 중복을 없앤다
- [ ] 쓰지 않는 import를 지운다 (VS Code에서 **회색으로 표시** 됨)
- [ ] `.env`가 `.gitignore`에 있는지 확인한다
- [ ] API 키가 코드에 직접 적힌 곳이 없는지 검색한다 (`AIza`로 찾기)
- [ ] 함수 이름이 하는 일과 맞는지 확인한다

학습용 엔드포인트를 **남기고 싶다면** 지우는 대신 문서에서만 숨길 수 있습니다.

```python
@router.get("/slow-async", include_in_schema=False)
```

동작은 그대로이고 `/docs`와 `openapi.json`에서만 사라집니다.

**확인:** 정리 후 Postman 컬렉션을 다시 실행한다. **전부 통과하면 정리 과정에서 아무것도 망가뜨리지 않았다는 뜻** 이다.
4일차에 테스트를 만들어 둔 이유가 여기서 드러난다.

|정리 전후 비교 항목|확인 방법|
|---|---|
|엔드포인트 개수|`/docs`에서 세어 보기|
|전체 동작|Postman `Run collection`|
|API 키 노출|편집기에서 `AIza` 전체 검색 → 결과 없어야 함|
|불필요한 import|VS Code `문제` 패널(`Ctrl + Shift + M`)|

---

### 실습 8. 상호 코드 리뷰

**목표:** 다른 사람의 코드를 읽고 개선점을 제안한다.

2인 1조로 코드를 교환합니다. [5. 코드 리뷰 관점](#5-코드-리뷰-관점)을 기준으로 각자 **3가지 이상** 찾아 적습니다.

**리뷰 기록 양식**

```
파일: routers/books.py
줄:   45
관점: 중복
내용: 제목 중복 검사가 create_book과 update_book 두 곳에 있습니다.
제안: get_book_or_404처럼 check_duplicate_title 함수로 빼면 어떨까요.
```

받은 리뷰 중 **동의하는 것을 골라** 수정하고, 수정 후 다시 Postman으로 검증합니다.

> **참고:** 동의하지 않는 지적은 고치지 않아도 됩니다. 대신 **왜 그렇게 했는지 설명해 보세요.**
> 설명이 잘 안 되면 대개 고치는 게 맞습니다.

#### AI에게 먼저 리뷰받기 (선택)

사람에게 보여주기 전에 AI에게 1차 점검을 받으면, 사람은 더 본질적인 부분에 집중할 수 있습니다.
4일차 「바이브코딩」 절의 원칙이 그대로 적용됩니다. **범위·금지사항·기준·출력 형식** 을 명시합니다.

```
아래는 FastAPI 프로젝트의 routers/books.py입니다.

코드를 고치지 말고, 아래 7가지 관점으로만 검토해 표로 정리해 주세요.

1. 이름: 함수·변수 이름만 보고 하는 일을 알 수 있는가
2. 중복: 같은 코드가 세 번 이상 반복되는가
3. 책임: 한 함수가 한 가지 일만 하는가
4. 오류: 실패할 수 있는 지점에 처리가 있는가
5. 상태 코드: 상황에 맞는 코드를 쓰는가
6. 비밀 값: 키나 비밀번호가 코드에 직접 적혀 있는가
7. 죽은 코드: 주석 처리된 옛 버전이 남아 있는가

각 항목마다 "파일:줄 번호", "무엇이 문제인지", "어떻게 바꾸면 좋을지"를 적어 주세요.
문제가 없는 관점은 "해당 없음"으로 표시해 주세요.
없는 문제를 지어내지 마세요.
```

> **주의:** AI 리뷰는 **1차 점검** 입니다. 지적을 그대로 다 반영하지 마세요.
> 각 지적이 타당한지 직접 판단하고, 반영한 뒤에는 **반드시 Postman으로 검증** 합니다.

---

### 심화 (시간이 남을 때)

- 삭제된 도서를 실제로 지우지 않고 `deleted: true` 표시만 하는 방식(**소프트 삭제**)으로 바꾼다.
- `save_books()` 호출을 매번 쓰는 대신, 데이터가 바뀌면 자동으로 저장되게 만든다.
- `lifespan` 이벤트를 사용해 서버 시작·종료 시점에 파일을 읽고 쓰도록 바꾼다.
- `PUT`으로 없는 번호를 보내면 새로 만드는 방식(**upsert**)을 검토해 본다. 그것이 적절한지 토론한다.
- 목록 조회에 정렬과 페이지네이션을 합쳐 하나의 엔드포인트로 통합한다.
- `books_data.json`을 SQLite로 바꾸는 것이 어떤 작업인지 조사한다.

---

## 7. 전체 완성 코드

5일차까지의 최종 상태입니다. `external_api.py`는 **3일차 이후 변경이 없으므로** 생략합니다.

### 7-1. `database.py`

```python
import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "books_data.json"

DEFAULT_BOOKS = [
    {"id": 1, "title": "파이썬 입문", "author": "김철수", "year": 2021, "tags": [], "publisher": None},
    {"id": 2, "title": "FastAPI 실전", "author": "이영희", "year": 2023, "tags": [], "publisher": None},
    {"id": 3, "title": "파이썬 웹개발", "author": "김철수", "year": 2022, "tags": [], "publisher": None},
    {"id": 4, "title": "데이터 분석 기초", "author": "박민수", "year": 2020, "tags": [], "publisher": None},
    {"id": 5, "title": "FastAPI로 배우는 백엔드", "author": "이영희", "year": 2024, "tags": [], "publisher": None},
]

books: list[dict] = []


def load_books() -> None:
    """파일에서 도서 목록을 읽어 books에 채운다. 파일이 없으면 기본값을 쓴다."""
    books.clear()
    if DATA_FILE.exists():
        with open(DATA_FILE, encoding="utf-8") as f:
            books.extend(json.load(f))
    else:
        books.extend(DEFAULT_BOOKS)
        save_books()


def save_books() -> None:
    """현재 books 내용을 파일에 저장한다."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)


load_books()
```

### 7-2. `schemas.py`

```python
from pydantic import BaseModel, Field, field_validator


class Publisher(BaseModel):
    name: str = Field(description="출판사 이름", examples=["한빛미디어"])
    city: str = Field(default="서울", description="출판사 소재 도시")


class BookCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=100,
        description="도서 제목",
        examples=["처음 시작하는 FastAPI"],
    )
    author: str = Field(
        min_length=1,
        max_length=50,
        description="저자명",
        examples=["빌 루바노빅"],
    )
    year: int = Field(
        ge=1900,
        le=2100,
        description="출판 연도",
        examples=[2024],
    )
    tags: list[str] = Field(default_factory=list, description="분류 태그")
    publisher: Publisher | None = Field(default=None, description="출판사 정보")

    @field_validator("title")
    @classmethod
    def strip_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("제목은 공백일 수 없습니다")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "처음 시작하는 FastAPI",
                    "author": "빌 루바노빅",
                    "year": 2024,
                    "tags": ["python", "backend"],
                    "publisher": {"name": "한빛미디어", "city": "서울"},
                }
            ]
        }
    }


class BookUpdate(BaseModel):
    """부분 수정용. 모든 필드가 선택이며, 보낸 필드만 반영된다."""

    title: str | None = Field(default=None, min_length=1, max_length=100, description="도서 제목")
    author: str | None = Field(default=None, min_length=1, max_length=50, description="저자명")
    year: int | None = Field(default=None, ge=1900, le=2100, description="출판 연도")
    tags: list[str] | None = Field(default=None, description="분류 태그")
    publisher: Publisher | None = Field(default=None, description="출판사 정보")

    model_config = {
        "json_schema_extra": {
            "examples": [{"year": 2025}]
        }
    }


class BookResponse(BookCreate):
    id: int = Field(description="서버가 발급한 도서 번호", examples=[1])


class WeatherResponse(BaseModel):
    latitude: float = Field(description="위도", examples=[36.8])
    longitude: float = Field(description="경도", examples=[127.1])
    temperature: float = Field(description="현재 기온(섭씨)", examples=[28.9])
    time: str = Field(description="관측 시각", examples=["2026-08-04T09:00"])


class ExternalBook(BaseModel):
    title: str = Field(description="도서 제목", examples=["처음 시작하는 FastAPI"])
    authors: list[str] = Field(default_factory=list, description="저자 목록")
    published_date: str = Field(default="", description="발행일. 없을 수 있음")


class ErrorDetail(BaseModel):
    detail: str = Field(description="오류 메시지", examples=["도서를 찾을 수 없습니다"])
```

### 7-3. `main.py`

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers import books, external, system

tags_metadata = [
    {"name": "시스템", "description": "서버 상태와 앱 정보 확인"},
    {"name": "도서", "description": "내 도서 목록의 등록, 조회, 수정, 삭제"},
    {"name": "외부 연동", "description": "Google Books 도서 검색과 날씨 조회"},
]

app = FastAPI(
    title="도서 관리 API",
    description="""
도서를 등록·조회·수정·삭제하고, 외부 서비스에서 도서 정보와 날씨를 가져오는 API입니다.

FastAPI 입문 과정 실습용으로 제작되었습니다.
""",
    version="1.0.0",
    contact={"name": "작성자 이름", "email": "your@email.com"},
    openapi_tags=tags_metadata,
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# 등록 순서 주의: /books/external 이 /books/{book_id} 보다 먼저 등록돼야 한다
app.include_router(system.router)
app.include_router(external.router)
app.include_router(books.router)
```

### 7-4. `routers/system.py`, `routers/books.py`, `routers/external.py`

실습 6의 코드와 동일합니다. 위로 올라가 복사하세요.

### 7-5. 의존 방향

```
main.py  →  routers/*  →  database.py
                       →  schemas.py
                       →  external_api.py  →  schemas.py
```

모든 화살표가 **한 방향** 이고 `database.py`와 `schemas.py`는 아무것도 가져오지 않습니다.
**순환 import가 생길 수 없는 구조** 입니다.

---

## 8. 실습 확장 — 관리 화면

CRUD가 완성됐으므로 **한 화면에서 전부** 다룰 수 있습니다.

### 웹 실습 1. 수정 화면

파일: `static/20-edit.html` — 기존 값을 불러와 고친 뒤 `PATCH`로 보냅니다.

```html
<!DOCTYPE html>
<html lang="ko">
<head><meta charset="utf-8"><title>도서 수정</title></head>
<body>
  <h1>도서 수정</h1>
  <input id="bookId" type="number" placeholder="도서 번호">
  <button id="loadBtn">불러오기</button>

  <div id="form" style="display:none; margin-top:12px;">
    <input id="title" placeholder="제목"><br>
    <input id="author" placeholder="저자"><br>
    <input id="year" type="number" placeholder="연도"><br>
    <button id="saveBtn">수정</button>
  </div>

  <p id="msg"></p>

  <script>
    let currentId = null;

    document.getElementById("loadBtn").addEventListener("click", async () => {
      const id = document.getElementById("bookId").value;
      const msg = document.getElementById("msg");
      const res = await fetch("/books/" + id);

      if (res.status === 404) {
        msg.textContent = "해당 도서가 없습니다";
        document.getElementById("form").style.display = "none";
        return;
      }

      const book = await res.json();
      currentId = book.id;
      document.getElementById("title").value = book.title;
      document.getElementById("author").value = book.author;
      document.getElementById("year").value = book.year;
      document.getElementById("form").style.display = "block";
      msg.textContent = "";
    });

    document.getElementById("saveBtn").addEventListener("click", async () => {
      const payload = {
        title: document.getElementById("title").value,
        author: document.getElementById("author").value,
        year: Number(document.getElementById("year").value)
      };
      const res = await fetch("/books/" + currentId, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const msg = document.getElementById("msg");
      msg.textContent = res.ok ? "수정 완료" : "실패 (상태 " + res.status + ")";
    });
  </script>
</body>
</html>
```

> **참고:** `PATCH`를 쓴 이유는 **세 필드만 보내도 `tags`와 `publisher`가 유지되기** 때문입니다.

**확인:**

1. 번호 `1`을 넣고 `불러오기`를 누르면 입력칸에 현재 값이 채워진다.
2. 제목을 바꾸고 `수정`을 누르면 "수정 완료"가 표시된다.
3. `/docs`에서 `GET /books/1`을 실행해 `tags`가 **그대로 남아 있는지** 확인한다.
4. **`method`를 `"PUT"`으로 바꿔** 다시 실행해 본다. `tags`가 **빈 배열이 된다.** 이것이 차이다.
5. 없는 번호(`999`)를 넣으면 "해당 도서가 없습니다"가 표시된다.

---

### 웹 실습 2. 통합 관리 화면

파일: `static/21-manage.html` — 목록, 등록, 수정, 삭제를 한 페이지에서 처리합니다.

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>도서 관리</title>
  <style>
    table { border-collapse: collapse; margin-top: 12px; }
    th, td { border: 1px solid #ccc; padding: 6px 10px; }
    input { width: 120px; }
  </style>
</head>
<body>
  <h1>도서 관리</h1>

  <h2>새 도서 등록</h2>
  <input id="newTitle" placeholder="제목">
  <input id="newAuthor" placeholder="저자">
  <input id="newYear" type="number" placeholder="연도">
  <button id="addBtn">등록</button>
  <p id="msg"></p>

  <h2>목록</h2>
  <table>
    <thead>
      <tr><th>번호</th><th>제목</th><th>저자</th><th>연도</th><th>작업</th></tr>
    </thead>
    <tbody id="rows"></tbody>
  </table>

  <script>
    function showMessage(text, isError) {
      const msg = document.getElementById("msg");
      msg.textContent = text;
      msg.style.color = isError ? "red" : "green";
    }

    async function loadBooks() {
      const books = await (await fetch("/books")).json();
      const rows = document.getElementById("rows");
      rows.innerHTML = "";

      for (const b of books) {
        const tr = document.createElement("tr");
        tr.innerHTML =
          "<td>" + b.id + "</td>" +
          "<td><input value='" + b.title + "' data-field='title'></td>" +
          "<td><input value='" + b.author + "' data-field='author'></td>" +
          "<td><input type='number' value='" + b.year + "' data-field='year'></td>" +
          "<td></td>";

        const cell = tr.lastElementChild;

        const saveBtn = document.createElement("button");
        saveBtn.textContent = "저장";
        saveBtn.addEventListener("click", () => saveBook(b.id, tr));

        const delBtn = document.createElement("button");
        delBtn.textContent = "삭제";
        delBtn.addEventListener("click", () => deleteBook(b.id, b.title));

        cell.appendChild(saveBtn);
        cell.appendChild(delBtn);
        rows.appendChild(tr);
      }
    }

    async function saveBook(id, tr) {
      const payload = {};
      for (const input of tr.querySelectorAll("input")) {
        const field = input.dataset.field;
        payload[field] = field === "year" ? Number(input.value) : input.value;
      }

      const res = await fetch("/books/" + id, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        showMessage(id + "번 수정 완료", false);
      } else {
        showMessage("수정 실패 (상태 " + res.status + ")", true);
      }
    }

    async function deleteBook(id, title) {
      if (!confirm("'" + title + "'을(를) 삭제할까요?")) return;

      const res = await fetch("/books/" + id, { method: "DELETE" });
      if (res.status === 204) {
        showMessage(id + "번 삭제 완료", false);
        loadBooks();
      } else {
        showMessage("삭제 실패 (상태 " + res.status + ")", true);
      }
    }

    document.getElementById("addBtn").addEventListener("click", async () => {
      const payload = {
        title: document.getElementById("newTitle").value,
        author: document.getElementById("newAuthor").value,
        year: Number(document.getElementById("newYear").value)
      };

      const res = await fetch("/books", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (res.status === 201) {
        showMessage("등록 완료: " + data.title, false);
        loadBooks();
      } else if (res.status === 409) {
        showMessage("중복: " + data.detail, true);
      } else if (res.status === 422) {
        showMessage("입력 오류: " + data.detail.map(e => e.msg).join(" / "), true);
      } else {
        showMessage("실패 (상태 " + res.status + ")", true);
      }
    });

    loadBooks();
  </script>
</body>
</html>
```

> **참고:** 삭제 전 `confirm`으로 확인을 받는 점에 주의합니다. **되돌릴 수 없는 동작에는 확인 절차가 필요합니다.**

**확인:**

|동작|기대 결과|
|---|---|
|새 도서 등록|초록 글씨 "등록 완료" + 목록에 추가됨|
|같은 제목 재등록|빨간 글씨 "중복: 이미 등록된 제목입니다"|
|연도를 `1800`으로 등록|빨간 글씨 "입력 오류: ..." (`422`)|
|목록에서 제목 고치고 `저장`|"N번 수정 완료"|
|`삭제` 클릭|확인 창이 뜨고, 확인하면 목록에서 사라짐|
|**서버 재시작 후 새로고침**|**모든 변경이 그대로 유지됨**|

마지막 항목이 실습 5(파일 저장)가 동작한다는 증거입니다.

---

### 시작 페이지 갱신

`static/index.html`의 4일차 섹션에 오늘 만든 두 페이지를 추가합니다.

```html
  <h2>5일차. 관리 화면</h2>
  <ul>
    <li><a href="20-edit.html">도서 수정</a></li>
    <li><a href="21-manage.html">통합 관리</a></li>
  </ul>
```

### 웹 실습 심화 (시간이 남을 때)

- 3일차 외부 검색 화면과 이 관리 화면을 하나로 합친다.
- 삭제한 도서를 되돌리는 실행 취소 버튼을 만든다.
- 목록에 정렬 버튼(제목순, 연도순)을 추가한다.

---

## 9. 최종 확인 체크리스트

**CRUD 동작 (`/docs`에서 확인)**

- [ ] `POST /books`로 등록하면 `201`
- [ ] `GET /books`가 목록을 반환한다
- [ ] `GET /books/1`이 한 건을 반환한다
- [ ] `PUT /books/1`로 전체 교체하면 `200`, `tags`가 초기화된다
- [ ] `PATCH /books/1`에 `{"year": 2025}`만 보내면 다른 필드가 유지된다
- [ ] `DELETE /books/5`가 `204`이고 **본문이 비어 있다**
- [ ] 같은 번호를 다시 삭제하면 `404`
- [ ] 없는 번호로 `GET`·`PUT`·`PATCH`·`DELETE` 모두 `404`

**파일 저장**

- [ ] `books_data.json`이 자동 생성되었다
- [ ] 파일을 열면 한글이 **깨지지 않고** 보인다
- [ ] 도서를 등록하고 **서버를 껐다 켠 뒤에도** 남아 있다
- [ ] `.gitignore`에 `books_data.json`이 있다

**파일 구조**

- [ ] `main.py`가 **30줄 내외** 로 짧아졌다
- [ ] `routers/` 안에 `__init__.py`, `system.py`, `books.py`, `external.py`가 있다
- [ ] `database.py`가 아무것도 import하지 않는다
- [ ] `main.py`에서 `external.router`가 `books.router`보다 **먼저** 등록되어 있다
- [ ] `GET /books/external?keyword=fastapi`가 `422`가 아니라 `200`을 반환한다
- [ ] `/docs`에 그룹이 **3개** 이고 엔드포인트가 빠짐없이 있다

**정리**

- [ ] 코드에서 `AIza`를 검색해도 결과가 없다
- [ ] 주석 처리된 옛 코드가 없다
- [ ] VS Code `문제` 패널에 미사용 import 경고가 없다

**최종 검증**

- [ ] **Postman `Run collection`이 전부 통과한다**
- [ ] `static/19-dashboard.html`의 `전체 점검`이 전부 초록색이다
- [ ] `static/21-manage.html`에서 등록·수정·삭제가 모두 동작한다

---

## 10. 5일 정리

### 오늘 배운 것

- `PUT`은 **전체 교체**, `PATCH`는 **부분 수정** 이다. 실무에서는 대부분 `PATCH`를 쓴다.
- `PATCH`는 `model_dump(exclude_unset=True)`로 **보낸 필드만** 골라낸다. 이걸 빠뜨리면 기존 값이 `None`으로 지워진다.
- 삭제 성공은 `204`이며 **본문이 없다.** `response_model`도 지정하지 않는다.
- 같은 코드가 **세 번 반복되면 함수로 뺀다.**
- 데이터를 파일에 저장하면 서버를 껐다 켜도 유지된다. 다른 파일이 참조하는 리스트는 **재대입하지 말고 내용만 교체** 한다.
- `APIRouter`로 엔드포인트를 나누고, 데이터를 별도 파일에 두어 **순환 import를 피한다.**
- 라우터 **등록 순서** 가 경로 충돌을 결정한다. 리터럴 경로를 가진 라우터를 먼저 등록한다.

### 5일 전체

|일차|주제|만든 것|
|---|---|---|
|1|FastAPI 입문|환경 구축, GET 엔드포인트, 조회 화면|
|2|요청 데이터와 검증|Pydantic 모델, POST 등록, 오류 처리|
|3|비동기와 외부 연동|async/await, httpx, 외부 API 두 곳 연동|
|4|문서화와 테스트|OpenAPI 정리, Postman 자동 테스트|
|5|CRUD 완성과 정리|수정·삭제, 파일 저장, 라우터 분리|

시작은 `{"message": "Hello"}` 하나를 반환하는 서버였습니다.
끝은 **20개가 넘는 엔드포인트, 외부 서비스 연동, 자동 문서, 자동 테스트, 관리 화면** 을 갖춘 API입니다.

### 다음 단계

이 과정에서 다루지 않은 것들입니다. 각자의 방향에 따라 골라 학습하세요.

|주제|무엇을 배우나|
|---|---|
|**데이터베이스**|JSON 파일 대신 SQLite나 PostgreSQL. SQLAlchemy 또는 SQLModel|
|**인증**|로그인, JWT 토큰, 권한 관리|
|**배포**|내 컴퓨터가 아닌 서버에서 실행하기. Docker, 클라우드|
|**테스트 코드**|pytest로 파이썬 코드 안에서 테스트 작성|
|**프론트엔드**|React, Vue 등으로 제대로 된 화면 만들기|

---

## 11. 자주 나는 오류와 해결

### CRUD 관련

|증상 / 오류 메시지|원인|해결|
|---|---|---|
|`PATCH` 후 다른 필드가 `None`이 됨|`exclude_unset=True`를 빠뜨림|`patch.model_dump(exclude_unset=True)` 확인|
|`PATCH`가 `422`|`BookUpdate`가 아니라 `BookCreate`를 받음|파라미터 타입을 `BookUpdate`로|
|`DELETE`가 `500`|`204`인데 본문을 반환함|`return None`으로 변경, `response_model` 제거|
|`DELETE` 후에도 목록에 남음|`books.remove()`가 다른 객체를 지움|`get_book_or_404`가 반환한 객체를 그대로 넘기기|
|`PUT` 후 `id`가 사라짐|`{"id": book_id, **...}`에서 `id`를 안 넣음|새 딕셔너리에 `id` 포함 확인|

### 파일 저장 관련

|증상 / 오류 메시지|원인|해결|
|---|---|---|
|`books_data.json`이 안 생김|`load_books()` 호출이 없음|`database.py` 맨 아래 호출 확인|
|파일에 한글이 `서울`로 저장|`ensure_ascii=False` 누락|`json.dump(..., ensure_ascii=False)`|
|서버를 껐다 켜면 데이터가 사라짐|`save_books()` 호출을 빠뜨림|데이터를 바꾸는 5개 엔드포인트 전부 확인|
|`main.py`에서 등록해도 목록에 반영 안 됨|`books = [...]`로 **재대입** 함|`books.clear()` + `extend()` 방식 확인|
|`FileNotFoundError`|실행 폴더가 달라 상대 경로 실패|`Path(__file__).parent` 사용 확인|

### 라우터 분리 관련

|증상 / 오류 메시지|원인|해결|
|---|---|---|
|`ModuleNotFoundError: No module named 'routers'`|`__init__.py`가 없거나 실행 폴더가 다름|빈 `__init__.py` 생성, `cd 01-fastapi-basic` 후 실행|
|`ImportError: cannot import name 'books'`|`from routers import books`와 `from database import books` 충돌|`main.py`에서는 `routers`의 것만 import|
|`GET /books/external`이 `422`|`books.router`를 먼저 등록함|`external.router`를 **먼저** 등록|
|`GET /books`가 `404`|`@router.get("")`이 아니라 `("/")`로 씀|`prefix`가 있으면 목록 경로는 `""`|
|`/docs`에 엔드포인트가 빠짐|`include_router`를 안 함|`main.py`에서 3개 모두 등록했는지 확인|
|순환 import 오류|`routers`가 `main`을 import함|데이터는 `database.py`에서만 가져오기|
|태그가 두 번 표시됨|라우터와 엔드포인트에 태그를 둘 다 붙임|엔드포인트의 `tags=` 제거|

### 문제가 안 풀릴 때

1. **Postman `Run collection`** 을 먼저 돌려 **어느 엔드포인트가 깨졌는지** 좁힙니다.
2. 서버가 안 뜨면 터미널 traceback의 **마지막 줄** 을 봅니다. import 문제가 대부분입니다.
3. 경로 문제는 `/docs`에서 **실제 경로가 어떻게 등록됐는지** 확인합니다.
4. 그래도 안 되면 [7. 전체 완성 코드](#7-전체-완성-코드)와 본인 코드를 파일별로 비교합니다.

---

## 부록. 용어 사전 (5일차 추가분)

|용어|한 줄 정의|
|---|---|
|**CRUD**|Create·Read·Update·Delete. 데이터를 다루는 네 가지 기본 동작|
|**`PUT`**|**전체 교체.** 보내지 않은 필드는 기본값으로 덮어씀|
|**`PATCH`**|**부분 수정.** 보낸 필드만 바꾸고 나머지는 유지|
|**`DELETE`**|삭제. 성공 시 보통 `204`|
|**`204 No Content`**|성공했지만 **돌려줄 본문이 없음**|
|**멱등성 (idempotency)**|같은 요청을 여러 번 보내도 결과가 같은 성질|
|**`exclude_unset=True`**|**실제로 보낸 필드만** 딕셔너리로 만드는 옵션|
|**영속화 (persistence)**|프로그램이 꺼져도 데이터가 남아 있게 만드는 것|
|**`ensure_ascii=False`**|JSON 저장 시 **한글을 그대로** 기록하는 옵션|
|**`APIRouter`**|엔드포인트를 묶어 두었다가 앱에 한꺼번에 등록하는 도구|
|**`prefix`**|라우터의 모든 경로 앞에 붙는 공통 경로|
|**`include_router`**|라우터를 앱에 등록. **등록 순서가 경로 매칭 순서**|
|**`__init__.py`**|폴더를 파이썬 **패키지** 로 인식시키는 파일|
|**순환 import**|A가 B를, B가 A를 가져와 서로 물리는 상태|
|**`include_in_schema=False`**|동작은 유지하고 **문서에서만 숨김**|
|**리팩토링**|동작을 바꾸지 않고 **코드 구조만** 개선하는 작업|
|**소프트 삭제**|실제로 지우지 않고 `deleted: true` 표시만 하는 방식|

### 1~4일차 용어 복습

|용어|한 줄 정의|
|---|---|
|**FastAPI / Uvicorn**|웹 프레임워크 / 실제로 포트를 열고 요청을 받는 ASGI 서버|
|**`dev` / `run`**|`fastapi dev`는 개발용(자동 재시작), `fastapi run`은 운영용|
|**Pydantic / `Field`**|타입 힌트 기반 검증 라이브러리 / 제약·설명·예시를 붙이는 도구|
|**`response_model`**|응답 형태를 고정·검사하는 옵션|
|**`HTTPException`**|상태 코드와 함께 오류를 내보내는 예외. `raise`로 사용|
|**`async` / `await`**|비동기 함수 선언 / 실제로 기다리는 지점|
|**`responses`**|발생 가능한 오류를 **문서에** 표시. 동작은 바꾸지 않음|
|**리터럴 경로 우선 규칙**|`/books/search`는 `/books/{book_id}`보다 **위** 에 선언|

## 부록. 명령어 요약

|목적|명령|
|---|---|
|가상환경 활성화 (Windows PowerShell)|`.venv\Scripts\Activate.ps1`|
|**개발** 서버 실행 (반드시 `main.py` 폴더에서)|`cd 01-fastapi-basic` → `fastapi dev main.py`|
|서버 종료|`Ctrl + C`|
|`.env`·데이터 파일 변경 반영|**서버 재시작**|
|미사용 import 확인 (VS Code)|`Ctrl + Shift + M`|

## 부록. 주요 주소 요약

|주소|용도|
|---|---|
|`http://127.0.0.1:8000/docs`|Swagger UI (실행 가능)|
|`http://127.0.0.1:8000/redoc`|ReDoc (읽기 전용)|
|`http://127.0.0.1:8000/static/index.html`|실습 페이지 색인|
|`http://127.0.0.1:8000/static/21-manage.html`|통합 관리 화면|
|`http://127.0.0.1:8000/static/19-dashboard.html`|API 상태 점검|

---

**과정 완료.** 5일 동안 수고하셨습니다.

#FastAPI #Python #백엔드 #API #입문 #5일차 #배포용 #CRUD #PUT #PATCH #DELETE #204 #멱등성 #excludeunset #APIRouter #라우터분리 #영속화 #코드리뷰 #리팩토링
