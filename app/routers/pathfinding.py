from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.pathfinding import PathfindingService
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.core.config import settings

router = APIRouter(prefix="/api/pathfinding", tags=["pathfinding"])


class PixelCoordinate(BaseModel):
    """Model cho tọa độ pixel từ frontend"""
    x: float
    y: float


class PathRequest(BaseModel):
    """Model cho request tìm đường"""
    start_x: float
    start_y: float
    end_x: float
    end_y: float


class CoordinatePoint(BaseModel):
    """Model cho điểm tọa độ"""
    x: float
    y: float


class PathResponse(BaseModel):
    """Model cho response đường đi"""
    path: List[str]
    coordinates: List[CoordinatePoint]
    total_distance: float


class NodesResponse(BaseModel):
    """Model cho response danh sách nodes"""
    name: str
    x: float
    y: float


@router.get("/nodes", response_model=List[NodesResponse])
async def get_all_nodes(db: Session = Depends(get_db)):
    """
    Lấy danh sách tất cả nodes để hiển thị trên bản đồ
    """
    try:
        from app.db.models import NodeModel
        nodes = db.query(NodeModel).all()

        # Chuyển tọa độ y nếu DB dùng origin bottom-left -> đưa về top-left (để thống nhất với map)
        map_h = getattr(settings, "MAP_HEIGHT", None)
        origin = getattr(settings, "MAP_ORIGIN", "top-left")

        result = []
        for node in nodes:
            y = node.y
            if map_h and origin == "bottom-left":
                y = map_h - node.y
            result.append({"name": node.name, "x": node.x, "y": y})

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/find-nearest-node", response_model=Optional[str])
async def find_nearest_node(
    coord: PixelCoordinate,
    db: Session = Depends(get_db)
):
    """
    Tìm node gần nhất với tọa độ pixel được click
    
    Args:
        coord: tọa độ pixel {x, y}
    
    Returns:
        Tên node gần nhất hoặc None nếu không tìm thấy
    """
    try:
        pathfinding = PathfindingService(db)
        nearest = pathfinding.find_nearest_node(coord.x, coord.y, max_distance=150)
        return nearest
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/find-path", response_model=Optional[PathResponse])
async def find_path(
    request: PathRequest,
    db: Session = Depends(get_db)
):
    """
    Tìm đường đi từ 2 điểm được click trên bản đồ
    
    Args:
        request: {start_x, start_y, end_x, end_y} (tọa độ pixel)
    
    Returns:
        {
            'path': ['node1', 'node2', ...],
            'coordinates': [[x1, y1], [x2, y2], ...],
            'total_distance': float
        }
    """
    try:
        pathfinding = PathfindingService(db)
        
        # Tìm 2 node gần nhất
        start_node = pathfinding.find_nearest_node(request.start_x, request.start_y)
        end_node = pathfinding.find_nearest_node(request.end_x, request.end_y)
        
        if not start_node or not end_node:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy node gần vị trí được click"
            )
        
        # Tìm đường đi
        result = pathfinding.get_path_with_coordinates(start_node, end_node)
        
        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy đường đi từ {start_node} đến {end_node}"
            )
        
        return PathResponse(
            path=result['path'],
            coordinates=[CoordinatePoint(x=coord[0], y=coord[1]) for coord in result['coordinates']],
            total_distance=result['total_distance']
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))