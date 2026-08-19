from pydantic import BaseModel, Field

class Publisher(BaseModel):
    name: str = Field(
                min_length=1,
                max_length=100,
                description="출판사 이름",
                examples=["플레이 출판사"],
    )
    city : str = Field(default="고양",
                       description="출판사 소재지",
                       examples=["고양"])
    
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
    tags: list[str] = Field(default_factory=list, description="도서 태그 목록",
                            examples =['python','web'])
    publisher: Publisher | None = Field(default=None, description="출판사 정보")
    
    def strip_title(cls, v: str) -> str:
        v = v.strip()
        # 공백문자열 체크
        if not v :
            raise ValueError("제목은 필수입력입니다.(공백안됨)") 
        return v

class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    author: str | None = Field(default=None, min_length=1, max_length=50)
    year: int | None = Field(default=None, ge=1900, le=2026, description="출판 연도", examples=[2024])
    tags :list[str] | None = Field(default=None, description="도서 태그 목록", examples=["python","web"])
    publisher: Publisher | None = Field(default=None, description="출판사 정보")


class BookResponse(BookCreate):
    id: int

class WeatherResponse(BaseModel):
    latitude: float = Field(
        ge=-90,
        le=90,
        description="위도",
        examples=[37.5665],
    )
    longitude: float = Field(
        ge=-180,
        le=180,
        description="경도",
        examples=[126.9780],
    )
    temperature: float = Field(
        description="현재 기온(섭씨)",
        examples=[25.3],
    )
    time: str = Field(
        min_length=1,
        description="날씨 데이터 측정 시간",
        examples=["2026-08-18T14:00"],
    )

class GoogleBooks(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Google Books 도서 제목",
        examples=["FastAPI"],
    )
    authors: list[str] = Field(
        default_factory=list,
        description="Google Books 도서 저자 목록",
        examples=["Bill Lubanovic"],
    )
    published_date: str = Field(
        default="",
        description="Google Books 도서 출판일",
        examples=["2024-01-01"],
    )


class ExternalBook(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
        description="외부 API 도서 제목",
        examples=["FastAPI"],
    )
    authors: list[str] = Field(
        default_factory=list,
        description="외부 API 도서 저자 목록",
        examples=["Bill Lubanovic"],
    )
    published_date: str = Field(
        default="",
        description="외부 API 도서 출판일",
        examples=["2024-01-01"],
    )