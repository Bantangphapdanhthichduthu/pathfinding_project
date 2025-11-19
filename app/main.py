from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import pathfinding
from app.core.config import settings
from app.db.database import engine
from app.db.models import Base

# Tạo database tables
Base.metadata.create_all(bind=engine)

# Khởi tạo FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

# Thêm CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(pathfinding.router)

# Mount static files so frontend is available at /static/aaa.html
# Nếu chạy từ thư mục project root, dùng directory="app"
# Hoặc dùng đường dẫn tuyệt đối nếu cần
app.mount("/static", StaticFiles(directory="app"), name="static")


@app.get("/")
async def root():
    return {"message": "Pathfinding API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)