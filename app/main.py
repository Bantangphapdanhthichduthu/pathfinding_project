from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import pathfinding
from app.core.config import settings
from app.db.database import engine, SessionLocal
from app.services.pathfinding import PathfindingService
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

# Tạo 1 instance PathfindingService dùng chung (load nodes/edges 1 lần)
# sử dụng SessionLocal để khởi tạo session riêng cho service này
try:
    _pf_db = SessionLocal()
    app.state.pathfinder = PathfindingService(_pf_db)
except Exception:
    app.state.pathfinder = None

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